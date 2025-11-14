import os
import subprocess
from pathlib import Path
from openai import OpenAI
from src.models import VoiceoverScript


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def generate_tts_audio(script: VoiceoverScript, output_path: str) -> str:
    """
    Generate text-to-speech audio using OpenAI TTS API with custom instructions

    Voice options:
    - alloy: Neutral, balanced
    - echo: Male, clear
    - fable: British accent, warm
    - onyx: Deep male voice
    - nova: Female, energetic (RECOMMENDED for Hinglish educational content)
    - shimmer: Female, soft
    - ash: New voice option
    - sage: New voice option
    - coral: New voice option
    """

    print(f"   Generating TTS audio with OpenAI...")
    print(f"   Model: gpt-4o-mini-tts (advanced TTS)")
    print(f"   Script length: {len(script.full_script)} characters")
    print(f"   Voice: nova (Hinglish educational)")

    # Custom instructions for educational Hinglish physics content
    instructions = """Accent/Affect: Warm, clear, and gently instructive, like a friendly physics teacher explaining concepts in a classroom.

Tone: Calm, encouraging, and articulate, clearly describing each step with patience and enthusiasm for learning.

Pacing: Moderate and deliberate, pausing briefly at key points to allow the listener to absorb physics concepts comfortably. Slightly slower during mathematical steps.

Emotion: Cheerful, supportive, and genuinely enthusiastic about physics; convey enjoyment and passion for teaching science.

Pronunciation: Clearly articulate physics and mathematical terminology (e.g., "velocity," "kinetic energy," "conservation") with appropriate emphasis. Handle Hinglish (Hindi-English mix) naturally, pronouncing Hindi words authentically while maintaining clarity.

Language Style: Natural Hinglish flow—seamlessly mix Hindi and English as commonly used in Indian educational settings. Use Hindi connectors like "toh," "aur," "matlab" naturally.

Personality Affect: Friendly and approachable with educational authority; speak confidently yet warmly, guiding students through physics problems step-by-step with patience and clarity. Sound like you genuinely care about the student understanding the concept."""

    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",  # Advanced TTS model with instructions support
        voice="nova",              # Best for Hinglish educational content
        input=script.full_script,
        instructions=instructions   # Custom voice characteristics
    )

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Stream to file
    response.stream_to_file(output_path)

    print(f"   Audio saved to: {output_path}")

    return output_path


def get_audio_duration(audio_path: str) -> float:
    """Get duration of audio file using ffprobe"""
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = float(result.stdout.strip())

        return duration

    except subprocess.CalledProcessError as e:
        print(f"Error getting audio duration: {e}")
        return 0.0
    except ValueError as e:
        print(f"Error parsing duration: {e}")
        return 0.0
