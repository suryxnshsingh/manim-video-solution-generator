# Quick Start Guide

Get your first AI-generated educational video in 3 steps!

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Setup (2 minutes)

1. **Add your OpenAI API key:**
```bash
cp .env.example .env
```

Edit `.env` and add your key:
```
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

2. **Build the Docker container:**
```bash
docker-compose build
```

This will take 3-5 minutes the first time (downloads dependencies).

## Generate Your First Video (5-10 minutes)

**Option 1: Use the run script (easiest)**
```bash
./run.sh
```

**Option 2: Use docker-compose directly**
```bash
docker-compose run --rm manim-video-generator python main.py
```

The script will:
1. ✅ Analyze the physics question (rolling ball problem)
2. ✅ Generate step-by-step solution
3. ✅ Create voiceover script
4. ✅ Generate TTS audio
5. ✅ Generate Manim animation code
6. ✅ Render high-quality video
7. ✅ Sync audio and video

**Your video will be saved to:** `output/final/final_TIMESTAMP.mp4`

## Try Different Questions

Edit `main.py` and change the `question` variable (line ~130):

```python
question = """
A ball is thrown upward with initial velocity 20 m/s.
Find the maximum height reached and time to return to ground.
"""
```

Then run again:
```bash
./run.sh
```

## What Gets Generated

Each run creates:
```
output/
├── final/final_20241102_143022.mp4      ← Your video! 🎥
├── solutions/solution_*.json            ← Structured solution
├── scripts/script_*.json                ← Voiceover script
├── manim_code/animation_*.py            ← Animation code
├── videos/video_*.mp4                   ← Video (no audio)
└── audio/audio_*.mp3                    ← TTS audio
```

## Troubleshooting

### "OPENAI_API_KEY not found"
- Make sure `.env` file exists
- Check that your API key starts with `sk-proj-` or `sk-`

### "Docker not found"
Install Docker Desktop: https://www.docker.com/products/docker-desktop/

### "Build failed"
```bash
# Try rebuilding without cache
docker-compose build --no-cache
```

### Test your setup
```bash
docker-compose run --rm manim-video-generator python test_setup.py
```

## Cost

Each video costs approximately **$0.20-0.25** in OpenAI API credits.

## Next Steps

1. ✅ Read [USAGE.md](USAGE.md) for detailed usage instructions
2. ✅ Read [README.md](README.md) for technical details
3. ✅ Try the example questions in USAGE.md
4. ✅ Customize the pipeline for your needs

## Example Output

The default question generates a ~90 second video that:
- Shows an animated inclined plane with a rolling sphere
- Displays equations step-by-step in LaTeX
- Has synchronized AI voiceover explaining each step
- Ends with the final answer highlighted

Perfect for educational content, tutorials, or learning! 🎓

---

**Need help?** Check USAGE.md or README.md for detailed documentation.
