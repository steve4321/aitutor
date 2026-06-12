#!/usr/bin/env python3
"""Auto-generated Manim CE animation: 勾股定理面积证明"""

from manim import *


config.pixel_width = 1280
config.pixel_height = 720
config.frame_rate = 30
config.background_color = "#1a1a2e"


class Animation_2676fd73_Scene(Scene):
    def construct(self):
        title_text = Text(r'勾股定理的面积证明', font_size=40, color="#FFFFFF")
        title_text.move_to([0, 3.2, 0])
        right_triangle = Polygon([-2, -1, 0], [1, -1, 0], [-2, 2, 0], color="#58C4DD", stroke_width=3.0, fill_color="#58C4DD", fill_opacity=0.3)
        side_a_label = MathTex(r'a = 3', font_size=28, color="#58C4DD")
        side_a_label.move_to([-0.5, -1.7, 0])
        side_b_label = MathTex(r'b = 4', font_size=28, color="#58C4DD")
        side_b_label.move_to([-2.7, 0.5, 0])
        side_c_label = MathTex(r'c = 5', font_size=28, color="#E74C3C")
        side_c_label.move_to([0.2, 1.3, 0])
        square_a = Rectangle(width=3.0, height=3.0, color="#27AE60", stroke_width=3.0, fill_color="#27AE60", fill_opacity=0.3).move_to([-0.5, -2.5, 0])
        square_a_label = MathTex(r'a^2 = 9', font_size=32, color="#27AE60")
        square_a_label.move_to([-0.5, -2.5, 0])
        square_b = Rectangle(width=4.0, height=4.0, color="#F39C12", stroke_width=3.0, fill_color="#F39C12", fill_opacity=0.3).move_to([-4.0, 0.5, 0])
        square_b_label = MathTex(r'b^2 = 16', font_size=32, color="#F39C12")
        square_b_label.move_to([-4.0, 0.5, 0])
        equation_1_all = MathTex(r'a^2 + b^2 = c^2', r'3^2 + 4^2 = 5^2', r'9 + 16 = 25', r'25 = 25 \checkmark', font_size=30, color="#FFFFFF")
        equation_1_all.arrange(DOWN, buff=0.4).move_to([2.5, -0.5, 0])
        equation_1_0 = equation_1_all[0]
        equation_1_1 = equation_1_all[1]
        equation_1_2 = equation_1_all[2]
        equation_1_3 = equation_1_all[3]
        equation_1 = equation_1_all
        conclusion_text = MathTex(r'a^2 + b^2 = c^2', font_size=44, color="#FFFF00")
        conclusion_text.move_to([2.5, -2.5, 0])

        self.play(Write(title_text), run_time=2.0)
        self.play(Create(right_triangle), run_time=2.0)
        self.play(Write(side_a_label), run_time=1.0)
        self.play(Write(side_b_label), run_time=1.0)
        self.play(Write(side_c_label), run_time=1.0)
        self.play(Create(square_a), run_time=2.0)
        self.play(Write(square_a_label), run_time=1.5)
        self.play(Create(square_b), run_time=2.0)
        self.play(Write(square_b_label), run_time=1.5)
        self.play(Circumscribe(square_a), run_time=1.5)
        self.play(Circumscribe(square_b), run_time=1.5)
        self.play(Write(equation_1_0), run_time=1.50)
        self.play(Write(equation_1_1), run_time=1.50)
        self.play(Write(equation_1_2), run_time=1.50)
        self.play(Write(equation_1_3), run_time=1.50)
        self.play(Write(conclusion_text), run_time=2.0)
        self.play(conclusion_text.animate.set_color("#FFFF00"), run_time=2.0)

        self.wait(1)
