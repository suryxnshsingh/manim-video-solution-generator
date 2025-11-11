#!/usr/bin/env python3
"""
Test script to verify the setup and dependencies
Run this before attempting to generate videos
"""

import sys
import os
from pathlib import Path


def test_imports():
    """Test that all required Python packages are installed"""
    print("Testing Python package imports...")

    try:
        import openai
        print("  ✅ openai")
    except ImportError:
        print("  ❌ openai - run: pip install openai")
        return False

    try:
        import manim
        print("  ✅ manim")
    except ImportError:
        print("  ❌ manim - run: pip install manim")
        return False

    try:
        import pydantic
        print("  ✅ pydantic")
    except ImportError:
        print("  ❌ pydantic - run: pip install pydantic")
        return False

    try:
        from dotenv import load_dotenv
        print("  ✅ python-dotenv")
    except ImportError:
        print("  ❌ python-dotenv - run: pip install python-dotenv")
        return False

    return True


def test_env_file():
    """Test that .env file exists and has API key"""
    print("\nTesting environment configuration...")

    if not Path(".env").exists():
        print("  ❌ .env file not found")
        print("     Create one with: cp .env.example .env")
        return False

    print("  ✅ .env file exists")

    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("  ❌ OPENAI_API_KEY not set in .env")
        return False

    if not api_key.startswith("sk-"):
        print("  ⚠️  OPENAI_API_KEY doesn't look valid (should start with 'sk-')")
        return False

    print("  ✅ OPENAI_API_KEY is set")
    return True


def test_ffmpeg():
    """Test that FFmpeg is installed"""
    print("\nTesting FFmpeg installation...")
    import subprocess

    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            check=True
        )
        version_line = result.stdout.split('\n')[0]
        print(f"  ✅ FFmpeg installed: {version_line}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  ❌ FFmpeg not found")
        print("     Install with: brew install ffmpeg (macOS) or apt-get install ffmpeg (Linux)")
        return False


def test_directories():
    """Test that output directories can be created"""
    print("\nTesting directory structure...")

    output_dir = Path("output")
    subdirs = ["solutions", "manim_code", "scripts", "videos", "audio", "final"]

    try:
        for subdir in subdirs:
            (output_dir / subdir).mkdir(parents=True, exist_ok=True)
        print("  ✅ Output directories created")
        return True
    except Exception as e:
        print(f"  ❌ Failed to create directories: {e}")
        return False


def test_openai_api():
    """Test OpenAI API connection"""
    print("\nTesting OpenAI API connection...")

    try:
        from openai import OpenAI
        from dotenv import load_dotenv

        load_dotenv()
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Make a minimal API call
        response = client.chat.completions.create(
            model="gpt-5-mini",  # Use cheaper model for testing
            messages=[{"role": "user", "content": "Say 'test successful'"}],
            max_tokens=10
        )

        if response.choices[0].message.content:
            print("  ✅ OpenAI API connection successful")
            return True
        else:
            print("  ❌ OpenAI API returned empty response")
            return False

    except Exception as e:
        print(f"  ❌ OpenAI API test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 80)
    print("AI Video Solution Generator - Setup Test")
    print("=" * 80)
    print()

    tests = [
        ("Python Packages", test_imports),
        ("Environment File", test_env_file),
        ("FFmpeg", test_ffmpeg),
        ("Directories", test_directories),
        ("OpenAI API", test_openai_api),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ Test crashed: {e}")
            results.append((test_name, False))
        print()

    # Summary
    print("=" * 80)
    print("Test Summary")
    print("=" * 80)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    all_passed = all(result for _, result in results)

    print()
    if all_passed:
        print("🎉 All tests passed! You're ready to generate videos.")
        print("Run: ./run.sh or docker-compose run --rm manim-video-generator python main.py")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
