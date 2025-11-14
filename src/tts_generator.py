import os
import subprocess
from pathlib import Path
from openai import OpenAI
from src.models import VoiceoverScript


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def generate_tts_audio(script: VoiceoverScript, output_path: str) -> str:
    """
    Generate text-to-speech audio using OpenAI TTS API

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
    print(f"   Script length: {len(script.full_script)} characters")
    print(f"   Voice: nova (Hinglish educational)")

    response = client.audio.speech.create(
        model="tts-1-hd",  # Higher quality model
        voice="nova",      # Best for Hinglish educational content
        input=script.full_script,
        speed=1.0          # Normal speed
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
