"""Batch generate Manim animations for all animation blocks in the database.

For each animation block:
1. Read lesson context + animation title from DB
2. Call LLM to generate an AnimationTimeline JSON description
3. Render via Manim → TTS → ffmpeg pipeline
4. Update the DB animation block URL with the generated MP4 path

Usage:
    cd backend && python -m scripts.batch_generate_animations
    cd backend && python -m scripts.batch_generate_animations --dry-run   # LLM only, no rendering
    cd backend && python -m scripts.batch_generate_animations --lesson-code A1  # specific lesson
    cd backend && python -m scripts.batch_generate_animations --skip-existing   # skip if URL != placeholder
"""
import argparse
import asyncio
import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select, text
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import settings, LLM_PROVIDER_PROFILES
from app.db.session import async_session_factory
from app.models.course import Lesson
from app.agents.llm import is_llm_available
from app.schemas.animation import AnimationTimeline
from app.services.animation_service import render_animation_pipeline

logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BACKEND_DIR / "static" / "animations"

# Reference sample for LLM prompt
SAMPLE_JSON = json.loads(
    (BACKEND_DIR / "scripts" / "samples" / "pythagorean_area_proof.json").read_text(encoding="utf-8")
)

SYSTEM_PROMPT = """你是一个数学动画设计师。你严格按照 AnimationTimeline JSON schema 输出 Manim CE 动画描述。

可用元素类型 (elements[].type):
- coordinate_system: 坐标系 (config: x_range, y_range, x_label, y_label, show_grid)
- function_plot: 函数图像 (config: expression="lambda x: x**2", color, stroke_width, label, x_range) — expression 必须是合法 Python lambda
- geometric_shape: 几何图形 (config: shape_type=circle|rectangle|triangle|polygon|regular_polygon, vertices, radius, width, height, center, stroke_color, fill_color, fill_opacity, stroke_width)
- text_label: 文本/数学标签 (config: text, font_size, color, position) — text 中用 $..$ 包裹 LaTeX，CJK 文字不加 $
- point: 点 (config: position, radius, color) — 仅在坐标系内使用
- line_segment: 线段 (config: start, end, color, stroke_width) — 仅在坐标系内使用
- arrow: 箭头 (config: start, end, color, stroke_width, buff) — 仅在坐标系内使用
- equation_step: 方程步骤 (config: expressions=["LaTeX1", "LaTeX2", ...], font_size, color, position)

可用动作类型 (steps[].action):
- create: 创建/显示元素
- write: 写入文本/公式
- transform / replace: 变换 (需 params.source_element_id)
- move: 移动 (params.shift 或 params.to_position)
- highlight: 高亮 (params.color)
- fade: 淡出
- indicate: 指示 (params.indicate_type="flash"|"circumscribe")

规则:
1. 动画总时长 15-30 秒，每个 step 的 duration 建议 1-3 秒
2. 坐标使用 Manim 坐标系 (frame_height=8, 原点在画面中心)
3. 几何动画不用坐标系时，position 用 Manim 坐标 [x, y, 0]
4. 涉及函数图像必须先定义 coordinate_system 元素
5. point/line_segment/arrow 只能在坐标系内使用
6. 颜色用 hex 格式 "#RRGGBB"
7. narration 用中文，面向中小学生，通俗易懂
8. elements 和 steps 中的 id/target_element_id 必须一一对应

只输出 JSON，不要任何解释文字。"""

USER_PROMPT_TEMPLATE = """参考示例（勾股定理面积证明）:
{sample_json}

---

请为以下课程生成动画:

课程: {course_title}
课节: {lesson_title} ({lesson_code})
主题: {step_title}
动画标题: {anim_title}
{extra_context}

输出 AnimationTimeline JSON:"""


def _build_llm():
    profile = LLM_PROVIDER_PROFILES.get(settings.LLM_PROVIDER, {})
    client_type = profile.get("client", "openai")

    llm_kwargs = {
        "model": settings.STRONG_MODEL,
        "api_key": settings.OPENAI_API_KEY,
        "temperature": 0.7,
        "max_tokens": 8192,
        "timeout": 120.0,
        "max_retries": 2,
    }
    if settings.LLM_BASE_URL:
        llm_kwargs["base_url"] = settings.LLM_BASE_URL

    if client_type == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(**llm_kwargs)
    else:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(**llm_kwargs)


