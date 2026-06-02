"""Generate TTS audio for lesson text blocks using Edge TTS.

Usage:
    cd backend && python -m scripts.generate_tts_audio --dry-run
    cd backend && python -m scripts.generate_tts_audio --lesson-code AMC-GEO-B3
    cd backend && python -m scripts.generate_tts_audio --subject amc_math --limit 5
"""
import argparse
import asyncio
import logging
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import async_session_factory, engine
from app.models.course import Course, Lesson, Unit

logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parent.parent
STATIC_AUDIO_DIR = BACKEND_DIR / "static" / "audio"

VOICE_MAP = {
    "amc_math": "zh-CN-YunxiNeural",
    "ket_english": "en-US-AriaNeural",
    "chn_composition": "zh-CN-XiaoxiaoNeural",
    "chn_poetry": "zh-CN-XiaoxiaoNeural",
}

SKIP_BLOCK_TYPES = {"formula", "audio", "image", "video", "geogebra", "divider", "code"}
MIN_TEXT_LENGTH = 20


def _get_subject_for_lesson(lesson: Lesson) -> str:
    unit = lesson.unit
    if unit and unit.course:
        return unit.course.subject
    content = lesson.content or {}
    return content.get("subject", "amc_math")


def _strip_markdown(text: str) -> str:
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"`{1,3}[^`]*`{1,3}", "", text)
    text = re.sub(r"#{1,6}\s+", "", text)
    text = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)
    text = re.sub(r"~~([^~]+)~~", r"\1", text)
    text = re.sub(r"\$\$.*?\$\$", "", text, flags=re.DOTALL)
    text = re.sub(r"\$[^$]+\$", "", text)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{2,}", ". ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _collect_text_blocks(content: dict) -> list[tuple[str, int, dict]]:
    blocks_info = []
    for step in content.get("steps", []):
        step_id = step.get("id", step.get("phase", "unknown"))
        for idx, block in enumerate(step.get("blocks", [])):
            if not isinstance(block, dict):
                continue
            block_type = block.get("type", "")
            if block_type != "text":
                continue
            raw = block.get("content", "")
            if not raw or len(raw.strip()) < MIN_TEXT_LENGTH:
                continue
            if block.get("audio_url"):
                continue
            blocks_info.append((step_id, idx, block))
    return blocks_info


async def _generate_audio(text: str, voice: str, output_path: Path) -> bool:
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(output_path))
        return True
    except Exception as e:
        logger.error("Edge TTS failed for '%s...': %s", text[:50], e)
        return False


async def _generate_narration(
    parts: list[str], voice: str, output_path: Path, dry_run: bool
) -> bool:
    if not parts:
        return False
    full_text = "... ".join(parts)
    if len(full_text.strip()) < MIN_TEXT_LENGTH:
        return False
    if dry_run:
        logger.info("[DRY RUN] Would generate narration: %s (%d chars)", output_path.name, len(full_text))
        return True
    return await _generate_audio(full_text, voice, output_path)


async def process_lesson(
    lesson: Lesson, voice: str, dry_run: bool, force: bool
) -> tuple[int, int]:
    content = lesson.content
    if not content or not isinstance(content, dict):
        logger.warning("Lesson %s has no content", lesson.code)
        return 0, 0

    lesson_code = lesson.code or f"lesson_{lesson.id}"
    audio_dir = STATIC_AUDIO_DIR / lesson_code
    blocks = _collect_text_blocks(content) if not force else []

    if force:
        blocks = []
        for step in content.get("steps", []):
            step_id = step.get("id", step.get("phase", "unknown"))
            for idx, block in enumerate(step.get("blocks", [])):
                if not isinstance(block, dict):
                    continue
                if block.get("type") != "text":
                    continue
                raw = block.get("content", "")
                if not raw or len(raw.strip()) < MIN_TEXT_LENGTH:
                    continue
                blocks.append((step_id, idx, block))

    if not blocks:
        logger.info("Lesson %s: no text blocks to process", lesson_code)
        return 0, 0

    logger.info(
        "[%s] Generating audio for lesson %s (%d blocks)...",
        lesson_code, lesson.title, len(blocks),
    )

    if not dry_run:
        audio_dir.mkdir(parents=True, exist_ok=True)

    generated = 0
    failed = 0
    narration_parts = []

    for step_id, block_idx, block in blocks:
        raw_text = block.get("content", "")
        clean_text = _strip_markdown(raw_text)
        if len(clean_text) < MIN_TEXT_LENGTH:
            continue

        filename = f"{step_id}_{block_idx}.mp3"
        audio_url = f"/static/audio/{lesson_code}/{filename}"
        output_path = audio_dir / filename

        narration_parts.append(clean_text)

        if dry_run:
            logger.info(
                "[DRY RUN] Would generate: %s (%d chars)", audio_url, len(clean_text)
            )
            block["audio_url"] = audio_url
            generated += 1
            continue

        success = await _generate_audio(clean_text, voice, output_path)
        if success:
            block["audio_url"] = audio_url
            generated += 1
        else:
            failed += 1

    narration_path = audio_dir / "full_narration.mp3"
    narration_ok = await _generate_narration(
        narration_parts, voice, narration_path, dry_run
    )
    if narration_ok:
        content["full_audio_url"] = f"/static/audio/{lesson_code}/full_narration.mp3"

    return generated, failed


