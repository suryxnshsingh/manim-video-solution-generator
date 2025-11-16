import os
import json
from openai import OpenAI
from src.models import QuestionAnalysis, SolutionStep, SolutionSteps, AnimationScene


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


SYSTEM_PROMPT = """You are an expert physics and mathematics tutor. Given a problem, generate a VERY DETAILED step-by-step solution optimized for video explanation.

Requirements:
1. Break solution into 8-15 VERY GRANULAR steps (more is better!)
2. Each step should take 6-12 seconds to explain (account for narration time!)
3. CRITICAL: Show EVERY intermediate calculation step:
   - Write the formula
   - Substitute values
   - Simplify algebraically (show each simplification)
   - Calculate final number
4. Include ALL relevant equations in LaTeX format for each step
5. Each equation transformation should be its own step
6. Identify key visual elements that should be animated
7. Keep total duration between 100-150 seconds (longer to match actual speech duration!)
8. Output as structured JSON

EXAMPLE of granular breakdown for v = √(2gh):
Step 1: State energy conservation principle (equation)
Step 2: Expand energy conservation (mgh = ½mv²)
Step 3: Cancel mass from both sides (gh = ½v²)
Step 4: Rearrange for v² (v² = 2gh)
Step 5: Take square root (v = √(2gh))
Step 6: Substitute values (v = √(2 × 9.8 × 3))
Step 7: Simplify inside root (v = √(58.8))
Step 8: Calculate final answer (v = 7.67 m/s)

THIS IS 8 STEPS for a simple formula - make sure your solutions are similarly detailed!

Output JSON structure:
{
    "analysis": {
        "topic": "string",
        "subtopic": "string or null",
        "difficulty": "beginner|intermediate|advanced",
        "concepts": ["array of concept strings"],
        "prerequisite_knowledge": ["array of prerequisite strings"]
    },
    "steps": [
        {
            "step_number": 1,
            "title": "Step title",
            "explanation": "Detailed explanation of this step - be verbose and educational!",
            "equations": ["latex equation 1", "latex equation 2"],
            "key_visual_elements": ["element 1", "element 2"],
            "duration_seconds": 8
        }
    ],
    "total_duration": 95
}"""


async def analyze_question(question: str) -> QuestionAnalysis:
    """Analyze the question to extract topic, difficulty, and concepts"""
    user_prompt = f"""Analyze this physics/math question and identify:
- The main topic and subtopic
- Difficulty level
- Key concepts involved
- Prerequisite knowledge needed

Question: {question}

Provide response as JSON with keys: topic, subtopic, difficulty, concepts, prerequisite_knowledge"""

    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "You are an expert at analyzing physics and math problems."},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )

    analysis_data = json.loads(response.choices[0].message.content)
    return QuestionAnalysis(**analysis_data)


async def generate_solution_steps(question: str) -> SolutionSteps:
    """Generate complete solution with steps optimized for video"""

    user_prompt = f"""Generate a VERY DETAILED, video-optimized solution for this problem:

{question}

Create a GRANULAR step-by-step solution that:
- Takes 100-150 seconds total to explain (account for narration speaking time!)
- Has 8-15 DETAILED steps (break down every calculation!)
- Each step has 6-12 second duration
- CRITICAL: Show EVERY intermediate calculation:
  * Formula statement
  * Value substitution
  * Algebraic simplification (each step separately!)
  * Numerical calculation
- Includes ALL relevant LaTeX equations for EACH transformation
- Identifies visual elements to animate (e.g., "inclined plane", "force vectors", "ball", "energy bars")
- Has engaging, verbose explanations suitable for educational voiceover

IMPORTANT: If a solution involves v = √(2gh), that should be at least 6-8 steps showing:
1. Energy principle statement
2. Energy equation expansion
3. Simplification (cancel terms)
4. Rearrange for target variable
5. Substitute numerical values
6. Simplify calculation
7. Final numerical answer

Return ONLY valid JSON matching the required structure."""

    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )

    solution_data = json.loads(response.choices[0].message.content)

    # Add the original question to the solution
    solution_data['question'] = question

    solution = SolutionSteps(**solution_data)

    # Generate detailed scene timeline for synchronization
    solution = await generate_scene_timeline(solution)

    return solution


