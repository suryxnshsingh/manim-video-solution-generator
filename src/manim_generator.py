import os
import json
import subprocess
import ast
from pathlib import Path
from openai import OpenAI
from src.models import SolutionSteps, ManimCode


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Load sample Manim code for few-shot learning
ENHANCED_SAMPLE_PATH = Path(__file__).parent.parent / "examples" / "enhanced_sample_manim.py"
BASIC_SAMPLE_PATH = Path(__file__).parent.parent / "examples" / "sample_manim.py"


def load_sample_manim() -> str:
    """Load the enhanced sample Manim code as reference"""
    # Try enhanced sample first
    try:
        with open(ENHANCED_SAMPLE_PATH, 'r') as f:
            return f.read()
    except FileNotFoundError:
        # Fallback to basic sample
        try:
            with open(BASIC_SAMPLE_PATH, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return ""


SYSTEM_PROMPT = """You are a master Manim animator creating 3Blue1Brown-quality educational physics animations.

🎯 CORE PHILOSOPHY: VISUAL STORYTELLING
Your animations should SHOW, not just display. Every element should serve the narrative.

📖 NARRATIVE STRUCTURE (Critical - follow this flow):

1. VISUAL SETUP (15-20% of duration) - PROFESSIONAL DIAGRAMS
   - Start with elegant, engaging title (gradient colors, smooth fade)
   - Build physical scenario with CLEAN, PROFESSIONAL diagrams:
     * Use proper geometry: accurate angles, proportional dimensions
     * Add coordinate axes (X-Y axes with arrows, labels) when relevant
     * Use dashed lines for reference/construction lines (DashedLine, GRAY_B)
     * Show measurements with proper brackets/braces (Brace with labels)
     * Add dimension arrows (DoubleArrow) for distances/heights
     * Use consistent stroke widths: main objects (6-8), annotations (2-3)
   - Create visual hierarchy:
     * Main objects: bold, saturated colors (BLUE_D, RED_E)
     * Reference lines: lighter, dashed (GRAY_B, stroke_opacity=0.6)
     * Labels: clear font (24-28), proper positioning with buff
   - Add "Given" box in corner with:
     * Professional border (SurroundingRectangle, rounded corners)
     * Organized list with consistent spacing (buff=0.2)
     * Clear title "Given" above box

2. PROBLEM VISUALIZATION (15-20% of duration) - DYNAMIC STORYTELLING
   - ANIMATE the actual motion/scenario with realistic physics:
     * Ball rolling: use MoveAlongPath with rotate animation
     * Projectile: show parabolic path with velocity vectors
     * Use rate_func=smooth for natural motion
   - Show what we're finding:
     * Highlight unknown with question mark in box/circle
     * Use arrow pointing to quantity we need to find
     * Add "Find: v = ?" with prominent styling
   - Add visual cues for engagement:
     * Motion blur trails (fading opacity copies)
     * Velocity/acceleration vectors that update during motion
     * Show forces acting on object (arrows with labels)
     * Use UpdateFromFunc or always_redraw for dynamic elements

3. CONCEPTUAL APPROACH (20-25% of duration) - VISUAL PRINCIPLES
   - Transition to analysis:
     * Fade out physical setup smoothly
     * Keep ONE key element as visual anchor
     * Clear the board before showing principle
   - Show governing principle with VISUAL DIAGRAMS:
     * Energy Conservation: show energy bar charts or flow diagrams
     * Forces: show free body diagram with proper force vectors
     * Use icons/visual metaphors (not just text)
     * Add small illustrations alongside equations
   - Build equations WITH VISUAL CONTEXT:
     * Show where each term comes from (small diagram/label)
     * Use color coding: initial (YELLOW), final (GREEN), constant (BLUE)
     * Add small reference diagrams next to equation terms
     * Use arrows showing energy/force relationships
   - Professional diagram elements:
     * Energy bars: Rectangle with gradient fills
     * Flow arrows: thick arrows showing energy transfer
     * Proper spacing and alignment

4. MATHEMATICAL SOLUTION (25-30% of duration) - STEP-BY-STEP CLEAN PROGRESSION

   🚨 THIS IS THE MOST IMPORTANT PART - SHOW EVERY CALCULATION STEP!

   STEP-BY-STEP means showing EACH intermediate calculation:
   - Start with formula
   - Substitute values (show substitution)
   - Simplify step by step (show each simplification)
   - Final calculation with number

   Example for v = √(2gh):
   Step 1: v = √(2gh)                    ← Formula
   Step 2: v = √(2 × 9.8 × 3)           ← Substitute values
   Step 3: v = √(58.8)                   ← Simplify
   Step 4: v = 7.67 m/s                  ← Final answer

   SHOW ALL 4 STEPS with ReplacementTransform between each!

   Guidelines:
   - Use ReplacementTransform for clean equation flow (NO OVERLAP!)
   - Show step-by-step with clear visual logic:
     * Highlight the term being substituted (change color to YELLOW)
     * Show substitution source (small reference equation in corner)
     * Fade out reference after use
   - Use visual grouping:
     * SurroundingRectangle around key steps (corner_radius=0.15)
     * Arrows showing which terms combine
     * Color-code like terms before combining
   - Keep it clean:
     * One main equation at center at a time
     * Small reference equations in corners if needed (font_size=24-28)
     * REMOVE old content before showing next step (ReplacementTransform)

   CRITICAL: Don't skip calculation steps! Show the math progression clearly!

5. FINAL ANSWER (10-15% of duration) - EMPHASIS & CONTEXT
   - Clear everything for final answer (fade out all previous content)
   - Present result with STRONG EMPHASIS:
     * Large font size (48-56)
     * Bright GREEN color
     * Professional box (SurroundingRectangle, corner_radius=0.2)
     * Subtle pulse animation (scale 1.0 → 1.08 → 1.0)
   - Add context if useful:
     * Small text below: "This means..." interpretation
     * Quick comparison (e.g., "≈ 23 mph")
     * Brief visual reminder of scenario
   - Clean ending:
     * Hold for 1-2 seconds
     * Smooth fade out all elements

🎨 VISUAL QUALITY GUIDELINES:

Colors (professional palette):
- Primary objects: BLUE_D, BLUE_C (darker/lighter shades)
- Focus/moving objects: RED_E with WHITE shine circle
- Energy/abstract: YELLOW, ORANGE (use for PE, heat)
- Final answers: GREEN (bright - #00FF00 or GREEN_A)
- Annotations: WHITE, GRAY_A (lighter for secondary info)
- Reference lines: GRAY_B, GRAY_C (dashed, low opacity)
- Use set_color_by_gradient(BLUE, TEAL) for titles

Professional Diagram Elements:
- Coordinate axes: NumberPlane or custom axes with Arrow tips
- Dimension indicators: Brace with MathTex labels (not just Text)
- Reference lines: DashedLine with stroke_width=2, stroke_opacity=0.6
- Measurement arrows: DoubleArrow with labels in the middle
- Info boxes: SurroundingRectangle with corner_radius=0.15-0.2
- Shine effects on spheres: small WHITE circle (radius*0.3, fill_opacity=0.8)
- Force vectors: Arrow with stroke_width=5-6, clear labels

Advanced Techniques for Professional Look:
- VGroup for organizing related elements (keep diagrams together)
- Updaters for dynamic elements:
  * always_redraw() for vectors that follow motion
  * add_updater() for continuous rotation/following
- Rate functions for natural motion:
  * rate_func=smooth (most animations)
  * rate_func=there_and_back (oscillations)
  * rate_func=linear (constant velocity motion)
- Gradient fills: Rectangle with set_fill(color=[BLUE, CYAN], opacity=0.7)
- Layering: Create background first, then main objects, then annotations

Animation Polish (CRITICAL for professionalism):
- NEVER Write() or FadeIn() everything at once
- Build scenes in logical order:
  1. Background/reference lines (ground, axes)
  2. Main physical objects (ball, plane, etc.)
  3. Measurements and dimensions (braces, arrows)
  4. Labels and annotations (text, values)
- Use directional animations:
  * FadeIn(obj, shift=DOWN) - slide from top
  * FadeOut(obj, shift=UP) - slide upward
  * Create() for lines/paths (draws from start to end)
  * GrowFromCenter() for symmetric objects
- Vary timing for rhythm:
  * Quick: simple labels (0.5-0.8s)
  * Medium: equations, objects (1.0-1.5s)
  * Slow: complex diagrams (2.0-2.5s)
- Use emphasis animations:
  * .animate.scale(1.2) then scale(1/1.2) for pulse
  * .animate.set_color(YELLOW) to highlight
  * Indicate() for quick attention draw

🚨 CRITICAL ANIMATION REQUIREMENT:
- EVERY self.play() call MUST include explicit run_time parameter
- Example: self.play(obj.animate.scale(0.5), run_time=1.0)
- NEVER write: self.play(obj.animate.scale(0.5))  # WRONG - missing run_time
- Default run_time should be 0.5-2.0 seconds depending on complexity
- For multiple animations: self.play(anim1, anim2, run_time=1.5)
- Even simple animations need run_time: self.play(FadeIn(text), run_time=0.8)

🚨 MANIM COMMUNITY EDITION API (CRITICAL - Use correct syntax):

⚠️⚠️⚠️ NEVER USE stretch=True PARAMETER - IT DOESN'T EXIST! ⚠️⚠️⚠️

The methods set_width() and set_height() DO NOT accept a 'stretch' parameter!
This will cause: TypeError: got an unexpected keyword argument 'stretch'

ABSOLUTELY WRONG (WILL CRASH):
❌ obj.set_width(3, stretch=True)  # CRASH! 'stretch' parameter doesn't exist!
❌ obj.set_height(2, stretch=True)  # CRASH! 'stretch' parameter doesn't exist!
❌ obj.set_width(3, stretch=True, about_point=ORIGIN)  # CRASH!
❌ obj.animate.set_width(2.5, stretch=True)  # CRASH!

CORRECT alternatives for resizing:

For stretching (non-proportional):
✅ obj.stretch_to_fit_width(3)   # Stretch to width 3
✅ obj.stretch_to_fit_height(2)  # Stretch to height 2
✅ obj.stretch(2, 0)             # Stretch by factor 2 in X dimension (width)
✅ obj.stretch(2, 1)             # Stretch by factor 2 in Y dimension (height)

For proportional scaling:
✅ obj.scale_to_fit_width(3)     # Scale proportionally to fit width
✅ obj.scale_to_fit_height(2)    # Scale proportionally to fit height
✅ obj.scale(0.5)                # Scale by factor 0.5

CONCRETE EXAMPLES (energy bar resizing):

WRONG:
❌ pot_bar.animate.set_width(0.0, stretch=True, about_point=...)  # CRASH!
❌ kin_bar.animate.set_width(2.5, stretch=True, about_point=...)  # CRASH!

CORRECT:
✅ pot_bar.animate.stretch_to_fit_width(0.1)  # Shrink bar
✅ kin_bar.animate.stretch_to_fit_width(2.5)  # Grow bar
✅ pot_bar.animate.stretch(0.1, 0)           # Stretch in X dimension
✅ kin_bar.animate.scale(2.0)                # Scale proportionally

Common methods:
- .move_to(position) - move center to position
- .next_to(obj, direction, buff=0.5) - position relative to another object
- .to_edge(edge, buff=0.5) - move to screen edge (UP, DOWN, LEFT, RIGHT, UL, UR, DL, DR)
- .shift(vector) - shift by vector (UP, DOWN, LEFT, RIGHT, or custom)
- .rotate(angle) - rotate by angle in radians (use PI for 180°)
- .set_color(color) - change color
- .set_opacity(value) - change opacity (0-1) for EXISTING objects

⚠️⚠️⚠️ OPACITY IN CONSTRUCTORS - CRITICAL! ⚠️⚠️⚠️

When CREATING objects, there is NO 'opacity' parameter!
Use stroke_opacity and fill_opacity instead.

ABSOLUTELY WRONG (WILL CRASH):
❌ Line(start, end, color=RED, opacity=0)  # CRASH! 'opacity' doesn't exist in __init__
❌ Circle(radius=1, color=BLUE, opacity=0.5)  # CRASH!
❌ Rectangle(width=2, height=1, opacity=0.3)  # CRASH!
❌ Arrow(start, end, opacity=0.8)  # CRASH!

CORRECT (use stroke_opacity and/or fill_opacity):
✅ Line(start, end, color=RED, stroke_opacity=0)  # Invisible line
✅ Circle(radius=1, color=BLUE, fill_opacity=0.5, stroke_opacity=1)  # Semi-transparent fill
✅ Rectangle(width=2, height=1, fill_opacity=0.3)  # Transparent rectangle
✅ Arrow(start, end, stroke_opacity=0.8)  # Semi-transparent arrow
✅ path = Line(start, end, color=RED); path.set_opacity(0)  # Create then set opacity

For shapes with fills (Circle, Rectangle, etc.):
- stroke_opacity: opacity of the outline/border
- fill_opacity: opacity of the inside fill

For lines/curves (Line, Arrow, etc.):
- stroke_opacity: opacity of the line itself

Text & Math:
- Titles: font_size=40-44, weight=BOLD, gradients
- Main equations (single): font_size=36-40
- Step-by-step equations: font_size=28-32 (SMALLER for readability)
- Labels: font_size=24-28
- Use \\text{} for units in MathTex
- TransformMatchingTex for equation evolution

🚨 TEXT OVERLAP PREVENTION (CRITICAL):

NEVER OVERLAP TEXT - This looks messy and unprofessional!

⚠️⚠️⚠️ CRITICAL: REMOVE OLD TEXT BEFORE SHOWING NEW TEXT! ⚠️⚠️⚠️

DO NOT WRITE TEXT ON TOP OF OTHER TEXT - IT LOOKS TERRIBLE!

🚨 MANDATORY TEXT REPLACEMENT RULES:

1. NEVER USE Transform() OR TransformMatchingTex() - THEY CREATE MESSY LAYERS!
   Transform() keeps the original object and layers new visuals on top.
   This creates an UGLY MESS with text stacked on each other!

2. ABSOLUTELY WRONG (creates layers - DO NOT USE):
   ❌ self.play(Transform(eq1, eq2), run_time=1.0)  # eq1 stays, eq2 layers on top! HORRIBLE!
   ❌ self.play(TransformMatchingTex(eq1, eq2), run_time=1.0)  # Same issue! MESSY!
   ❌ Writing new equation without removing old one  # OVERLAPPING TEXT!

3. ALWAYS CORRECT (clean replacement - MUST USE):
   ✅ self.play(ReplacementTransform(eq1, eq2), run_time=1.0)  # eq1 REMOVED, eq2 shown cleanly
   ✅ self.play(FadeOut(eq1), run_time=0.6); self.wait(0.2); self.play(Write(eq2), run_time=1.0)
   ✅ self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)  # Clear ALL before new

4. BEFORE SHOWING NEW EQUATION, ALWAYS:
   Option A: Use ReplacementTransform (old equation morphs into new)
   Option B: FadeOut old equation, wait briefly, then Write new equation
   Option C: Clear entire screen with FadeOut all mobjects, then show new

🚨 ESPECIALLY FOR CALCULATION STEPS (solve scenes):
   Step 1: Show equation → REMOVE IT
   Step 2: Show substitution → REMOVE IT
   Step 3: Show simplification → REMOVE IT
   Step 4: Show final answer

   NEVER have multiple equations visible unless intentionally stacking them vertically!

Example of CORRECT sequential replacement:
```python
# Step 1
eq1 = MathTex("E_i = E_f", font_size=32).move_to(ORIGIN)
self.play(Write(eq1), run_time=1.2)
self.wait(1.0)

# Step 2 - REMOVE eq1 first!
eq2 = MathTex("mgh = \\frac{1}{2}mv^2", font_size=32).move_to(ORIGIN)
self.play(ReplacementTransform(eq1, eq2), run_time=1.2)  # eq1 disappears!
self.wait(1.0)

# Step 3 - REMOVE eq2 first!
eq3 = MathTex("v = \\sqrt{2gh}", font_size=32).move_to(ORIGIN)
self.play(ReplacementTransform(eq2, eq3), run_time=1.2)  # eq2 disappears!
self.wait(1.0)

# Only eq3 visible now - CLEAN!
```

STEP-BY-STEP SOLUTION DISPLAY:

Method 1: Clean sequential replacement (PREFERRED for solve scenes):
   ```python
   # Step 1: Starting equation
   eq1 = MathTex("v^2 = v_0^2 + 2ad", font_size=32)
   eq1.move_to(ORIGIN)
   self.play(Write(eq1), run_time=1.2)
   self.wait(0.8)

   # Step 2: Substitute values - REPLACE previous equation
   eq2 = MathTex("v^2 = 0 + 2(5)(10)", font_size=32)
   eq2.move_to(ORIGIN)
   self.play(ReplacementTransform(eq1, eq2), run_time=1.2)  # eq1 disappears!
   self.wait(0.8)

   # Step 3: Simplify - REPLACE again
   eq3 = MathTex("v^2 = 100", font_size=32)
   eq3.move_to(ORIGIN)
   self.play(ReplacementTransform(eq2, eq3), run_time=1.2)  # eq2 disappears!
   self.wait(0.8)

   # Step 4: Final answer - REPLACE one more time
   eq4 = MathTex("v = 10\\text{ m/s}", font_size=36, color=GREEN)
   eq4.move_to(ORIGIN)
   self.play(ReplacementTransform(eq3, eq4), run_time=1.2)  # eq3 disappears!
   self.wait(1.0)

   # At this point, only eq4 is visible - NO OVERLAP!
   ```

Method 2: Stack equations vertically (ALTERNATIVE - when you want to show all steps together):
   ```python
   # Only use this if you want ALL steps visible at once
   # Not recommended for long calculations (use Method 1 instead)

   eq1 = MathTex("v^2 = v_0^2 + 2ad", font_size=28)
   eq2 = MathTex("v^2 = 0 + 2(5)(10)", font_size=28)
   eq3 = MathTex("v^2 = 100", font_size=28)
   eq4 = MathTex("v = 10\\text{ m/s}", font_size=28, color=GREEN)

   # Pre-arrange all equations
   equations = VGroup(eq1, eq2, eq3, eq4)
   equations.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
   equations.move_to(ORIGIN)

   # Check bounds after positioning
   if equations.get_bottom()[1] < -3.5:
       equations.scale_to_fit_height(6.5)

   # Show one by one (they stack below each other)
   self.play(Write(eq1), run_time=1.0)
   self.wait(0.6)
   self.play(Write(eq2), run_time=1.0)
   self.wait(0.6)
   self.play(Write(eq3), run_time=1.0)
   self.wait(0.6)
   self.play(Write(eq4), run_time=1.0)
   self.wait(1.0)
   ```

3. For center emphasis with background (clean method):
   ```python
   # Clear everything first
   self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)

   # Show emphasized equation
   final_answer = MathTex("v = 10\\text{ m/s}", font_size=48, color=GREEN)
   bg_rect = SurroundingRectangle(final_answer, buff=0.3, color=GREEN, corner_radius=0.2)

   answer_group = VGroup(bg_rect, final_answer).move_to(ORIGIN)
   self.play(Create(bg_rect), Write(final_answer), run_time=1.5)
   ```

4. Background overlay (when keeping previous content):
   ```python
   # Fade background to 30% opacity
   self.play(*[mob.animate.set_opacity(0.3) for mob in old_elements], run_time=0.6)

   # Show new equation with background
   new_eq = MathTex("...", font_size=40)
   bg = SurroundingRectangle(new_eq, buff=0.4, fill_color=BLACK, fill_opacity=0.9, color=BLUE)

   VGroup(bg, new_eq).move_to(ORIGIN)
   self.play(FadeIn(bg), Write(new_eq), run_time=1.2)
   ```

GENERAL RULES:
- Use smaller font (28-32) for multi-step solutions
- Stack vertically with buff=0.3-0.4
- ALWAYS clear or fade old content before showing large centered text
- Use background rectangles for overlays
- Check bounds after EVERY positioning operation

📐 PROFESSIONAL DIAGRAM CONSTRUCTION PATTERNS:

Pattern 1: Inclined Plane Setup (with proper measurements)
```python
# Ground reference
ground = Line(LEFT * 6, RIGHT * 6, color=GRAY_B, stroke_width=3)
ground.to_edge(DOWN, buff=0.8)

# Inclined plane with proper angle
plane_top = LEFT * 4 + UP * 2
plane_bottom = RIGHT * 4 + DOWN * 1
plane = Line(plane_top, plane_bottom, color=BLUE_D, stroke_width=7)

# Height measurement with Brace
height_line = DashedLine(plane_top, plane_top + DOWN * 3, color=YELLOW, stroke_width=2, stroke_opacity=0.7)
height_brace = Brace(height_line, direction=LEFT, color=YELLOW)
height_label = MathTex("h = 3\\,\\text{m}", font_size=30, color=YELLOW)
height_label.next_to(height_brace, LEFT, buff=0.2)

# Angle indicator with Arc
angle = np.arctan(3/8)  # Calculate actual angle
angle_arc = Arc(radius=0.7, start_angle=0, angle=-angle, color=ORANGE, arc_center=plane_top)
angle_label = MathTex("30^\\circ", font_size=28, color=ORANGE)
angle_label.next_to(angle_arc, RIGHT + DOWN * 0.2, buff=0.2)

# Animate in order
self.play(Create(ground), run_time=0.8)
self.play(Create(plane), run_time=1.0)
self.play(Create(height_line), GrowFromCenter(height_brace), Write(height_label), run_time=1.2)
self.play(Create(angle_arc), Write(angle_label), run_time=0.9)
```

Pattern 2: Force/Vector Diagram (professional arrows)
```python
# Object at center
obj = Circle(radius=0.4, color=RED_E, fill_opacity=1)
obj.move_to(ORIGIN)

# Force vectors with proper labels
gravity = Arrow(obj.get_center(), obj.get_center() + DOWN * 1.5,
                color=YELLOW, stroke_width=6, buff=0)
normal = Arrow(obj.get_center(), obj.get_center() + UP * 1.2,
               color=GREEN, stroke_width=6, buff=0)
friction = Arrow(obj.get_center(), obj.get_center() + LEFT * 1.0,
                 color=RED, stroke_width=6, buff=0)

# Labels positioned properly
g_label = MathTex("\\vec{F}_g", font_size=32, color=YELLOW)
g_label.next_to(gravity, RIGHT, buff=0.2)
n_label = MathTex("\\vec{N}", font_size=32, color=GREEN)
n_label.next_to(normal, RIGHT, buff=0.2)
f_label = MathTex("\\vec{f}", font_size=32, color=RED)
f_label.next_to(friction, DOWN, buff=0.2)

# Animate with staging
self.play(FadeIn(obj, scale=0.5), run_time=0.8)
self.wait(0.3)
self.play(GrowArrow(gravity), Write(g_label), run_time=1.0)
self.play(GrowArrow(normal), Write(n_label), run_time=1.0)
self.play(GrowArrow(friction), Write(f_label), run_time=1.0)
```

Pattern 3: Energy Bar Chart (visual comparison)
```python
# Baseline for bars
baseline = Line(LEFT * 3, RIGHT * 3, color=GRAY_B, stroke_width=2)
baseline.shift(DOWN * 1.5)

# Energy bars with labels
pe_bar = Rectangle(width=0.8, height=2.5, fill_color=YELLOW, fill_opacity=0.8, stroke_width=2)
ke_bar = Rectangle(width=0.8, height=1.8, fill_color=GREEN, fill_opacity=0.8, stroke_width=2)

# Position bars on baseline (bottom aligned)
pe_bar.next_to(baseline.get_left() + RIGHT * 1, UP, buff=0)
ke_bar.next_to(baseline.get_right() + LEFT * 1, UP, buff=0)

# Labels below bars
pe_label = Text("PE", font_size=28, color=YELLOW).next_to(pe_bar, DOWN, buff=0.3)
ke_label = Text("KE", font_size=28, color=GREEN).next_to(ke_bar, DOWN, buff=0.3)

# Value labels on bars
pe_value = MathTex("mgh", font_size=26).move_to(pe_bar.get_center())
ke_value = MathTex("\\frac{1}{2}mv^2", font_size=24).move_to(ke_bar.get_center())

# Flow arrow between bars
flow_arrow = Arrow(pe_bar.get_right(), ke_bar.get_left(), color=WHITE, stroke_width=4)

# Animate construction
self.play(Create(baseline), run_time=0.6)
self.play(FadeIn(pe_bar, shift=UP * 0.3), FadeIn(ke_bar, shift=UP * 0.3), run_time=1.0)
self.play(Write(pe_label), Write(ke_label), run_time=0.8)
self.play(Write(pe_value), Write(ke_value), run_time=1.0)
self.play(GrowArrow(flow_arrow), run_time=0.8)
```

🚨 VISUAL BOUNDARIES (CRITICAL - Prevent Overflow):

STRICT BOUNDARY ENFORCEMENT:
- Screen safe zone: X ∈ [-6.5, 6.5], Y ∈ [-3.5, 3.5]
- NEVER allow any element to exceed these bounds
- After creating ANY text/equation, IMMEDIATELY check and fix bounds:

  ```python
  # Check and fix horizontal bounds
  if eq.get_right()[0] > 6.5:
      eq.scale_to_fit_width(13)
  if eq.get_left()[0] < -6.5:
      eq.shift(RIGHT * abs(eq.get_left()[0] + 6.5))

  # Check and fix vertical bounds
  if eq.get_top()[1] > 3.5:
      eq.shift(DOWN * abs(eq.get_top()[1] - 3.5))
  if eq.get_bottom()[1] < -3.5:
      eq.shift(UP * abs(eq.get_bottom()[1] + 3.5))
  ```

POSITIONING RULES:
- Corner boxes: .to_edge(UR, buff=0.6) - ALWAYS use buff >= 0.6
- Titles: .to_edge(UP, buff=0.8).scale_to_fit_width(13)
- Centered equations: .move_to(ORIGIN) then .scale_to_fit_width(12)
- Long equations: MUST use .scale_to_fit_width(12) or smaller
- Equation stacks: .arrange(DOWN, buff=0.25, aligned_edge=LEFT)

📦 INFO/GIVEN BOX POSITIONING (CRITICAL):
When creating boxes with borders (like "Given" info boxes):

CORRECT pattern:
```python
# 1. Create content first
items = VGroup(
    MathTex("m = 2\\,\\text{kg}", font_size=28),
    MathTex("h = 3\\,\\text{m}", font_size=28),
).arrange(DOWN, aligned_edge=LEFT, buff=0.2)

# 2. Position the content group
items.to_edge(UR, buff=0.8)

# 3. Create border AFTER positioning content
border = SurroundingRectangle(items, color=WHITE, buff=0.25, corner_radius=0.15)

# 4. NO boundary check on border! It's already positioned correctly
# 5. Optional: Add title above
title = Text("Given", font_size=24).next_to(border, UP, buff=0.15)

# 6. Group everything for animation
box_group = VGroup(border, items, title)
```

WRONG pattern:
❌ Creating border then calling ensure_bounds() on it - shifts border away from content!
❌ Positioning border separately from content - they won't align!

🎬 TIMING CRITICAL - MATCH AUDIO DURATION EXACTLY:

⚠️ The audio narration duration is LONGER than your estimated animation time!
You MUST add sufficient wait times to match the total audio duration.

Timing guidelines:
- Intro: 1-1.5s for title + WAIT time to fill scene duration
- Setup: 0.8-1.2s per element + WAIT times between (fill scene duration)
- Motion: 2-3s main animation + WAIT time to fill scene duration
- Equation writes: 1.0-1.5s each + WAIT 0.8-1.5s after each
- Transforms: 1.0-1.5s + WAIT 0.8-1.2s after
- Final answer: Hold for 2-3s minimum

CRITICAL: Add self.wait() after EVERY animation to allow narration to complete!

Example with proper waits:
```python
# Scene duration: 9.0 seconds
self.play(Create(line), run_time=1.0)  # 1s
self.wait(0.8)  # Let narration catch up
self.play(Write(label), run_time=1.0)  # 1s
self.wait(1.2)  # More narration time
self.play(FadeIn(box), run_time=1.0)  # 1s
self.wait(4.0)  # Fill remaining time = 9 - (1+0.8+1+1.2+1) = 4s
# Total: exactly 9 seconds
```

Calculate waits: If scene is 12s and animations are 5s, add 7s of self.wait() distributed throughout!

🎬 REQUIRED: SHOW ACTUAL MOTION
For physics problems, you MUST animate the actual physical motion:
- Ball rolling: Use MoveAlongPath + rotation with updater
- Projectile: Curved path with gravity
- Oscillation: Sinusoidal motion
- Collision: Impact with bounce
Make it realistic and engaging!

📐 TECHNICAL REQUIREMENTS:
- Manim Community Edition syntax only
- Class: PhysicsSolution(Scene)
- Exact timing match to solution duration
- Complete, executable code with imports
- Detailed comments for each section

Remember: You're creating a mini-documentary, not a slideshow. Every animation should feel purposeful and engaging."""


async def generate_manim_code(solution: SolutionSteps) -> ManimCode:
    """Generate Manim animation code from solution steps"""

    # Load sample code for reference
    sample_code = load_sample_manim()

    # Format solution steps for prompt
    steps_description = []
    for step in solution.steps:
        steps_description.append(f"""
Step {step.step_number}: {step.title}
Duration: {step.duration_seconds} seconds
Explanation: {step.explanation}
Equations: {step.equations}
Visual Elements: {step.key_visual_elements}
""")

    # Build narrative structure description
    narrative_guide = f"""
NARRATIVE STRUCTURE FOR THIS PROBLEM:

1. VISUAL SETUP (~{int(solution.total_duration * 0.18)}s):
   - Title: Engaging question restatement
   - Build the physical scenario: {', '.join(solution.steps[0].key_visual_elements[:3]) if solution.steps[0].key_visual_elements else 'setup scene'}
   - Show given information in organized box

2. PROBLEM VISUALIZATION (~{int(solution.total_duration * 0.18)}s):
   - ANIMATE the actual motion described in the problem
   - Make it dynamic and engaging (use MoveAlongPath, rotation, etc.)
   - Show what we're finding with arrows/labels

3. CONCEPTUAL APPROACH (~{int(solution.total_duration * 0.22)}s):
   - Transition to analysis mode
   - Show governing principle: {solution.analysis.concepts[0] if solution.analysis.concepts else 'key concept'}
   - Build foundational equations

4. MATHEMATICAL SOLUTION (~{int(solution.total_duration * 0.28)}s):
   - Step through the algebra with TransformMatchingTex
   - Show substitutions with color emphasis
   - Make each step feel motivated

5. FINAL ANSWER (~{int(solution.total_duration * 0.14)}s):
   - Present result with emphasis
   - Use highlighting, boxes, brief pulse
   - Clean fadeout
"""

    # Build timeline with precise timestamps
    timeline = solution.build_scene_timeline()
    timeline_text = []
    for scene in timeline:
        timeline_text.append(f"""
# SCENE: {scene.scene_id} ({scene.scene_type})
# Time: {scene.start_time:.2f}s - {scene.end_time:.2f}s (Duration: {scene.duration:.2f}s)
# {scene.description}
# Visuals: {', '.join(scene.visual_elements) if scene.visual_elements else 'None'}
# Equations: {', '.join(scene.equations) if scene.equations else 'None'}
""")

    user_prompt = f"""Create a 3Blue1Brown-quality Manim animation for this physics problem:

PROBLEM CONTEXT:
Topic: {solution.analysis.topic}
Difficulty: {solution.analysis.difficulty}
Total Duration: {solution.total_duration} seconds
Question: {solution.question}

KEY CONCEPTS: {', '.join(solution.analysis.concepts)}

🎬 EXACT SCENE TIMELINE (CRITICAL - Match these timestamps precisely):
{''.join(timeline_text)}

SOLUTION BREAKDOWN:
{''.join(steps_description)}

{narrative_guide}

CRITICAL REQUIREMENTS:
✓ Follow the scene timeline above with EXACT timestamps
✓ Add timing comments in your code matching the scenes
✓ MUST include actual motion animation (rolling, flying, oscillating, etc.)
✓ Prevent visual overflow - keep all elements within screen bounds
✓ Use .scale_to_fit_width(12) for long equations
✓ Position info boxes with .to_edge(UR, buff=0.5) to avoid overflow
✓ Apply 3Blue1Brown-style polish: gradients, smooth transitions, visual emphasis
✓ Total duration must be exactly {solution.total_duration} seconds
✓ Every animation should serve the story

REFERENCE CODE (study the techniques and style):
{sample_code}

Generate ONLY the complete Python code with timing comments for each scene. No markdown."""

    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
    )

    code = response.choices[0].message.content

    # Clean up code (remove markdown code blocks if present)
    if code.startswith("```python"):
        code = code.split("```python")[1]
    if code.startswith("```"):
        code = code.split("```")[1]
    if code.endswith("```"):
        code = code.rsplit("```", 1)[0]

    code = code.strip()

    return ManimCode(
        code=code,
        class_name="PhysicsSolution",
        estimated_duration=solution.total_duration
    )