async def main():
    parser = argparse.ArgumentParser(description="Generate TTS audio for lesson content")
    parser.add_argument("--lesson-code", help="Process single lesson by code")
    parser.add_argument("--subject", help="Filter by subject (amc_math, ket_english, chn_composition, chn_poetry)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without generating audio or updating DB")
    parser.add_argument("--limit", type=int, help="Max lessons to process")
    parser.add_argument("--voice", help="Override voice name (e.g. zh-CN-YunxiNeural)")
    parser.add_argument("--force", action="store_true", help="Regenerate audio even if audio_url exists")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    try:
        import edge_tts  # noqa: F401
    except ImportError:
        logger.error("edge-tts not installed. Run: pip install edge-tts")
        sys.exit(1)

    async with async_session_factory() as session:
        query = select(Lesson).options(
            selectinload(Lesson.unit).selectinload(Unit.course)
        ).order_by(Lesson.sort_order)

        if args.subject:
            query = query.join(Lesson.unit).join(Unit.course).where(
                Course.subject == args.subject
            )

        if args.lesson_code:
            query = query.where(Lesson.code == args.lesson_code)

        result = await session.execute(query)
        lessons = result.scalars().all()

    if not lessons:
        logger.info("No lessons found matching criteria")
        return

    to_process = [lesson for lesson in lessons if lesson.content and isinstance(lesson.content, dict)]
    skipped_empty = len(lessons) - len(to_process)

    if skipped_empty:
        logger.info("Skipped %d lessons with no content", skipped_empty)

    if not to_process:
        logger.info("No lessons with content to process")
        return

    if args.limit:
        to_process = to_process[:args.limit]

    logger.info("Will process %d lessons", len(to_process))

    total_generated = 0
    total_failed = 0
    total_skipped = 0
    total_narrations = 0

    for i, lesson in enumerate(to_process, 1):
        subject = _get_subject_for_lesson(lesson)
        voice = args.voice or VOICE_MAP.get(subject, "zh-CN-YunxiNeural")
        lesson_code = lesson.code or f"lesson_{lesson.id}"

        logger.info("[%d/%d] Processing lesson %s (%s) voice=%s",
                    i, len(to_process), lesson_code, lesson.title, voice)

        generated, failed = await process_lesson(lesson, voice, args.dry_run, args.force)

        if generated == 0 and failed == 0:
            total_skipped += 1
        else:
            total_generated += generated
            total_failed += failed
            if lesson.content.get("full_audio_url"):
                total_narrations += 1

        if not args.dry_run and (generated > 0 or lesson.content.get("full_audio_url")):
            async with async_session_factory() as session:
                result = await session.execute(
                    select(Lesson).where(Lesson.id == lesson.id)
                )
                db_lesson = result.scalar_one_or_none()
                if db_lesson:
                    db_lesson.content = lesson.content
                    await session.commit()
                    logger.info("Updated lesson %s in DB", lesson_code)
                else:
                    logger.error("Lesson %s not found in DB during update", lesson_code)
                    total_failed += generated
                    total_generated -= generated

    logger.info("=" * 50)
    logger.info(
        "Summary: %d audio files generated, %d narrations, %d failed, %d lessons skipped",
        total_generated, total_narrations, total_failed, total_skipped,
    )

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
