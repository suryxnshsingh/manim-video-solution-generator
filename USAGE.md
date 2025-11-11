# Usage Guide

## Quick Start

1. **Setup your environment:**
```bash
# Copy the example .env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-proj-your-key-here
```

2. **Run the generator:**
```bash
# Using the run script (recommended)
./run.sh

# Or using docker-compose directly
docker-compose run --rm manim-video-generator python main.py
```

3. **Find your video:**
```bash
# The final video will be in:
output/final/final_YYYYMMDD_HHMMSS.mp4
```

## Customizing the Question

### Option 1: Edit main.py

Open `main.py` and find the `question` variable (around line 130):

```python
question = """
Your custom physics or math question here...
"""
```

### Option 2: Create a Custom Script

Create a new Python file `custom_question.py`:

```python
import asyncio
from main import VideoSolutionGenerator

async def main():
    question = """
    Your custom question here
    """

    generator = VideoSolutionGenerator()
    output = await generator.generate(question)
    print(f"Video saved to: {output.video_path}")

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:
```bash
docker-compose run --rm manim-video-generator python custom_question.py
```

## Understanding the Pipeline

### 1. Solution Generation (30-60 seconds)
- Analyzes your question
- Breaks it into 4-7 steps
- Estimates timing for each step
- Saves: `output/solutions/solution_TIMESTAMP.json`

### 2. Script Generation (30-60 seconds)
- Creates natural voiceover script
- Adds timestamps for each segment
- Saves: `output/scripts/script_TIMESTAMP.json`

### 3. Audio Generation (10-30 seconds)
- Converts script to speech using OpenAI TTS
- Uses "nova" voice (female, energetic)
- Saves: `output/audio/audio_TIMESTAMP.mp3`

### 4. Manim Code Generation (30-60 seconds)
- Generates Python code for animations
- Based on solution steps and visual elements
- Saves: `output/manim_code/animation_TIMESTAMP.py`

### 5. Video Rendering (3-5 minutes)
- Executes Manim code to create animations
- Renders at 1080p60 quality
- Saves: `output/videos/video_TIMESTAMP.mp4`

### 6. Synchronization (10-20 seconds)
- Combines audio and video with FFmpeg
- Ensures perfect sync
- Saves: `output/final/final_TIMESTAMP.mp4`

**Total time: 5-10 minutes per video**

## Output Structure

After running, you'll have these files:

```
output/
├── final/
│   └── final_20241102_143022.mp4      # ← Your final video!
├── solutions/
│   └── solution_20241102_143022.json  # Structured solution data
├── scripts/
│   └── script_20241102_143022.json    # Voiceover script with timestamps
├── manim_code/
│   └── animation_20241102_143022.py   # Generated Manim code
├── videos/
│   └── video_20241102_143022.mp4      # Video without audio
└── audio/
    └── audio_20241102_143022.mp3      # TTS audio
```

## Example Questions

### Physics - Kinematics
```
A car accelerates from rest at 2 m/s² for 10 seconds, then maintains
constant velocity for 20 seconds. Find the total distance traveled.
```

### Physics - Forces
```
A 5 kg block sits on a frictionless incline at 45°. Find the acceleration
of the block and the normal force on the block.
```

### Physics - Energy
```
A 2 kg pendulum is released from a height of 1 m. Find its velocity at the
lowest point using conservation of energy.
```

### Math - Algebra
```
Solve the system of equations:
2x + 3y = 12
4x - y = 5
```

### Math - Calculus
```
Find the derivative of f(x) = x³ sin(2x) using the product rule.
```

## Troubleshooting

### Video and Audio Don't Match
- Check `output/solutions/solution_TIMESTAMP.json` for step durations
- Check `output/scripts/script_TIMESTAMP.json` for segment timings
- The system allows ±5 seconds tolerance
- Large mismatches will trigger a warning

### Manim Rendering Fails
- Check `output/manim_code/animation_TIMESTAMP.py` for errors
- The code is validated for Python syntax but not Manim-specific errors
- Common issues: incorrect MathTex syntax, timing calculation errors
- Try regenerating (run again)

### OpenAI API Errors
- Check your API key in `.env`
- Ensure you have credits in your OpenAI account
- Check rate limits (usually not an issue for single videos)

### Docker Issues
```bash
# Rebuild the container
docker-compose build --no-cache

# Check if container is running
docker ps -a

# View logs
docker-compose logs
```

## Advanced Configuration

### Change TTS Voice

Edit `src/tts_generator.py` line 24:

```python
voice="nova",  # Options: alloy, echo, fable, onyx, nova, shimmer
```

### Change Video Quality

Edit `src/manim_generator.py` line 115:

```python
"-qh",  # Options: -ql (480p), -qm (720p), -qh (1080p), -qk (4k)
```

Note: Higher quality = longer rendering time

### Adjust GPT Model

Edit the generator files to use different models:

```python
model="gpt-5",  # Options: gpt-5, gpt-5-mini
```

## Cost Management

Each video costs approximately **$0.20-0.25**:
- GPT-5 calls: ~$0.20
- TTS: ~$0.02

To reduce costs:
1. Use `gpt-5-mini` instead of `gpt-5` (10x cheaper, slightly lower quality)
2. Use `tts-1` instead of `tts-1-hd` (lower quality audio)
3. Generate shorter videos (60 seconds instead of 120)

## Batch Processing

To generate multiple videos:

```python
# batch_generate.py
import asyncio
from main import VideoSolutionGenerator

questions = [
    "Question 1...",
    "Question 2...",
    "Question 3...",
]

async def main():
    generator = VideoSolutionGenerator()

    for i, question in enumerate(questions, 1):
        print(f"\n{'='*80}")
        print(f"Generating video {i}/{len(questions)}")
        print(f"{'='*80}\n")

        try:
            output = await generator.generate(question)
            print(f"✅ Video {i} complete: {output.video_path}")
        except Exception as e:
            print(f"❌ Video {i} failed: {e}")
            continue

if __name__ == "__main__":
    asyncio.run(main())
```

Run:
```bash
docker-compose run --rm manim-video-generator python batch_generate.py
```

## Tips for Best Results

1. **Clear Questions**: Provide all necessary information (values, units, what to find)
2. **Appropriate Scope**: Questions that take 60-120 seconds to explain work best
3. **Visual Elements**: Questions with clear visual components (diagrams, graphs) work better
4. **Step-by-Step**: Problems that naturally break into steps produce better videos

## Next Steps

After generating your first video:
1. Review the output files to understand the pipeline
2. Try different physics/math questions
3. Adjust parameters (voice, quality, model) to your preference
4. Consider extending the code for your specific needs

Enjoy creating educational videos! 🎥✨
