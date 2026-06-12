"""Manim CE 动画渲染管线服务。

将 AnimationTimeline 描述转换为可执行的 Manim 脚本，
然后通过 subprocess 调用 Manim 渲染 MP4，配合 Edge TTS 和 ffmpeg 合成最终视频。
"""
from __future__ import annotations

import asyncio
import logging
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any

from app.schemas.animation import (
    AnimationElement,
    AnimationResult,
    AnimationTimeline,
)

logger = logging.getLogger(__name__)

# 模块级缓存: manim 是否可用
_MANIM_AVAILABLE: bool | None = None
_MANIM_WARNING_LOGGED: bool = False


def check_manim_available() -> bool:
    """检测 manim 渲染器是否安装在系统 PATH 中。

    结果会被缓存,不会重复调用 shutil.which。
    """
    global _MANIM_AVAILABLE
    if _MANIM_AVAILABLE is None:
        _MANIM_AVAILABLE = shutil.which("manim") is not None
        if not _MANIM_AVAILABLE and not _MANIM_WARNING_LOGGED:
            logger.warning(
                "manim 未安装在系统 PATH 中,动画渲染将降级为静态文本说明. "
                "如需启用视频渲染,请安装 manim: pip install manim"
            )
            _MANIM_WARNING_LOGGED = True
    return _MANIM_AVAILABLE


def _python_color(hex_color: str) -> str:
    """将 hex 颜色转为 Manim 颜色字符串。Manim 接受 '#RRGGBB' 格式。"""
    return f'"{hex_color}"'


def _vec3(lst: list[float]) -> str:
    match len(lst):
        case 2:
            return f"[{lst[0]}, {lst[1]}, 0]"
        case 3:
            return f"[{lst[0]}, {lst[1]}, {lst[2]}]"
        case _:
            return f"[{lst[0]}, {lst[1]}, 0]"


def _build_coordinate_system(elem_id: str, cfg: dict[str, Any], width: int, height: int) -> str:
    xr = cfg.get("x_range", [-7, 7, 1])
    yr = cfg.get("y_range", [-4, 4, 1])
    xl = cfg.get("x_label", "x")
    yl = cfg.get("y_label", "y")
    sg = cfg.get("show_grid", True)
    # Manim uses its own coordinate system (frame_height=8 units by default).
    # Convert pixel dimensions to Manim units: scale so axes fill ~70% of frame.
    frame_height = 8.0
    frame_width = frame_height * width / height
    x_len = frame_width * 0.75
    y_len = frame_height * 0.75

    lines = [
        f"        {elem_id} = Axes(",
        f"            x_range={xr},",
        f"            y_range={yr},",
        f"            x_length={x_len},",
        f"            y_length={y_len},",
        "            axis_config={'include_numbers': True},",
        "            tips=False,",
        "        )",
        f"        {elem_id}_labels = {elem_id}.get_axis_labels(x_label='{xl}', y_label='{yl}')",
    ]
    if sg:
        lines.append(f"        {elem_id}_grid = NumberPlane(")
        lines.append(f"            x_range={xr}, y_range={yr},")
        lines.append(f"            x_length={x_len},")
        lines.append(f"            y_length={y_len},")
        lines.append("            background_line_style={'stroke_opacity': 0.3},")
        lines.append("        )")
    return "\n".join(lines)


def _build_function_plot(elem_id: str, cfg: dict[str, Any]) -> str:
    expr = cfg.get("expression", "lambda x: x")
    color = cfg.get("color", "#58C4DD")
    sw = cfg.get("stroke_width", 3.0)
    label = cfg.get("label")
    x_range = cfg.get("x_range")

    lines = [
        f"        {elem_id} = axes.plot(",
        f"            {expr},",
        f"            color={_python_color(color)},",
        f"            stroke_width={sw},",
    ]
    if x_range:
        lines.append(f"            x_range={x_range},")
    lines.append("        )")
    if label:
        lines.append(f"        {elem_id}_label = axes.get_graph_label(")
        lines.append(f"            {elem_id}, r'{label}',")
        lines.append("            x_val=axes.x_range[1] * 0.7, direction=UR")
        lines.append("        )")
    return "\n".join(lines)


