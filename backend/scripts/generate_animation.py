"""生成 Manim 动画视频。

Usage:
    cd backend && python -m scripts.generate_animation --input animation_desc.json --output-dir static/animations/
    cd backend && python -m scripts.generate_animation --sample
"""
import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.schemas.animation import AnimationTimeline
from app.services.animation_service import generate_manim_script, render_animation_pipeline

logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parent.parent
SAMPLE_DIR = Path(__file__).resolve().parent / "samples"


def _get_sample_quadratic() -> dict:
    sample_path = SAMPLE_DIR / "quadratic_transform.json"
    if sample_path.exists():
        return json.loads(sample_path.read_text(encoding="utf-8"))
    logger.error("示例文件不存在: %s", sample_path)
    sys.exit(1)


def _check_dependencies(skip_video: bool, skip_audio: bool) -> None:
    if not skip_video:
        try:
            import manim  # noqa: F401
        except ImportError:
            logger.error("manim 未安装。请运行: pip install manim>=0.18.0")
            sys.exit(1)

    if not skip_audio:
        try:
            import edge_tts  # noqa: F401
        except ImportError:
            logger.error("edge-tts 未安装。请运行: pip install edge-tts")
            sys.exit(1)


async def main() -> None:
    parser = argparse.ArgumentParser(description="生成 Manim 动画视频")
    parser.add_argument("--input", help="动画描述 JSON 文件路径")
    parser.add_argument("--sample", action="store_true", help="生成内置示例动画（二次函数变换）")
    parser.add_argument("--output-dir", default="static/animations", help="输出目录（默认: static/animations/）")
    parser.add_argument("--skip-video", action="store_true", help="仅生成 Manim 脚本，不渲染视频")
    parser.add_argument("--skip-audio", action="store_true", help="跳过 TTS 音频生成")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    if not args.input and not args.sample:
        parser.error("请指定 --input 或 --sample")

    _check_dependencies(args.skip_video, args.skip_audio)

    if args.sample:
        desc_dict = _get_sample_quadratic()
        logger.info("使用内置示例: %s", desc_dict.get("title", "unknown"))
    else:
        input_path = Path(args.input)
        if not input_path.exists():
            logger.error("输入文件不存在: %s", input_path)
            sys.exit(1)
        desc_dict = json.loads(input_path.read_text(encoding="utf-8"))

    description = AnimationTimeline.model_validate(desc_dict)
    output_dir = BACKEND_DIR / args.output_dir

    if args.skip_video:
        script, scene_name = generate_manim_script(description)
        output_dir.mkdir(parents=True, exist_ok=True)
        script_path = output_dir / f"{scene_name}.py"
        script_path.write_text(script, encoding="utf-8")
        logger.info("Manim 脚本已生成: %s", script_path)
        return

    result = await render_animation_pipeline(
        description=description,
        output_dir=output_dir,
        skip_video=args.skip_video,
        skip_audio=args.skip_audio,
    )

    if result.error:
        logger.error("渲染出错: %s", result.error)
        sys.exit(1)

    logger.info("=" * 50)
    logger.info("渲染完成:")
    if result.script_path:
        logger.info("  脚本: %s", result.script_path)
    if result.video_path:
        logger.info("  视频: %s", result.video_path)
    if result.audio_path:
        logger.info("  音频: %s", result.audio_path)
    if result.merged_path:
        logger.info("  合成: %s", result.merged_path)


if __name__ == "__main__":
    asyncio.run(main())
