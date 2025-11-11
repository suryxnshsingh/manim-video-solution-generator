"""
Enhanced 3Blue1Brown-Style Manim Animation for Physics Problem
Focus on visual storytelling, dynamic animations, and engaging presentation
"""

from manim import *


class PhysicsSolution(Scene):
    def construct(self):
        # ============================================================
        # PART 1: VISUAL SETUP - Show the problem scenario (12 seconds)
        # ============================================================

        # Elegant title with fade-in
        title = Text("Rolling Ball on an Inclined Plane", font_size=44, weight=BOLD)
        title.set_color_by_gradient(BLUE, TEAL)
        self.play(FadeIn(title, shift=DOWN), run_time=1.5)
        self.wait(1.5)
        self.play(FadeOut(title, shift=UP), run_time=1)

        # Create inclined plane with proper perspective
        plane_start = LEFT * 4 + UP * 2.5
        plane_end = RIGHT * 4 + DOWN * 1.5

        # Ground reference line
        ground = Line(LEFT * 5, RIGHT * 5, color=GRAY).shift(DOWN * 1.5)

        # Inclined plane with thickness
        plane = Line(plane_start, plane_end, color=BLUE_D, stroke_width=6)
        plane_surface = Line(plane_start, plane_end, color=BLUE_C, stroke_width=4).shift(UP * 0.05)

        # Height indicator (vertical line)
        height_line = DashedLine(
            plane_start,
            plane_start + DOWN * 3.5,
            color=YELLOW,
            stroke_width=2
        )
        height_brace = Brace(height_line, direction=LEFT, color=YELLOW)
        height_label = MathTex("h = 3\\text{ m}", color=YELLOW, font_size=32)
        height_label.next_to(height_brace, LEFT)

        # Angle indicator with arc
        angle_arc = Arc(
            radius=0.6,
            start_angle=0,
            angle=-0.524,  # 30 degrees
            color=ORANGE,
            arc_center=plane_start
        )
        angle_label = MathTex(r"30°", color=ORANGE, font_size=30)
        angle_label.next_to(angle_arc, RIGHT * 1.5 + DOWN * 0.3)

        # Create sphere (not just a circle - show it's 3D)
        ball_radius = 0.35
        ball = Circle(radius=ball_radius, color=RED_E, fill_opacity=1, stroke_color=RED_A, stroke_width=3)

        # Add shine effect to ball
        shine = Circle(radius=ball_radius * 0.3, color=WHITE, fill_opacity=0.8, stroke_width=0)
        shine.move_to(ball.get_center() + UP * 0.15 + LEFT * 0.1)
        ball_group = VGroup(ball, shine)

        # Position ball at top of incline
        ball_group.move_to(plane_start + RIGHT * 0.8 + UP * 0.5)

        # Animate the setup
        self.play(
            Create(ground),
            Create(plane),
            Create(plane_surface),
            run_time=1.5
        )
        self.play(
            Create(height_line),
            GrowFromCenter(height_brace),
            Write(height_label),
            run_time=1.5
        )
        self.play(
            Create(angle_arc),
            Write(angle_label),
            run_time=1
        )
        self.play(FadeIn(ball_group, scale=0.5), run_time=1)

        # Add given information box
        given_box = VGroup(
            MathTex(r"m = 2\text{ kg}", font_size=28),
            MathTex(r"r = 0.5\text{ m}", font_size=28),
            MathTex(r"v_0 = 0\text{ (starts from rest)}", font_size=28)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        given_box.to_corner(UR, buff=0.8)

        box_border = SurroundingRectangle(given_box, color=WHITE, buff=0.3, corner_radius=0.1)
        given_title = Text("Given:", font_size=24, color=YELLOW).next_to(box_border, UP)

        self.play(
            Create(box_border),
            Write(given_title),
            FadeIn(given_box, shift=DOWN),
            run_time=2
        )
        self.wait(1)

        # ============================================================
        # PART 2: SHOW THE MOTION - Animate the ball rolling (10 seconds)
        # ============================================================

        # Calculate path for ball
        ball_start = ball_group.get_center()
        ball_end = plane_end + UP * 0.5 + LEFT * 0.3

        # Create motion path
        motion_path = Line(ball_start, ball_end, color=RED, stroke_width=2, stroke_opacity=0.3)

        # Show what we want to find
        find_text = Text("Find: velocity at bottom", font_size=32, color=GREEN)
        find_arrow = Arrow(start=UP, end=DOWN, color=GREEN, stroke_width=4)
        find_arrow.next_to(ball_end, DOWN, buff=0.5)
        find_text.next_to(find_arrow, DOWN)

        self.play(Write(find_text), GrowArrow(find_arrow), run_time=1.5)
        self.wait(0.5)

        # Fade out given info to make room
        self.play(FadeOut(given_box), FadeOut(box_border), FadeOut(given_title), run_time=0.5)

        # Animate ball rolling down with rotation
        rolling_time = 3

        # Create rotation updater
        angle_tracker = ValueTracker(0)

        def update_ball_rotation(mob):
            angle = angle_tracker.get_value()
            # Rotate ball
            mob[0].rotate(angle - mob.angle if hasattr(mob, 'angle') else angle, about_point=mob.get_center())
            mob.angle = angle
            # Keep shine in place (relative to ball)
            mob[1].move_to(mob[0].get_center() + UP * 0.15 + LEFT * 0.1)

        ball_group.add_updater(update_ball_rotation)

        self.play(
            MoveAlongPath(ball_group, motion_path),
            angle_tracker.animate.set_value(8 * PI),  # Multiple rotations
            run_time=rolling_time,
            rate_func=there_and_back  # Slow start, fast middle, slow end
        )

        ball_group.remove_updater(update_ball_rotation)

        # Velocity vector appears at bottom
        velocity_arrow = Arrow(
            ball_group.get_center(),
            ball_group.get_center() + RIGHT * 2,
            color=GREEN,
            buff=0,
            stroke_width=6,
            max_tip_length_to_length_ratio=0.15
        )
        velocity_label = MathTex("v = ?", color=GREEN, font_size=36)
        velocity_label.next_to(velocity_arrow, UP)

        self.play(
            GrowArrow(velocity_arrow),
            Write(velocity_label),
            run_time=1.5
        )
        self.wait(1.5)

        # ============================================================
        # PART 3: ENERGY ANALYSIS - Show energy transformation (15 seconds)
        # ============================================================

        # Fade out scene elements, keep ball
        self.play(
            FadeOut(plane), FadeOut(plane_surface), FadeOut(ground),
            FadeOut(height_line), FadeOut(height_brace), FadeOut(height_label),
            FadeOut(angle_arc), FadeOut(angle_label),
            FadeOut(find_text), FadeOut(find_arrow),
            FadeOut(velocity_arrow), FadeOut(velocity_label),
            ball_group.animate.scale(0.7).to_edge(LEFT, buff=1.5).shift(UP * 1),
            run_time=1.5
        )

        # Energy conservation title
        energy_title = Text("Energy Conservation", font_size=36, color=BLUE)
        energy_title.to_edge(UP, buff=0.5)
        self.play(Write(energy_title), run_time=1)

        # Initial energy (potential)
        initial_energy = VGroup(
            Text("Initial:", font_size=28, color=YELLOW),
            MathTex(r"E_i = mgh", font_size=32, color=YELLOW)
        ).arrange(DOWN, buff=0.3)
        initial_energy.next_to(ball_group, RIGHT, buff=1).shift(UP * 0.5)

        # Final energy (kinetic translational + rotational)
        final_energy = VGroup(
            Text("Final:", font_size=28, color=GREEN),
            MathTex(r"E_f = \frac{1}{2}mv^2 + \frac{1}{2}I\omega^2", font_size=28, color=GREEN)
        ).arrange(DOWN, buff=0.3)
        final_energy.next_to(ball_group, RIGHT, buff=1).shift(DOWN * 0.5)

        self.play(FadeIn(initial_energy, shift=RIGHT), run_time=1.5)
        self.wait(1)
        self.play(FadeIn(final_energy, shift=RIGHT), run_time=1.5)
        self.wait(1)

        # Main equation with boundary checking
        main_eq = MathTex(
            r"mgh = \frac{1}{2}mv^2 + \frac{1}{2}I\omega^2",
            font_size=36
        )
        main_eq.move_to(ORIGIN + DOWN * 0.5)

        # BOUNDARY CHECK: Ensure equation fits on screen
        if main_eq.get_right()[0] > 6.5:
            main_eq.scale_to_fit_width(13)

        self.play(
            FadeOut(initial_energy),
            FadeOut(final_energy),
            FadeOut(ball_group),
            Write(main_eq),
            run_time=2
        )
        self.wait(2)

        # ============================================================
        # PART 4: SOLVE STEP-BY-STEP with visual transforms (20 seconds)
        # ============================================================

        # Moment of inertia for sphere
        moment_eq = MathTex(
            r"I = \frac{2}{5}mr^2",
            font_size=32,
            color=BLUE
        )
        moment_eq.to_edge(LEFT, buff=1).shift(UP * 2)

        # Rolling condition
        rolling_eq = MathTex(
            r"v = r\omega",
            font_size=32,
            color=BLUE
        )
        rolling_eq.next_to(moment_eq, DOWN, buff=0.5, aligned_edge=LEFT)

        self.play(
            Write(moment_eq),
            Write(rolling_eq),
            run_time=2
        )
        self.wait(1.5)

        # EXAMPLE: Clean sequential replacement (NO OVERLAP!)
        # This is the PREFERRED method for calculation steps

        # Fade out reference equations first
        self.play(
            FadeOut(moment_eq),
            FadeOut(rolling_eq),
            run_time=0.8
        )
        self.wait(0.3)

        # Step 1: Start with main equation
        eq_step1 = MathTex(r"mgh = \frac{1}{2}mv^2 + \frac{1}{2}I\omega^2", font_size=32)
        eq_step1.move_to(ORIGIN)
        if eq_step1.get_right()[0] > 6.5:
            eq_step1.scale_to_fit_width(12)
        self.play(ReplacementTransform(main_eq, eq_step1), run_time=1.2)
        self.wait(0.8)

        # Step 2: Simplify - REPLACE previous (eq_step1 disappears!)
        eq_step2 = MathTex(r"gh = \frac{1}{2}v^2 + \frac{1}{5}v^2", font_size=32)
        eq_step2.move_to(ORIGIN)
        if eq_step2.get_right()[0] > 6.5:
            eq_step2.scale_to_fit_width(12)
        self.play(ReplacementTransform(eq_step1, eq_step2), run_time=1.2)
        self.wait(0.8)

        # Step 3: Combine fractions - REPLACE again (eq_step2 disappears!)
        eq_step3 = MathTex(r"gh = \frac{7}{10}v^2", font_size=36)
        eq_step3.move_to(ORIGIN)
        self.play(ReplacementTransform(eq_step2, eq_step3), run_time=1.2)
        self.wait(0.8)

        # Step 4: Solve for v - REPLACE one more time (eq_step3 disappears!)
        eq_step4 = MathTex(r"v = \sqrt{\frac{10gh}{7}}", font_size=38, color=GREEN)
        eq_step4.move_to(ORIGIN)
        self.play(ReplacementTransform(eq_step3, eq_step4), run_time=1.2)
        self.wait(1.5)

        # At this point, ONLY eq_step4 is visible - perfectly clean!

        # ============================================================
        # PART 5: NUMERICAL RESULT with emphasis (8 seconds)
        # ============================================================

        # EXAMPLE: Clear screen before showing emphasized result
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)
        self.wait(0.3)

        # Show final answer with background emphasis
        final_answer = MathTex(r"v = 6.26 \text{ m/s}", font_size=48, color=GREEN)
        final_answer.move_to(ORIGIN)

        # Answer box with background
        answer_box = SurroundingRectangle(
            final_answer,
            color=GREEN,
            buff=0.3,
            corner_radius=0.2,
            stroke_width=5
        )

        # BOUNDARY CHECK: Center elements should always fit
        answer_group = VGroup(answer_box, final_answer)
        if answer_group.get_right()[0] > 6.5:
            answer_group.scale_to_fit_width(12)

        self.play(
            Create(answer_box),
            Write(final_answer),
            run_time=1.8
        )
        self.wait(1.0)

        # Pulse emphasis (subtle animation)
        self.play(
            answer_box.animate.set_stroke(width=7),
            final_answer.animate.scale(1.08),
            run_time=0.5
        )
        self.play(
            answer_box.animate.set_stroke(width=5),
            final_answer.animate.scale(1/1.08),
            run_time=0.5
        )

        self.wait(2)

        # ============================================================
        # PART 6: CONCLUSION (5 seconds)
        # ============================================================

        self.play(
            FadeOut(energy_title),
            FadeOut(substituted),
            FadeOut(numerical),
            FadeOut(answer_box),
            final_answer.animate.move_to(ORIGIN),
            run_time=1.5
        )

        self.wait(2)
        self.play(FadeOut(final_answer), run_time=1)


# To render: manim -qh enhanced_sample_manim.py PhysicsSolution