def _build_geometric_shape(elem_id: str, cfg: dict[str, Any]) -> str:
    shape_type = cfg.get("shape_type", "circle")
    stroke_color = _python_color(cfg.get("stroke_color", "#FFFFFF"))
    stroke_w = cfg.get("stroke_width", 2.0)
    fill_color = _python_color(cfg.get("fill_color", "#000000"))
    fill_op = cfg.get("fill_opacity", 0.0)

    match shape_type:
        case "circle":
            radius = cfg.get("radius", 1.0)
            center = cfg.get("center", [0, 0])
            return (
                f"        {elem_id} = Circle(radius={radius}, "
                f"color={stroke_color}, stroke_width={stroke_w}, "
                f"fill_color={fill_color}, fill_opacity={fill_op})"
                f".move_to({_vec3(center)})"
            )
        case "rectangle":
            w = cfg.get("width", 2.0)
            h = cfg.get("height", 1.0)
            center = cfg.get("center", cfg.get("corner1", [0, 0]))
            return (
                f"        {elem_id} = Rectangle("
                f"width={w}, height={h}, "
                f"color={stroke_color}, stroke_width={stroke_w}, "
                f"fill_color={fill_color}, fill_opacity={fill_op})"
                f".move_to({_vec3(center)})"
            )
        case "triangle":
            verts = cfg.get("vertices", [[-1, -1], [1, -1], [0, 1]])
            pts = ", ".join(_vec3(v) for v in verts)
            return (
                f"        {elem_id} = Polygon({pts}, "
                f"color={stroke_color}, stroke_width={stroke_w}, "
                f"fill_color={fill_color}, fill_opacity={fill_op})"
            )
        case "polygon":
            verts = cfg.get("vertices", [[0, 0], [1, 0], [1, 1], [0, 1]])
            pts = ", ".join(_vec3(v) for v in verts)
            return (
                f"        {elem_id} = Polygon({pts}, "
                f"color={stroke_color}, stroke_width={stroke_w}, "
                f"fill_color={fill_color}, fill_opacity={fill_op})"
            )
        case "regular_polygon":
            n = cfg.get("n_sides", 6)
            r = cfg.get("radius", 1.0)
            center = cfg.get("center", [0, 0])
            return (
                f"        {elem_id} = RegularPolygon(n={n}, "
                f"color={stroke_color}, stroke_width={stroke_w}, "
                f"fill_color={fill_color}, fill_opacity={fill_op})"
                f".scale({r}).move_to({_vec3(center)})"
            )
        case _:
            return f"        {elem_id} = Circle(radius=0.5, color={stroke_color})"


def _build_text_label(elem_id: str, cfg: dict[str, Any], has_axes: bool = False) -> str:
    text = cfg.get("text", "")
    fs = cfg.get("font_size", 36)
    color = _python_color(cfg.get("color", "#FFFFFF"))
    pos = cfg.get("position", [0, 0, 0])
    direction = cfg.get("direction")

    has_latex = "$" in text
    has_cjk = any("\u4e00" <= c <= "\u9fff" for c in text)
    if has_cjk:
        manim_cls = "Text"
        cleaned = text.replace("$", "")
    elif has_latex:
        manim_cls = "MathTex"
        cleaned = text.replace("$", "")
    else:
        manim_cls = "Tex"
        cleaned = text.replace("$", "")

    parts = [
        f"        {elem_id} = {manim_cls}(r'{cleaned}', font_size={fs}, color={color})"
    ]
    if any(p != 0 for p in pos):
        if has_axes:
            parts.append(f"        {elem_id}.move_to(axes.c2p({pos[0]}, {pos[1]}))")
        else:
            parts.append(f"        {elem_id}.move_to({_vec3(pos)})")
    if direction:
        parts.append(f"        {elem_id}.shift({_vec3(direction)} * 0.3)")
    return "\n".join(parts)


def _build_point(elem_id: str, cfg: dict[str, Any]) -> str:
    pos = cfg.get("position", [0, 0, 0])
    r = cfg.get("radius", 0.08)
    color = _python_color(cfg.get("color", "#FFFF00"))
    return f"        {elem_id} = Dot(point=axes.c2p({pos[0]}, {pos[1]}), radius={r}, color={color})"


def _build_line_segment(elem_id: str, cfg: dict[str, Any]) -> str:
    start = cfg.get("start", [0, 0, 0])
    end = cfg.get("end", [1, 0, 0])
    color = _python_color(cfg.get("color", "#FFFFFF"))
    sw = cfg.get("stroke_width", 2.0)
    return (
        f"        {elem_id} = Line("
        f"start=axes.c2p({start[0]}, {start[1]}), "
        f"end=axes.c2p({end[0]}, {end[1]}), "
        f"color={color}, stroke_width={sw})"
    )


