import subprocess
from pathlib import Path


def get_video_duration(video_path: str) -> float:
    """Get duration of video file using ffprobe"""
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = float(result.stdout.strip())
        return duration

    except subprocess.CalledProcessError as e:
        print(f"Error getting video duration: {e}")
        return 0.0
    except ValueError as e:
        print(f"Error parsing video duration: {e}")
        return 0.0


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
        print(f"Error parsing audio duration: {e}")
        return 0.0


def handle_timing_mismatch(video_duration: float, audio_duration: float) -> str:
    """
    Determine how to handle timing mismatch between video and audio

    Returns:
        "proceed" - timing is acceptable, proceed with sync
        "adjust" - timing has small mismatch, adjust during sync
        "regenerate" - timing has large mismatch, regeneration recommended
    """
    diff = abs(video_duration - audio_duration)

    if diff < 1.0:  # Less than 1 second - acceptable
        return "proceed"
    elif diff < 5.0:  # 1-5 seconds - warn and adjust
        print(f"   ⚠️  Timing mismatch: {diff:.1f}s difference")
        print(f"   Video: {video_duration:.1f}s, Audio: {audio_duration:.1f}s")
        print(f"   Proceeding with adjustment...")
        return "adjust"
    else:  # > 5 seconds - regenerate
        print(f"   ❌ Large timing mismatch: {diff:.1f}s")
        print(f"   Video: {video_duration:.1f}s, Audio: {audio_duration:.1f}s")
        print(f"   Consider regenerating the solution")
        return "regenerate"


def sync_audio_video(video_path: str, audio_path: str, output_path: str) -> str:
    """
    Synchronize audio and video using FFmpeg

    Strategy:
    1. If audio is longer than video: extend last frame of video to match audio duration
    2. If video is longer than audio: trim video to audio duration
    3. Ensure output has proper codecs and quality

    Args:
        video_path: Path to video file (no audio)
        audio_path: Path to audio file
        output_path: Path for final synchronized video

    Returns:
        Path to final video file
    """
    print(f"   Checking video and audio durations...")

    video_duration = get_video_duration(video_path)
    audio_duration = get_audio_duration(audio_path)

    print(f"   Video duration: {video_duration:.2f}s")
    print(f"   Audio duration: {audio_duration:.2f}s")

    # Check timing mismatch
    timing_status = handle_timing_mismatch(video_duration, audio_duration)

    if timing_status == "regenerate":
        print(f"   Warning: Large timing mismatch detected")
        print(f"   Continuing anyway, but results may not be optimal")

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    print(f"   Merging audio and video with FFmpeg...")

    try:
        # Determine which stream is longer and adjust strategy
        if audio_duration > video_duration:
            # Audio is longer: extend last frame of video to match audio
            print(f"   Audio is longer - extending video last frame by {audio_duration - video_duration:.2f}s")

            # Use tpad filter to extend last frame
            # tpad=stop_duration extends the last frame
            cmd = [
                "ffmpeg",
                "-y",  # Overwrite output file if exists
                "-i", video_path,
                "-i", audio_path,
                "-filter_complex",
                f"[0:v]tpad=stop_mode=clone:stop_duration={audio_duration - video_duration:.3f}[v]",
                "-map", "[v]",
                "-map", "1:a",
                "-c:v", "libx264",  # Re-encode video
                "-preset", "medium",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",  # Use shortest stream (should be equal now)
                output_path
            ]
        else:
            # Video is longer or equal: use video duration
            print(f"   Video duration matches or exceeds audio - proceeding normally")
            cmd = [
                "ffmpeg",
                "-y",  # Overwrite output file if exists
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",  # Use shortest stream
                output_path
            ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        print(f"   ✅ Video synchronized successfully!")
        print(f"   Output: {output_path}")

        return output_path

    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error synchronizing video and audio:")
        print(f"   {e.stderr}")
        raise Exception(f"FFmpeg synchronization failed: {e.stderr}")


def validate_output_video(video_path: str) -> bool:
    """Validate that output video exists and has both video and audio streams"""
    try:
        # Check if file exists
        if not Path(video_path).exists():
            print(f"   Output video does not exist: {video_path}")
            return False

        # Check for video and audio streams
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "stream=codec_type",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        streams = result.stdout.strip().split('\n')

        has_video = "video" in streams
        has_audio = "audio" in streams

        if not has_video:
            print(f"   Output video missing video stream")
            return False

        if not has_audio:
            print(f"   Output video missing audio stream")
            return False

        print(f"   ✅ Output video validated (has video and audio)")
        return True

    except subprocess.CalledProcessError as e:
        print(f"   Error validating output video: {e}")
        return False
