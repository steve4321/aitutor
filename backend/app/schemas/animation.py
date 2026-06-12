"""动画渲染管线 Pydantic 模型。

定义 AI 产出的动画描述格式，覆盖数学动画常见类型：
坐标系、函数图、几何图形、文本标签、点、线段、箭头、方程求解步骤。
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class CoordinateSystemConfig(BaseModel):
    """坐标系配置"""
    x_range: list[float] = Field([-7, 7, 1], description="[min, max, step]")
    y_range: list[float] = Field([-4, 4, 1], description="[min, max, step]")
    x_label: str = "x"
    y_label: str = "y"
    show_grid: bool = True
    axis_config: dict | None = None


class FunctionPlotConfig(BaseModel):
    """函数图像配置"""
    expression: str = Field(..., description="Python lambda 表达式，如 'lambda x: x**2'")
    color: str = "#58C4DD"
    stroke_width: float = 3.0
    x_range: list[float] | None = None
    label: str | None = None


class GeometricShapeConfig(BaseModel):
    """几何图形配置"""
    shape_type: str = Field(..., description="circle | rectangle | triangle | polygon | regular_polygon")
    radius: float | None = None
    center: list[float] | None = None
    width: float | None = None
    height: float | None = None
    corner1: list[float] | None = None
    corner2: list[float] | None = None
    vertices: list[list[float]] | None = None
    n_sides: int | None = None
    fill_color: str | None = None
    fill_opacity: float = 0.0
    stroke_color: str = "#FFFFFF"
    stroke_width: float = 2.0


class TextLabelConfig(BaseModel):
    """文本/数学标签配置"""
    text: str = Field(..., description="支持 LaTeX: $x^2 + 1$ 或纯文本")
    font_size: int = 36
    color: str = "#FFFFFF"
    position: list[float] = Field([0, 0, 0], description="3D position [x, y, z]")
    direction: list[float] | None = None


class PointConfig(BaseModel):
    """点/圆点配置"""
    position: list[float] = Field([0, 0, 0])
    radius: float = 0.08
    color: str = "#FFFF00"


class LineSegmentConfig(BaseModel):
    """线段配置"""
    start: list[float] = Field([0, 0, 0])
    end: list[float] = Field([1, 0, 0])
    color: str = "#FFFFFF"
    stroke_width: float = 2.0


class ArrowConfig(BaseModel):
    """箭头配置"""
    start: list[float] = Field([0, 0, 0])
    end: list[float] = Field([1, 0, 0])
    color: str = "#FFFF00"
    stroke_width: float = 3.0
    buff: float = 0.25
    max_tip_length_to_length_ratio: float = 0.25


class EquationStepConfig(BaseModel):
    """方程求解步骤配置"""
    expressions: list[str] = Field(..., description="按顺序展示的 LaTeX 表达式列表")
    font_size: int = 48
    color: str = "#FFFFFF"
    highlight_color: str = "#FFFF00"
    position: list[float] = Field([0, 0, 0])


_ELEMENT_CONFIG_MAP: dict[str, type[BaseModel]] = {
    "coordinate_system": CoordinateSystemConfig,
    "function_plot": FunctionPlotConfig,
    "geometric_shape": GeometricShapeConfig,
    "text_label": TextLabelConfig,
    "point": PointConfig,
    "line_segment": LineSegmentConfig,
    "arrow": ArrowConfig,
    "equation_step": EquationStepConfig,
}


class AnimationElement(BaseModel):
    """动画中的一个可操作元素"""
    id: str = Field(..., description="元素唯一 ID，用于 timeline 引用")
    type: str = Field(..., description="coordinate_system | function_plot | geometric_shape | text_label | point | line_segment | arrow | equation_step")
    config: dict = Field(..., description="类型特定的配置，见上方 *Config 模型")
    layer: int = Field(0, description="z-order，值大的在上层")


class AnimationStep(BaseModel):
    """时间轴中的一个动作步骤"""
    time_start: float = Field(..., ge=0, description="开始时间（秒）")
    duration: float = Field(..., gt=0, description="持续时间（秒）")
    action: str = Field(
        ...,
        description="create | transform | move | highlight | fade | write | indicate | replace",
    )
    target_element_id: str = Field(..., description="目标元素 ID")
    params: dict = Field(
        default_factory=dict,
        description="动作参数，如 direction, shift, color, source_element_id (for transform/replace)",
    )


class AnimationTimeline(BaseModel):
    """完整的动画描述，可由 AI Agent 直接产出"""
    title: str
    width: int = 1280
    height: int = 720
    fps: int = 30
    background_color: str = "#1a1a2e"
    elements: list[AnimationElement]
    steps: list[AnimationStep]
    narration: str = Field("", description="旁白文本，用于 TTS 音频生成")
    voice: str = "zh-CN-YunxiNeural"


class AnimationResult(BaseModel):
    """渲染管线输出"""
    status: Literal["video", "static"] = Field(
        "video", description="渲染状态: video=成功生成视频, static=降级为静态说明"
    )
    video_path: str | None = None
    audio_path: str | None = None
    merged_path: str | None = None
    script_path: str | None = None
    thumbnail_path: str | None = None
    duration_sec: float | None = None
    error: str | None = None
    static_steps: list[str] | None = Field(
        None, description="当 manim 不可用时,文本描述的动画步骤列表"
    )