def _build_arrow(elem_id: str, cfg: dict[str, Any]) -> str:
    start = cfg.get("start", [0, 0, 0])
    end = cfg.get("end", [1, 0, 0])
    color = _python_color(cfg.get("color", "#FFFF00"))
    sw = cfg.get("stroke_width", 3.0)
    buff = cfg.get("buff", 0.25)
    return (
        f"        {elem_id} = Arrow("
        f"start=axes.c2p({start[0]}, {start[1]}), "
        f"end=axes.c2p({end[0]}, {end[1]}), "
        f"color={color}, stroke_width={sw}, buff={buff})"
    )


def _build_equation_step(elem_id: str, cfg: dict[str, Any], has_axes: bool = False) -> str:
    exprs = cfg.get("expressions", ["x = 1"])
    fs = cfg.get("font_size", 48)
    color = _python_color(cfg.get("color", "#FFFFFF"))
    pos = cfg.get("position", [0, 0, 0])

    exprs_str = ", ".join(f"r'{e}'" for e in exprs)
    parts = [
        f"        {elem_id}_all = MathTex({exprs_str}, font_size={fs}, color={color})"
    ]
    if has_axes:
        parts.append(f"        {elem_id}_all.arrange(DOWN, buff=0.4).move_to(axes.c2p({pos[0]}, {pos[1]}))")
    else:
        parts.append(f"        {elem_id}_all.arrange(DOWN, buff=0.4).move_to({_vec3(pos)})")
    for i in range(len(exprs)):
        parts.append(f"        {elem_id}_{i} = {elem_id}_all[{i}]")
    parts.append(f"        {elem_id} = {elem_id}_all")
    return "\n".join(parts)


_ELEMENT_BUILDERS = {
    "coordinate_system": _build_coordinate_system,
    "function_plot": _build_function_plot,
    "geometric_shape": _build_geometric_shape,
    "text_label": _build_text_label,
    "point": _build_point,
    "line_segment": _build_line_segment,
    "arrow": _build_arrow,
    "equation_step": _build_equation_step,
}


def _safe_var(elem_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]", "_", elem_id)


