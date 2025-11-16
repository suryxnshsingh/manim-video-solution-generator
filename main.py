import asyncio
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from src.solution_generator import generate_solution_steps
from src.manim_generator_intro import generate_intro_manim_code_with_retry
from src.manim_generator_solution import generate_solution_manim_code_with_retry
from src.manim_renderer import render_manim_video
from src.script_generator import generate_voiceover_script, validate_timing
from src.tts_generator import generate_tts_audio
from src.video_synchronizer import sync_audio_video, validate_output_video
from src.video_joiner import join_videos, validate_joined_video
from src.models import VideoOutput


load_dotenv()


class VideoSolutionGenerator:
    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.setup_directories()

    def setup_directories(self):
        """Create output directory structure"""
        dirs = ["solutions", "manim_code", "scripts", "videos", "audio", "final"]
        for dir_name in dirs:
            (self.output_dir / dir_name).mkdir(parents=True, exist_ok=True)

    async def generate(self, question: str) -> VideoOutput:
        """
        Main pipeline to generate video solution using two-agent approach

        Steps:
        1. Analyze question and generate solution steps
        2. Generate voiceover script with timestamps
        3. Generate TTS audio
        4. Generate Manim animation code (TWO PARTS):
           - Part 1: Introduction & Problem Setup
           - Part 2: Solution & Answer
        5. Render both Manim videos
        6. Join the two videos
        7. Synchronize audio and final video
        """
        print(f"\n{'=' * 80}")
        print(f"🚀 AI Video Solution Generator (Two-Agent System)")
        print(f"{'=' * 80}\n")
        print(f"Question:\n{question}\n")
        print(f"{'=' * 80}\n")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Step 1: Generate solution
        print(f"📝 Step 1/7: Analyzing question and generating solution...")
        print(f"{'-' * 80}")
        solution = await generate_solution_steps(question)
        solution_path = self.output_dir / "solutions" / f"solution_{timestamp}.json"
        solution_path.write_text(solution.model_dump_json(indent=2))
        print(f"✅ Solution generated!")
        print(f"   Topic: {solution.analysis.topic}")
        print(f"   Difficulty: {solution.analysis.difficulty}")
        print(f"   Steps: {len(solution.steps)}")
        print(f"   Estimated duration: {solution.total_duration}s")
        print(f"   Saved to: {solution_path}")
        print()

        # Step 2: Generate voiceover script
        print(f"🎙️  Step 2/7: Generating voiceover script...")
        print(f"{'-' * 80}")
        script = await generate_voiceover_script(solution)
        script_path = self.output_dir / "scripts" / f"script_{timestamp}.json"
        script_path.write_text(script.model_dump_json(indent=2))

        # Validate timing
        if not validate_timing(script, solution.total_duration):
            print(f"   ⚠️  Warning: Script timing validation failed")
            print(f"   Script duration: {script.total_duration}s")
            print(f"   Expected duration: {solution.total_duration}s")

        print(f"✅ Script generated!")
        print(f"   Segments: {len(script.segments)}")
        print(f"   Duration: {script.total_duration}s")
        print(f"   Script length: {len(script.full_script)} characters")
        print(f"   Saved to: {script_path}")
        print()

        # Step 3: Generate TTS audio
        print(f"🔊 Step 3/7: Generating AI voiceover...")
        print(f"{'-' * 80}")
        audio_path = await generate_tts_audio(
            script,
            str(self.output_dir / "audio" / f"audio_{timestamp}.mp3")
        )
        print(f"✅ Audio generated!")
        print()

        # Step 4a: Generate intro/setup Manim code
        print(f"🎨 Step 4a/7: Generating intro/setup animation (Agent 1)...")
        print(f"{'-' * 80}")
        intro_manim_code = await generate_intro_manim_code_with_retry(solution, script)
        intro_manim_file = self.output_dir / "manim_code" / f"animation_intro_{timestamp}.py"
        intro_manim_code.save_to_file(str(intro_manim_file))
        print(f"✅ Intro Manim code generated!")
        print(f"   Code length: {len(intro_manim_code.code)} characters")
        print(f"   Estimated duration: {intro_manim_code.estimated_duration:.2f}s")
        print(f"   Saved to: {intro_manim_file}")
        print()

        # Step 4b: Generate solution Manim code
        print(f"🎨 Step 4b/7: Generating solution animation (Agent 2)...")
        print(f"{'-' * 80}")
        solution_manim_code = await generate_solution_manim_code_with_retry(solution, script)
        solution_manim_file = self.output_dir / "manim_code" / f"animation_solution_{timestamp}.py"
        solution_manim_code.save_to_file(str(solution_manim_file))
        print(f"✅ Solution Manim code generated!")
        print(f"   Code length: {len(solution_manim_code.code)} characters")
        print(f"   Estimated duration: {solution_manim_code.estimated_duration:.2f}s")
        print(f"   Saved to: {solution_manim_file}")
        print()

        # Step 5a: Render intro video
        print(f"🎬 Step 5a/7: Rendering intro/setup animation...")
        print(f"{'-' * 80}")
        print(f"   This may take several minutes...")
        intro_video_path = await render_manim_video(
            str(intro_manim_file),
            intro_manim_code.class_name,
            str(self.output_dir / "videos" / f"video_intro_{timestamp}.mp4")
        )

        if not intro_video_path or not Path(intro_video_path).exists():
            raise Exception("Intro Manim rendering failed - no video output")

        print(f"✅ Intro video rendered!")
        print(f"   Video path: {intro_video_path}")
        print()

        # Step 5b: Render solution video
        print(f"🎬 Step 5b/7: Rendering solution animation...")
        print(f"{'-' * 80}")
        print(f"   This may take several minutes...")
        solution_video_path = await render_manim_video(
            str(solution_manim_file),
            solution_manim_code.class_name,
            str(self.output_dir / "videos" / f"video_solution_{timestamp}.mp4")
        )

        if not solution_video_path or not Path(solution_video_path).exists():
            raise Exception("Solution Manim rendering failed - no video output")

        print(f"✅ Solution video rendered!")
        print(f"   Video path: {solution_video_path}")
        print()

        # Step 6: Join the two videos
        print(f"🔗 Step 6/7: Joining intro and solution videos...")
        print(f"{'-' * 80}")
        joined_video_path = str(self.output_dir / "videos" / f"video_joined_{timestamp}.mp4")
        joined_video = join_videos(intro_video_path, solution_video_path, joined_video_path)

        if not joined_video or not validate_joined_video(joined_video):
            raise Exception("Video joining failed")

        print(f"✅ Videos joined successfully!")
        print(f"   Joined video path: {joined_video}")
        print()

        # Step 7: Sync audio and video
        print(f"🎵 Step 7/7: Synchronizing audio and video...")
        print(f"{'-' * 80}")
        final_path = str(self.output_dir / "final" / f"final_{timestamp}.mp4")
        final_video = sync_audio_video(joined_video, audio_path, final_path)

        # Validate output
        if not validate_output_video(final_video):
            raise Exception("Output video validation failed")

        print()

        # Create output object
        output = VideoOutput(
            question=question,
            video_path=final_video,
            duration=solution.total_duration,
            generated_at=datetime.now().isoformat(),
            metadata={
                "topic": solution.analysis.topic,
                "subtopic": solution.analysis.subtopic,
                "difficulty": solution.analysis.difficulty,
                "steps": len(solution.steps),
                "concepts": solution.analysis.concepts,
            }
        )

        print(f"\n{'=' * 80}")
        print(f"🎉 SUCCESS! Video solution generated!")
        print(f"{'=' * 80}\n")
        print(f"📊 Video Details:")
        print(f"   Topic: {output.metadata['topic']}")
        print(f"   Difficulty: {output.metadata['difficulty']}")
        print(f"   Duration: {output.duration:.1f} seconds")
        print(f"   Steps: {output.metadata['steps']}")
        print(f"   Concepts: {', '.join(output.metadata['concepts'][:3])}...")
        print(f"\n📁 Output Files:")
        print(f"   Final Video: {output.video_path}")
        print(f"   Solution: {solution_path}")
        print(f"   Script: {script_path}")
        print(f"   Intro Manim Code: {intro_manim_file}")
        print(f"   Solution Manim Code: {solution_manim_file}")
        print(f"\n🎥 Video Parts:")
        print(f"   Part 1 (Intro): {intro_video_path}")
        print(f"   Part 2 (Solution): {solution_video_path}")
        print(f"   Joined Video: {joined_video}")
        print(f"\n{'=' * 80}\n")

        return output


