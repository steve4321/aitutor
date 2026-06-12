#!/usr/bin/env python3
"""Auto-generated Manim CE animation: 二次函数图像变换"""

from manim import *


config.pixel_width = 1280
config.pixel_height = 720
config.frame_rate = 30
config.background_color = "#1a1a2e"


class Animation_71af96ef_Scene(Scene):
    def construct(self):
        axes = Axes(
            x_range=[-4, 8, 1],
            y_range=[-2, 8, 1],
            x_length=10.666666666666666,
            y_length=6.0,
            axis_config={'include_numbers': True},
            tips=False,
        )
        axes_labels = axes.get_axis_labels(x_label='x', y_label='y')
        axes_grid = NumberPlane(
            x_range=[-4, 8, 1], y_range=[-2, 8, 1],
            x_length=10.666666666666666,
            y_length=6.0,
            background_line_style={'stroke_opacity': 0.3},
        )
        self.add(axes)
        self.add(axes_grid)
        self.add(axes_labels)
        axes = axes
        base_curve = axes.plot(
            lambda x: x**2,
            color="#58C4DD",
            stroke_width=3.0,
        )
        base_curve_label = axes.get_graph_label(
            base_curve, r'y = x^2',
            x_val=axes.x_range[1] * 0.7, direction=UR
        )
        transformed_curve = axes.plot(
            lambda x: (x - 2)**2 + 1,
            color="#E74C3C",
            stroke_width=3.0,
        )
        transformed_curve_label = axes.get_graph_label(
            transformed_curve, r'y = (x-2)^2 + 1',
            x_val=axes.x_range[1] * 0.7, direction=UR
        )
        vertex_origin = Dot(point=axes.c2p(0, 0), radius=0.1, color="#58C4DD")
        vertex_new = Dot(point=axes.c2p(2, 1), radius=0.1, color="#E74C3C")
        vertex_label_origin = MathTex(r'(0, 0)', font_size=28, color="#58C4DD")
        vertex_label_origin.move_to(axes.c2p(0.8, -0.8))
        vertex_label_new = MathTex(r'(2, 1)', font_size=28, color="#E74C3C")
        vertex_label_new.move_to(axes.c2p(3.2, 0.2))
        shift_arrow_h = Arrow(start=axes.c2p(0, -1.5), end=axes.c2p(2, -1.5), color="#FFFF00", stroke_width=3.0, buff=0.1)
        shift_arrow_v = Arrow(start=axes.c2p(2.5, 0), end=axes.c2p(2.5, 1), color="#FFFF00", stroke_width=3.0, buff=0.1)
        shift_label_h = MathTex(r'\Delta x = 2', font_size=24, color="#FFFF00")
        shift_label_h.move_to(axes.c2p(1, -2.2))
        shift_label_v = MathTex(r'\Delta y = 1', font_size=24, color="#FFFF00")
        shift_label_v.move_to(axes.c2p(3.8, 0.5))
        title_text = Text(r'y = (x-2)^2 + 1 的图像变换', font_size=36, color="#FFFFFF")
        title_text.move_to(axes.c2p(0, 3.5))
        equation_summary_all = MathTex(r'y = x^2', r'\downarrow \quad x \to x-2', r'y = (x-2)^2', r'\downarrow \quad +1', r'y = (x-2)^2 + 1', font_size=32, color="#FFFFFF")
        equation_summary_all.arrange(DOWN, buff=0.4).move_to(axes.c2p(-3.5, -1))
        equation_summary_0 = equation_summary_all[0]
        equation_summary_1 = equation_summary_all[1]
        equation_summary_2 = equation_summary_all[2]
        equation_summary_3 = equation_summary_all[3]
        equation_summary_4 = equation_summary_all[4]
        equation_summary = equation_summary_all

        self.play(Create(base_curve), run_time=2.0)
        self.play(FadeIn(base_curve_label), run_time=2.0)
        self.play(FadeIn(vertex_origin), run_time=1.0)
        self.play(Write(vertex_label_origin), run_time=1.5)
        self.play(Create(shift_arrow_h), run_time=2.0)
        self.play(Write(shift_label_h), run_time=1.5)
        self.play(Create(shift_arrow_v), run_time=2.0)
        self.play(Write(shift_label_v), run_time=1.5)
        self.play(ReplacementTransform(base_curve, transformed_curve), run_time=3.0)
        self.play(transformed_curve.animate.set_color("#E74C3C"), run_time=1.5)
        self.play(FadeIn(vertex_new), run_time=1.0)
        self.play(Write(vertex_label_new), run_time=1.5)
        self.play(Write(title_text), run_time=1.5)
        self.play(Write(equation_summary_0), run_time=1.20)
        self.play(Write(equation_summary_1), run_time=1.20)
        self.play(Write(equation_summary_2), run_time=1.20)
        self.play(Write(equation_summary_3), run_time=1.20)
        self.play(Write(equation_summary_4), run_time=1.20)
        self.play(Circumscribe(transformed_curve), run_time=1.0)

        self.wait(1)