async def generate_scene_timeline(solution: SolutionSteps) -> SolutionSteps:
    """Generate detailed scene-by-scene timeline with precise timestamps"""

    # Calculate target durations for each part (based on 3B1B structure)
    total = solution.total_duration
    intro_duration = total * 0.05  # 5%
    setup_duration = total * 0.15  # 15%
    motion_duration = total * 0.15  # 15%
    concept_duration = total * 0.22  # 22%
    solution_duration = total * 0.28  # 28%
    answer_duration = total * 0.15  # 15%

    timeline = []
    current_time = 0.0

    # 1. Intro scene
    timeline.append(AnimationScene(
        scene_id="intro",
        scene_type="intro",
        start_time=current_time,
        end_time=current_time + intro_duration,
        duration=intro_duration,
        description="Title and problem statement",
        visual_elements=["title"],
        equations=[]
    ))
    current_time += intro_duration

    # 2. Setup scene
    setup_visuals = solution.steps[0].key_visual_elements if solution.steps else []
    timeline.append(AnimationScene(
        scene_id="setup",
        scene_type="setup",
        start_time=current_time,
        end_time=current_time + setup_duration,
        duration=setup_duration,
        description="Build the physical scenario",
        visual_elements=setup_visuals + ["given_info_box"],
        equations=[]
    ))
    current_time += setup_duration

    # 3. Motion visualization scene
    timeline.append(AnimationScene(
        scene_id="motion",
        scene_type="visualization",
        start_time=current_time,
        end_time=current_time + motion_duration,
        duration=motion_duration,
        description="Animate the actual motion",
        visual_elements=["dynamic_motion", "velocity_arrow", "what_we_find"],
        equations=[]
    ))
    current_time += motion_duration

    # 4. Concept scene
    concept_equations = []
    for step in solution.steps:
        if any(keyword in step.title.lower() for keyword in ['energy', 'conservation', 'principle', 'concept']):
            concept_equations.extend(step.equations[:2])  # First 2 equations
            break

    timeline.append(AnimationScene(
        scene_id="concept",
        scene_type="concept",
        start_time=current_time,
        end_time=current_time + concept_duration,
        duration=concept_duration,
        description=f"Show governing principle: {solution.analysis.concepts[0] if solution.analysis.concepts else 'key concept'}",
        visual_elements=["energy_diagram"] if "energy" in solution.analysis.concepts[0].lower() else ["force_diagram"],
        equations=concept_equations
    ))
    current_time += concept_duration

    # 5. Solution scenes (split into sub-scenes for each major step)
    remaining_steps = [s for s in solution.steps if s.equations]  # Steps with equations
    if remaining_steps:
        time_per_solve_step = solution_duration / len(remaining_steps)
        for i, step in enumerate(remaining_steps):
            timeline.append(AnimationScene(
                scene_id=f"solve_{i+1}",
                scene_type="math",
                start_time=current_time,
                end_time=current_time + time_per_solve_step,
                duration=time_per_solve_step,
                description=step.title,
                visual_elements=[],
                equations=step.equations
            ))
            current_time += time_per_solve_step
    else:
        # Fallback if no equation steps
        timeline.append(AnimationScene(
            scene_id="solve",
            scene_type="math",
            start_time=current_time,
            end_time=current_time + solution_duration,
            duration=solution_duration,
            description="Mathematical solution",
            visual_elements=[],
            equations=[]
        ))
        current_time += solution_duration

    # 6. Answer scene
    final_equations = []
    for step in reversed(solution.steps):
        if step.equations:
            final_equations = step.equations[-2:]  # Last 2 equations
            break

    timeline.append(AnimationScene(
        scene_id="answer",
        scene_type="answer",
        start_time=current_time,
        end_time=current_time + answer_duration,
        duration=answer_duration,
        description="Present final answer with emphasis",
        visual_elements=["answer_box", "final_value"],
        equations=final_equations
    ))

    # Update solution with timeline
    solution.scene_timeline = timeline
    return solution