def generate_manim_script(description: AnimationTimeline) -> tuple[str, str]:
    """将 AnimationTimeline 转换为可执行的 Manim CE Python 脚本。

    Returns:
        (script_text, scene_name) 元组
    """
    import hashlib
    title_hash = hashlib.md5(description.title.encode()).hexdigest()[:8]
    scene_name = f"Animation_{title_hash}_Scene"

    elements_by_id: dict[str, AnimationElement] = {e.id: e for e in description.elements}
    var_map: dict[str, str] = {e.id: _safe_var(e.id) for e in description.elements}

    setup_lines: list[str] = []
    has_axes = any(e.type == "coordinate_system" for e in description.elements)

    if has_axes:
        cs_elem = next(e for e in description.elements if e.type == "coordinate_system")
        cs_var = var_map[cs_elem.id]
        cs_code = _build_coordinate_system(cs_var, cs_elem.config, description.width, description.height)
        setup_lines.append(cs_code)
        setup_lines.append(f"        self.add({cs_var})")
        if cs_elem.config.get("show_grid", True):
            setup_lines.append(f"        self.add({cs_var}_grid)")
        setup_lines.append(f"        self.add({cs_var}_labels)")
        setup_lines.append(f"        axes = {cs_var}")

    for elem in description.elements:
        vid = var_map[elem.id]
        if elem.type == "coordinate_system":
            continue

        builder = _ELEMENT_BUILDERS.get(elem.type)
        if builder is None:
            logger.warning("未知的元素类型: %s, 跳过", elem.type)
            continue

        if elem.type in ("text_label", "equation_step"):
            code = builder(vid, elem.config, has_axes=has_axes)
        else:
            code = builder(vid, elem.config)
        setup_lines.append(code)

    action_lines: list[str] = []
    total_time = 0.0

    for step in description.steps:
        vid = var_map.get(step.target_element_id, _safe_var(step.target_element_id))
        dur = step.duration
        run_time = f"run_time={dur}"

        match step.action:
            case "create":
                elem = elements_by_id.get(step.target_element_id)
                if elem and elem.type == "coordinate_system":
                    continue
                if elem and elem.type == "function_plot":
                    action_lines.append(f"        self.play(Create({vid}), {run_time})")
                    if elem.config.get("label"):
                        action_lines.append(f"        self.play(FadeIn({vid}_label), {run_time})")
                elif elem and elem.type == "geometric_shape":
                    action_lines.append(f"        self.play(Create({vid}), {run_time})")
                elif elem and elem.type == "text_label":
                    action_lines.append(f"        self.play(Write({vid}), {run_time})")
                elif elem and elem.type == "equation_step":
                    n_expr = len(elem.config.get("expressions", ["x"]))
                    per_expr_time = step.duration / max(n_expr, 1)
                    expr_run_time = f"run_time={per_expr_time:.2f}"
                    for i in range(n_expr):
                        action_lines.append(f"        self.play(Write({vid}_{i}), {expr_run_time})")
                elif elem and elem.type == "point":
                    action_lines.append(f"        self.play(FadeIn({vid}), {run_time})")
                elif elem and elem.type == "arrow":
                    action_lines.append(f"        self.play(Create({vid}), {run_time})")
                elif elem and elem.type == "line_segment":
                    action_lines.append(f"        self.play(Create({vid}), {run_time})")
                else:
                    action_lines.append(f"        self.play(Create({vid}), {run_time})")

            case "transform":
                source_id = step.params.get("source_element_id", "")
                source_var = var_map.get(source_id, _safe_var(source_id))
                action_lines.append(f"        self.play(ReplacementTransform({source_var}, {vid}), {run_time})")

            case "replace":
                source_id = step.params.get("source_element_id", "")
                source_var = var_map.get(source_id, _safe_var(source_id))
                action_lines.append(f"        self.play(ReplacementTransform({source_var}, {vid}), {run_time})")

            case "move":
                shift = step.params.get("shift", [0, 0, 0])
                to_pos = step.params.get("to_position")
                if to_pos:
                    action_lines.append(f"        self.play({vid}.animate.move_to({_vec3(to_pos)}), {run_time})")
                else:
                    action_lines.append(f"        self.play({vid}.animate.shift({_vec3(shift)}), {run_time})")

            case "highlight":
                color = step.params.get("color", "#FFFF00")
                action_lines.append(
                    f"        self.play({vid}.animate.set_color({_python_color(color)}), {run_time})"
                )

            case "fade":
                action_lines.append(f"        self.play(FadeOut({vid}), {run_time})")

            case "write":
                action_lines.append(f"        self.play(Write({vid}), {run_time})")

            case "indicate":
                indicate_type = step.params.get("indicate_type", "flash")
                if indicate_type == "flash":
                    action_lines.append(f"        self.play(Flash({vid}), {run_time})")
                else:
                    action_lines.append(f"        self.play(Circumscribe({vid}), {run_time})")

            case _:
                logger.warning("未知的动作类型: %s", step.action)

        total_time = max(total_time, step.time_start + step.duration)

    header = [
        "#!/usr/bin/env python3",
        f'"""Auto-generated Manim CE animation: {description.title}"""',
        "",
        "from manim import *",
        "",
        "",
        f"config.pixel_width = {description.width}",
        f"config.pixel_height = {description.height}",
        f"config.frame_rate = {description.fps}",
        f'config.background_color = "{description.background_color}"',
        "",
        "",
        f"class {scene_name}(Scene):",
        "    def construct(self):",
    ]

    body = "\n".join(setup_lines) + "\n\n" + "\n".join(action_lines) + "\n\n        self.wait(1)\n"

    return "\n".join(header) + "\n" + body, scene_name


async def render_animation(script: str, output_dir: Path, scene_name: str) -> Path:
    """执行 Manim 渲染 MP4（通过 subprocess，headless 模式）。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    script_path = output_dir / f"{scene_name}.py"
    script_path.write_text(script, encoding="utf-8")

    media_dir = output_dir / "media"

    cmd = [
        sys.executable, "-m", "manim", "render",
        str(script_path),
        scene_name,
        "--format", "mp4",
        "--media_dir", str(media_dir),
        "--silent",
        "--disable_caching",
    ]

    env_override = {
        "DISPLAY": "",
    }

    logger.info("执行 Manim 渲染: %s", " ".join(cmd))

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env={**os.environ, **env_override},
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        err_msg = stderr.decode("utf-8", errors="replace")
        logger.error("Manim 渲染失败 (rc=%d): %s", proc.returncode, err_msg)
        raise RuntimeError(f"Manim rendering failed: {err_msg[:2000]}")

    mp4_files = list(media_dir.rglob("*.mp4"))
    if not mp4_files:
        raise FileNotFoundError(f"Manim 渲染完成但未找到 MP4 文件: {media_dir}")

    final_mp4 = output_dir / f"{scene_name}.mp4"
    shutil.move(str(mp4_files[0]), str(final_mp4))
    shutil.rmtree(media_dir, ignore_errors=True)

    return final_mp4


async def generate_tts_audio(text: str, voice: str, output_path: Path) -> Path:
    """使用 Edge TTS 生成旁白音频。"""
    import edge_tts

    output_path.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))
    return output_path


async def merge_audio_video(video_path: Path, audio_path: Path, output_path: Path) -> Path:
    """使用 ffmpeg 合并音频和视频。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        str(output_path),
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        err_msg = stderr.decode("utf-8", errors="replace")
        logger.error("ffmpeg 合并失败 (rc=%d): %s", proc.returncode, err_msg)
        raise RuntimeError(f"ffmpeg merge failed: {err_msg[:2000]}")

    return output_path