def validate_manim_code(code: str) -> bool:
    """Validate that the generated Manim code has valid Python syntax"""
    try:
        ast.parse(code)
        return True
    except SyntaxError as e:
        print(f"Syntax error in generated Manim code: {e}")
        return False


async def render_manim_video(manim_file: str, output_path: str, timeout: int = 600) -> str:
    """
    Render Manim animation to video file

    Args:
        manim_file: Path to the .py file containing Manim code
        output_path: Desired output path for video
        timeout: Maximum time to wait for rendering (seconds)

    Returns:
        Path to rendered video file
    """
    print(f"   Rendering Manim animation...")
    print(f"   This may take a few minutes...")

    try:
        # Create output directory
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Manim command: -qh for high quality (1080p), --disable_caching to avoid issues
        cmd = [
            "manim",
            "-qh",  # High quality (1080p, 60fps)
            "--disable_caching",
            "-o", Path(output_path).name,  # Output filename
            manim_file,
            "PhysicsSolution"  # Scene class name
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True
        )

        # Manim outputs to media/videos/[filename]/[quality]/[output_name].mp4
        # We need to find and move it to our desired location
        # Manim outputs relative to current working directory (/app)
        import shutil

        # First try: /app/media/videos/...
        manim_output_dir = Path("/app/media/videos") / Path(manim_file).stem / "1080p60"
        rendered_file = manim_output_dir / Path(output_path).name

        # Second try: relative to manim file
        if not rendered_file.exists():
            manim_output_dir = Path(manim_file).parent / "media" / "videos" / Path(manim_file).stem / "1080p60"
            rendered_file = manim_output_dir / Path(output_path).name

        if rendered_file.exists():
            # Move to desired location
            shutil.move(str(rendered_file), output_path)
            print(f"   Manim rendering complete: {output_path}")
            return output_path
        else:
            print(f"   Error: Rendered file not found at {rendered_file}")
            print(f"   Searching in /app/media/videos/...")
            # Try to find the file
            media_dir = Path("/app/media/videos")
            if media_dir.exists():
                for mp4_file in media_dir.rglob("*.mp4"):
                    print(f"   Found: {mp4_file}")
            print(f"   Manim output: {result.stdout}")
            return ""

    except subprocess.TimeoutExpired:
        print(f"   Error: Manim rendering timed out after {timeout} seconds")
        return ""
    except subprocess.CalledProcessError as e:
        print(f"   Error rendering Manim animation:")
        print(f"   {e.stderr}")
        return ""
    except Exception as e:
        print(f"   Unexpected error during rendering: {e}")
        return ""


async def generate_manim_code_with_retry(solution: SolutionSteps, max_retries: int = 3) -> ManimCode:
    """Generate Manim code with retry logic for invalid syntax"""
    for attempt in range(max_retries):
        print(f"   Generating Manim code (attempt {attempt + 1}/{max_retries})...")

        manim_code = await generate_manim_code(solution)

        if validate_manim_code(manim_code.code):
            print(f"   Valid Manim code generated!")
            return manim_code

        print(f"   Invalid syntax in generated code, retrying...")

    raise Exception(f"Failed to generate valid Manim code after {max_retries} attempts")