async def main():
    """Main entry point for the video generator"""

    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment")
        print("Please create a .env file with: OPENAI_API_KEY=your_key_here")
        print("Or set the environment variable before running")
        exit(1)

    # Example physics question - Rolling ball on inclined plane
    question = """
A solid sphere of mass 2 kg and radius 0.5 m rolls without slipping down
an inclined plane that makes an angle of 30° with the horizontal.
The sphere starts from rest at a height of 3 m above the ground.
Find the linear velocity of the sphere when it reaches the bottom of the incline.
    """.strip()

    # Alternative questions for testing:

    # Projectile Motion
    # question = """
    # A ball is thrown horizontally from a cliff 45m high with initial velocity
    # 20 m/s. Find: (a) time to hit the ground, (b) horizontal distance traveled,
    # (c) final velocity magnitude and direction.
    # """

    # Simple Harmonic Motion
    # question = """
    # A mass of 0.5 kg is attached to a spring with spring constant k = 200 N/m.
    # If the mass is displaced 0.1 m from equilibrium and released, find the
    # period of oscillation and maximum velocity.
    # """

    generator = VideoSolutionGenerator()

    try:
        output = await generator.generate(question)
        print(f"✅ Video generation complete!")
        print(f"   Watch your video at: {output.video_path}")

    except Exception as e:
        print(f"\n❌ Error during video generation:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
