"""
Sample Manim Animation for Physics Problem
This serves as a template for AI-generated Manim code
"""

from manim import *


class PhysicsSolution(Scene):
    def construct(self):
        # Intro (5 seconds)
        title = Text("Rolling Ball on Inclined Plane", font_size=36)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))

        # Step 1: Setup the problem (10 seconds)
        # Draw inclined plane
        plane_start = LEFT * 3 + UP * 2
        plane_end = RIGHT * 3 + DOWN * 1
        plane = Line(plane_start, plane_end, color=BLUE, stroke_width=4)

        # Add angle indicator
        angle_arc = Arc(
            radius=0.8,
            start_angle=0,
            angle=-0.524,  # ~30 degrees in radians
            color=YELLOW,
            arc_center=plane_start
        )
        angle_label = MathTex(r"30°", font_size=28).next_to(angle_arc, RIGHT, buff=0.2)

        # Add ball
        ball = Circle(radius=0.3, color=RED, fill_opacity=1, stroke_color=WHITE)
        ball.move_to(plane_start + RIGHT * 0.5 + UP * 0.5)

        # Display setup
        self.play(Create(plane), run_time=1)
        self.play(Create(angle_arc), Write(angle_label), run_time=1)
        self.play(FadeIn(ball), run_time=0.5)
        self.wait(6.5)

        # Step 2: Show given information (12 seconds)
        given_info = VGroup(
            MathTex(r"m = 2 \text{ kg}", font_size=32),
            MathTex(r"r = 0.5 \text{ m}", font_size=32),
            MathTex(r"\theta = 30°", font_size=32),
            MathTex(r"h = 3 \text{ m}", font_size=32),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        given_info.to_edge(RIGHT, buff=1)

        self.play(Write(given_info[0]), run_time=1)
        self.wait(1)
        self.play(Write(given_info[1]), run_time=1)
        self.wait(1)
        self.play(Write(given_info[2]), run_time=1)
        self.wait(1)
        self.play(Write(given_info[3]), run_time=1)
        self.wait(5)

        # Step 3: Energy conservation equation (15 seconds)
        self.play(FadeOut(given_info), run_time=0.5)

        energy_eq = MathTex(
            r"mgh = \frac{1}{2}mv^2 + \frac{1}{2}I\omega^2",
            font_size=36
        )
        energy_eq.to_edge(UP, buff=1)

        self.play(Write(energy_eq), run_time=2)
        self.wait(2)

        # Show moment of inertia for sphere
        moment_eq = MathTex(
            r"I = \frac{2}{5}mr^2",
            font_size=32
        )
        moment_eq.next_to(energy_eq, DOWN, buff=0.5)

        self.play(Write(moment_eq), run_time=1.5)
        self.wait(2)

        # Show rolling condition
        rolling_eq = MathTex(
            r"v = r\omega",
            font_size=32
        )
        rolling_eq.next_to(moment_eq, DOWN, buff=0.5)

        self.play(Write(rolling_eq), run_time=1.5)
        self.wait(6.5)

        # Step 4: Substitute and simplify (18 seconds)
        self.play(FadeOut(moment_eq), FadeOut(rolling_eq), run_time=0.5)

        substituted = MathTex(
            r"mgh = \frac{1}{2}mv^2 + \frac{1}{2} \cdot \frac{2}{5}mr^2 \cdot \frac{v^2}{r^2}",
            font_size=28
        )
        substituted.move_to(energy_eq.get_center())

        self.play(Transform(energy_eq, substituted), run_time=2)
        self.wait(3)

        simplified = MathTex(
            r"gh = \frac{1}{2}v^2 + \frac{1}{5}v^2",
            font_size=32
        )
        simplified.next_to(energy_eq, DOWN, buff=0.8)

        self.play(Write(simplified), run_time=2)
        self.wait(3)

        combined = MathTex(
            r"gh = \frac{7}{10}v^2",
            font_size=32
        )
        combined.next_to(simplified, DOWN, buff=0.5)

        self.play(Write(combined), run_time=2)
        self.wait(5.5)

        # Step 5: Solve for velocity (15 seconds)
        self.play(FadeOut(energy_eq), FadeOut(simplified), run_time=0.5)

        solve_v = MathTex(
            r"v = \sqrt{\frac{10gh}{7}}",
            font_size=36
        )
        solve_v.move_to(combined.get_center())

        self.play(Transform(combined, solve_v), run_time=2)
        self.wait(3)

        # Substitute values
        with_values = MathTex(
            r"v = \sqrt{\frac{10 \times 9.8 \times 3}{7}}",
            font_size=32
        )
        with_values.next_to(combined, DOWN, buff=0.8)

        self.play(Write(with_values), run_time=2)
        self.wait(3)

        # Final answer
        final_answer = MathTex(
            r"v \approx 6.49 \text{ m/s}",
            font_size=40,
            color=GREEN
        )
        final_answer.next_to(with_values, DOWN, buff=0.8)

        self.play(Write(final_answer), run_time=2)
        self.wait(2.5)

        # Conclusion (5 seconds)
        self.play(
            FadeOut(combined),
            FadeOut(with_values),
            FadeOut(plane),
            FadeOut(angle_arc),
            FadeOut(angle_label),
            FadeOut(ball),
            run_time=1
        )

        conclusion = Text(
            "Final velocity: 6.49 m/s",
            font_size=40,
            color=GREEN
        )

        self.play(Transform(final_answer, conclusion), run_time=1)
        self.wait(3)

        self.play(FadeOut(final_answer), run_time=0.5)


# To render this scene:
# manim -qh sample_manim.py PhysicsSolution