def _generate_static_steps(description: AnimationTimeline) -> list[str]:
    """将 AnimationTimeline 转换为文本步骤描述(用于 manim 不可用时的降级)。"""
    steps: list[str] = []
    steps.append(f"动画标题: {description.title}")
    if description.narration:
        steps.append(f"旁白: {description.narration}")

    elements_by_id: dict[str, AnimationElement] = {e.id: e for e in description.elements}

    steps.append("\n--- 动画步骤 ---")
    for i, step in enumerate(description.steps, 1):
        elem = elements_by_id.get(step.target_element_id)
        elem_desc = elem.type if elem else step.target_element_id

        match step.action:
            case "create":
                steps.append(
                    f"{i}. 创建元素 '{elem_desc}' (持续 {step.duration:.1f}秒)"
                )
            case "transform":
                src = step.params.get("source_element_id", "?")
                steps.append(f"{i}. 变换元素: {src} → {elem_desc} (持续 {step.duration:.1f}秒)")
            case "replace":
                src = step.params.get("source_element_id", "?")
                steps.append(f"{i}. 替换元素: {src} → {elem_desc} (持续 {step.duration:.1f}秒)")
            case "move":
                shift = step.params.get("shift", [0, 0, 0])
                to_pos = step.params.get("to_position")
                if to_pos:
                    steps.append(f"{i}. 移动 '{elem_desc}' 到 {to_pos} (持续 {step.duration:.1f}秒)")
                else:
                    steps.append(f"{i}. 平移 '{elem_desc}' {shift} (持续 {step.duration:.1f}秒)")
            case "highlight":
                color = step.params.get("color", "?")
                steps.append(f"{i}. 高亮 '{elem_desc}' (颜色: {color},持续 {step.duration:.1f}秒)")
            case "fade":
                steps.append(f"{i}. 淡出 '{elem_desc}' (持续 {step.duration:.1f}秒)")
            case "write":
                steps.append(f"{i}. 写入 '{elem_desc}' (持续 {step.duration:.1f}秒)")
            case "indicate":
                ind_type = step.params.get("indicate_type", "flash")
                steps.append(f"{i}. 指示 '{elem_desc}' ({ind_type}, 持续 {step.duration:.1f}秒)")
            case _:
                steps.append(f"{i}. 执行动作 '{step.action}' 于 '{elem_desc}' (持续 {step.duration:.1f}秒)")

    return steps


async def render_animation_pipeline(
    description: AnimationTimeline,
    output_dir: Path,
    skip_video: bool = False,
    skip_audio: bool = False,
) -> AnimationResult:
    """完整动画渲染管线：生成脚本 → 渲染视频 → 生成音频 → 合并。

    如果 manim 不可用,降级为静态文本说明。
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    result = AnimationResult()

    if not check_manim_available():
        result.status = "static"
        result.static_steps = _generate_static_steps(description)
        logger.info("manim 不可用,返回静态说明")
        return result

    script, scene_name = generate_manim_script(description)
    script_path = output_dir / f"{scene_name}.py"
    script_path.write_text(script, encoding="utf-8")
    result.script_path = str(script_path)
    logger.info("已生成 Manim 脚本: %s", script_path)

    if not skip_video:
        try:
            video_path = await render_animation(script, output_dir, scene_name)
            result.video_path = str(video_path)
            logger.info("视频渲染完成: %s", video_path)
        except Exception as e:
            logger.error("视频渲染失败: %s", e)
            result.error = str(e)
            return result

    if not skip_audio and description.narration:
        try:
            audio_path = await generate_tts_audio(
                description.narration,
                description.voice,
                output_dir / f"{scene_name}_audio.mp3",
            )
            result.audio_path = str(audio_path)
            logger.info("音频生成完成: %s", audio_path)
        except Exception as e:
            logger.error("音频生成失败: %s", e)
            result.error = str(e)
            return result

    if result.video_path and result.audio_path:
        try:
            merged_path = await merge_audio_video(
                Path(result.video_path),
                Path(result.audio_path),
                output_dir / f"{scene_name}_final.mp4",
            )
            result.merged_path = str(merged_path)
            logger.info("音视频合并完成: %s", merged_path)
        except Exception as e:
            logger.error("音视频合并失败: %s", e)
            result.error = str(e)

    return result
