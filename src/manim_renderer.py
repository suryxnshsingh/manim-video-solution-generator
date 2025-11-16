import subprocess
from pathlib import Path


async def render_manim_video(manim_file: str, class_name: str, output_path: str, timeout: int = 600) -> str:
    """
    Render Manim animation to video file

    Args:
        manim_file: Path to the .py file containing Manim code
        class_name: Name of the Scene class to render
        output_path: Desired output path for video
        timeout: Maximum time to wait for rendering (seconds)

    Returns:
        Path to rendered video file
    """
    print(f"   Rendering {class_name} animation...")
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
            class_name  # Scene class name
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
