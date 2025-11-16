import subprocess
from pathlib import Path


def join_videos(intro_video_path: str, solution_video_path: str, output_path: str) -> str:
    """
    Join two videos into one using FFmpeg

    Args:
        intro_video_path: Path to intro/setup video
        solution_video_path: Path to solution video
        output_path: Path for joined output video

    Returns:
        Path to joined video file
    """
    print(f"   Joining intro and solution videos...")

    try:
        # Create output directory
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Create a temporary file list for FFmpeg concat demuxer
        list_file = Path(output_path).parent / "video_list.txt"

        # Write file list
        with open(list_file, 'w') as f:
            f.write(f"file '{Path(intro_video_path).absolute()}'\n")
            f.write(f"file '{Path(solution_video_path).absolute()}'\n")

        # Use FFmpeg concat demuxer for lossless joining
        # This is the fastest and most reliable method for same-format videos
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_file),
            "-c", "copy",  # Copy codec (no re-encoding, fast!)
            "-y",  # Overwrite output file
            output_path
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        # Clean up temp file
        list_file.unlink()

        print(f"   Videos joined successfully: {output_path}")
        return output_path

    except subprocess.CalledProcessError as e:
        print(f"   Error joining videos:")
        print(f"   {e.stderr}")
        return ""
    except Exception as e:
        print(f"   Unexpected error during video joining: {e}")
        return ""


def validate_joined_video(video_path: str) -> bool:
    """Validate that the joined video exists and is playable"""
    if not Path(video_path).exists():
        print(f"   Error: Joined video not found at {video_path}")
        return False

    try:
        # Use ffprobe to check video
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = float(result.stdout.strip())

        if duration > 0:
            print(f"   ✅ Joined video validated! Duration: {duration:.2f}s")
            return True
        else:
            print(f"   Error: Joined video has zero duration")
            return False

    except Exception as e:
        print(f"   Error validating joined video: {e}")
        return False