async def get_animation_blocks(session) -> list[dict]:
    """Extract all animation blocks from lessons in DB."""
    result = await session.execute(
        text("""
            SELECT l.id as lesson_id, l.title as lesson_title, l.code as lesson_code,
                   l.content, c.name as course_name, c.subject
            FROM lessons l
            JOIN units u ON l.unit_id = u.id
            JOIN courses c ON u.course_id = c.id
            WHERE l.content IS NOT NULL
        """)
    )
    rows = result.fetchall()

    animations = []
    for row in rows:
        lesson_id, lesson_title, lesson_code, content_str, course_name, subject = row
        try:
            content = json.loads(content_str)
        except (json.JSONDecodeError, TypeError):
            continue

        steps = content.get("steps", [])
        for step_idx, step in enumerate(steps):
            phase = step.get("phase", step.get("id", "?"))
            step_title = step.get("title", "")
            blocks = step.get("blocks", [])
            for block_idx, block in enumerate(blocks):
                if block.get("type") == "animation":
                    animations.append({
                        "lesson_id": lesson_id,
                        "lesson_title": lesson_title,
                        "lesson_code": lesson_code,
                        "course_name": course_name,
                        "subject": subject,
                        "phase": phase,
                        "step_title": step_title,
                        "step_idx": step_idx,
                        "block_idx": block_idx,
                        "anim_title": block.get("title", ""),
                        "anim_url": block.get("url", ""),
                        "anim_type": block.get("animation_type", "manim"),
                        "duration_sec": block.get("duration_sec", 25),
                        "agent_instruction": block.get("agent_instruction", ""),
                        "description": block.get("description", ""),
                    })
    return animations


async def generate_timeline_with_llm(llm, anim_info: dict) -> dict | None:
    extra_parts = []
    if anim_info["agent_instruction"]:
        extra_parts.append(f"额外说明: {anim_info['agent_instruction']}")
    if anim_info["description"]:
        extra_parts.append(f"动画描述: {anim_info['description']}")
    extra_context = "\n".join(extra_parts) if extra_parts else ""

    user_msg = USER_PROMPT_TEMPLATE.format(
        sample_json=json.dumps(SAMPLE_JSON, ensure_ascii=False, indent=2),
        course_title=anim_info["course_name"],
        lesson_title=anim_info["lesson_title"],
        lesson_code=anim_info["lesson_code"],
        step_title=anim_info["step_title"],
        anim_title=anim_info["anim_title"],
        extra_context=extra_context,
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_msg),
    ]

    response = await llm.ainvoke(messages)
    raw = response.content.strip()

    if raw.startswith("```"):
        lines = raw.split("\n")
        start = 1
        end = len(lines)
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() == "```":
                end = i
                break
        raw = "\n".join(lines[start:end])

    # Try to find JSON object in the output
    json_start = raw.find("{")
    json_end = raw.rfind("}") + 1
    if json_start >= 0 and json_end > json_start:
        raw = raw[json_start:json_end]

    try:
        timeline_dict = json.loads(raw)
        AnimationTimeline.model_validate(timeline_dict)
        return timeline_dict
    except (json.JSONDecodeError, Exception) as e:
        logger.error("LLM output parse error for %s: %s", anim_info["anim_title"], e)
        logger.debug("Raw LLM output (first 800 chars):\n%s", raw[:800])
        return None


async def update_db_url(session, lesson_id: str, step_idx: int, block_idx: int, new_url: str):
    result = await session.execute(
        text("SELECT content FROM lessons WHERE id = :lid"),
        {"lid": lesson_id},
    )
    row = result.fetchone()
    if not row:
        logger.error("Lesson %s not found", lesson_id)
        return

    content = json.loads(row[0]) if isinstance(row[0], str) else dict(row[0])
    content["steps"][step_idx]["blocks"][block_idx]["url"] = new_url
    new_content = json.dumps(content, ensure_ascii=False)

    await session.execute(
        text("UPDATE lessons SET content = :content, updated_at = CURRENT_TIMESTAMP WHERE id = :lid"),
        {"content": new_content, "lid": lesson_id},
    )
    await session.commit()


async def process_one(llm, anim_info: dict, dry_run: bool = False) -> dict:
    """Process a single animation: LLM → render → DB update."""
    start = time.time()
    result = {
        "lesson_code": anim_info["lesson_code"],
        "title": anim_info["anim_title"],
        "status": "pending",
        "url": None,
        "error": None,
        "duration_sec": 0,
    }

    logger.info("Processing: [%s] %s", anim_info["lesson_code"], anim_info["anim_title"])

    # Step 1: Generate timeline with LLM
    timeline_dict = await generate_timeline_with_llm(llm, anim_info)
    if timeline_dict is None:
        result["status"] = "llm_failed"
        result["error"] = "Failed to generate timeline JSON"
        return result

    result["timeline"] = timeline_dict

    if dry_run:
        result["status"] = "dry_run"
        return result

    max_render_attempts = 5
    for attempt in range(max_render_attempts):
        try:
            timeline = AnimationTimeline.model_validate(timeline_dict)
            render_result = await render_animation_pipeline(
                description=timeline,
                output_dir=OUTPUT_DIR,
                skip_video=False,
                skip_audio=False,
            )

            if render_result.error:
                if attempt < max_render_attempts - 1:
                    logger.warning("  Render attempt %d failed, regenerating with LLM...", attempt + 1)
                    timeline_dict = await generate_timeline_with_llm(llm, anim_info)
                    if timeline_dict is None:
                        break
                    continue
                result["status"] = "render_error"
                result["error"] = render_result.error[:500]
                return result

            mp4_path = render_result.merged_path or render_result.video_path
            if not mp4_path:
                if attempt < max_render_attempts - 1:
                    logger.warning("  No output on attempt %d, regenerating...", attempt + 1)
                    timeline_dict = await generate_timeline_with_llm(llm, anim_info)
                    if timeline_dict is None:
                        break
                    continue
                result["status"] = "no_output"
                result["error"] = "No video file produced"
                return result

            async with async_session_factory() as db_session:
                await update_db_url(db_session, anim_info["lesson_id"], anim_info["step_idx"], anim_info["block_idx"],
                                    f"/static/animations/{Path(mp4_path).name}")

            result["status"] = "success"
            result["url"] = f"/static/animations/{Path(mp4_path).name}"
            result["duration_sec"] = round(time.time() - start, 1)
            logger.info("  ✓ Done in %.1fs (attempt %d): %s → %s", result["duration_sec"], attempt + 1, anim_info["anim_title"], result["url"])
            return result

        except Exception as e:
            if attempt < max_render_attempts - 1:
                logger.warning("  Exception on attempt %d: %s, regenerating...", attempt + 1, str(e)[:200])
                timeline_dict = await generate_timeline_with_llm(llm, anim_info)
                if timeline_dict is None:
                    break
                continue
            result["status"] = "exception"
            result["error"] = str(e)[:500]
            logger.error("  ✗ All %d attempts failed: %s — %s", max_render_attempts, anim_info["anim_title"], str(e)[:200])

    return result


async def main():
    parser = argparse.ArgumentParser(description="Batch generate animations for all lessons")
    parser.add_argument("--dry-run", action="store_true", help="Only generate LLM descriptions, no rendering")
    parser.add_argument("--lesson-code", help="Only process a specific lesson code (e.g. A1, B3)")
    parser.add_argument("--skip-existing", action="store_true", help="Skip animations that already have non-placeholder URLs")
    parser.add_argument("--limit", type=int, help="Max number of animations to process")
    parser.add_argument("--save-json-only", action="store_true", help="Save timeline JSONs without rendering")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    if not is_llm_available():
        logger.error("LLM not available. Set OPENAI_API_KEY in .env")
        sys.exit(1)

    llm = _build_llm()

    async with async_session_factory() as session:
        animations = await get_animation_blocks(session)

    logger.info("Found %d animation blocks in DB", len(animations))

    # Filter
    if args.lesson_code:
        animations = [a for a in animations if a["lesson_code"] == args.lesson_code]
        logger.info("Filtered to lesson code %s: %d blocks", args.lesson_code, len(animations))

    if args.skip_existing:
        before = len(animations)
        animations = [a for a in animations if a["anim_url"] in ("", "placeholder")]
        logger.info("Skipped %d with existing URLs, %d remaining", before - len(animations), len(animations))

    if args.limit:
        animations = animations[:args.limit]

    logger.info("Will process %d animations", len(animations))

    # Process sequentially (Manim is GPU-heavy, parallel would OOM)
    results = []
    success = 0
    failed = 0

    for i, anim in enumerate(animations, 1):
        logger.info("[%d/%d] %s — %s", i, len(animations), anim["lesson_code"], anim["anim_title"])

        if args.save_json_only:
            timeline_dict = await generate_timeline_with_llm(llm, anim)
            if timeline_dict:
                slug = f"{anim['lesson_code']}_{anim['phase']}"
                json_path = OUTPUT_DIR / f"{slug}_timeline.json"
                OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
                json_path.write_text(json.dumps(timeline_dict, ensure_ascii=False, indent=2), encoding="utf-8")
                results.append({"lesson_code": anim["lesson_code"], "title": anim["anim_title"], "status": "saved_json"})
                success += 1
            else:
                results.append({"lesson_code": anim["lesson_code"], "title": anim["anim_title"], "status": "llm_failed"})
                failed += 1
            continue

        async with async_session_factory() as session:
            r = await process_one(llm, anim, dry_run=args.dry_run)
        results.append(r)
        if r["status"] == "success":
            success += 1
        else:
            failed += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"BATCH COMPLETE: {success} success, {failed} failed, {len(results)} total")
    print("=" * 60)

    if args.dry_run or args.save_json_only:
        for r in results:
            status_icon = "✓" if "success" in r.get("status", "") or r.get("status") == "saved_json" else "✗"
            print(f"  {status_icon} [{r.get('lesson_code','?')}] {r.get('title','?')} — {r.get('status','?')}")
    else:
        for r in results:
            status_icon = "✓" if r["status"] == "success" else "✗"
            url = r.get("url", r.get("error", "?"))
            print(f"  {status_icon} [{r['lesson_code']}] {r['title']} → {url} ({r['duration_sec']}s)")

    # Save results log
    log_path = BACKEND_DIR / "scripts" / "batch_animation_results.json"
    log_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Results saved to %s", log_path)


if __name__ == "__main__":
    asyncio.run(main())
