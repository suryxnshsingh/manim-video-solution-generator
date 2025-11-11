# AI-Powered Video Solution Generator

Automatically generate educational physics/math videos with synchronized Manim animations and AI voiceover.

## Overview

This POC system takes a physics or math question as input and automatically generates a 60-120 second educational video with:
- Step-by-step animated solutions using Manim
- Natural AI voiceover explaining each step
- Perfect synchronization between visuals and narration

## Architecture

```
Input: Text question
    ↓
[1] Solution Generation (GPT-5)
    ↓
[2] Voiceover Script Generation (GPT-5)
    ↓
[3] TTS Audio Generation (OpenAI TTS)
    ↓
[4] Manim Animation Code Generation (GPT-5)
    ↓
[5] Manim Video Rendering
    ↓
[6] Audio-Video Synchronization (FFmpeg)
    ↓
Output: Final MP4 video
```

## Tech Stack

- **Python 3.11**
- **OpenAI API** (GPT-5 for generation, TTS-1-HD for voiceover)
- **Manim Community Edition** (mathematical animations)
- **FFmpeg** (video/audio processing)
- **Docker** (containerized environment)
- **Pydantic** (data validation)

## Quick Start

### Prerequisites

1. Docker and Docker Compose installed
2. OpenAI API key

### Setup

1. Clone the repository and navigate to it:
```bash
cd manim-video
```

2. Create `.env` file with your OpenAI API key:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

3. Build the Docker container:
```bash
docker-compose build
```

### Running the Generator

Generate a video from the default physics question:
```bash
docker-compose run --rm manim-video-generator python main.py
```

The final video will be saved in `output/final/`

### Customizing the Question

Edit `main.py` and modify the `question` variable (around line 130):

```python
question = """
Your physics or math question here...
"""
```

Then run the generator again.

## Project Structure

```
manim-video/
├── src/
│   ├── models.py              # Pydantic data models
│   ├── solution_generator.py  # GPT-5 solution generation
│   ├── script_generator.py    # Voiceover script generation
│   ├── tts_generator.py       # OpenAI TTS integration
│   ├── manim_generator.py     # Manim code generation
│   └── video_synchronizer.py  # FFmpeg audio/video sync
├── examples/
│   └── sample_manim.py        # Template for Manim code
├── output/
│   ├── solutions/             # Generated solution JSON
│   ├── scripts/               # Voiceover scripts
│   ├── audio/                 # TTS audio files
│   ├── manim_code/            # Generated Manim code
│   ├── videos/                # Rendered animations (no audio)
│   └── final/                 # Final synchronized videos
├── main.py                    # Main orchestrator
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose setup
└── requirements.txt           # Python dependencies
```

## Example Questions

### Rolling Ball (Rotational Motion)
```
A solid sphere of mass 2 kg and radius 0.5 m rolls without slipping down
an inclined plane that makes an angle of 30° with the horizontal.
The sphere starts from rest at a height of 3 m above the ground.
Find the linear velocity of the sphere when it reaches the bottom of the incline.
```

### Projectile Motion
```
A ball is thrown horizontally from a cliff 45m high with initial velocity
20 m/s. Find: (a) time to hit the ground, (b) horizontal distance traveled,
(c) final velocity magnitude and direction.
```

### Simple Harmonic Motion
```
A mass of 0.5 kg is attached to a spring with spring constant k = 200 N/m.
If the mass is displaced 0.1 m from equilibrium and released, find the
period of oscillation and maximum velocity.
```

## How It Works

### Step 1: Solution Generation
GPT-5 analyzes the question and breaks it down into 4-7 clear steps, each optimized for video explanation (8-15 seconds per step).

### Step 2: Script Generation
GPT-5 creates a natural, conversational voiceover script with precise timestamps matching each solution step.

### Step 3: TTS Generation
OpenAI's TTS-1-HD model (voice: "nova") generates high-quality audio narration from the script.

### Step 4: Manim Code Generation
GPT-5 generates complete Manim Community Edition code that creates animations synchronized with the solution steps.

### Step 5: Manim Rendering
The generated code is executed to render a high-quality (1080p60) video with mathematical animations.

### Step 6: Synchronization
FFmpeg combines the Manim video with the TTS audio, ensuring perfect synchronization.

## Output

Each run generates:
- **Final video** (`output/final/final_TIMESTAMP.mp4`) - The complete educational video
- **Solution JSON** (`output/solutions/solution_TIMESTAMP.json`) - Structured solution data
- **Script JSON** (`output/scripts/script_TIMESTAMP.json`) - Voiceover script with timestamps
- **Manim code** (`output/manim_code/animation_TIMESTAMP.py`) - Generated animation code
- **Intermediate files** - Raw video and audio before synchronization

## Cost Estimation

Per 90-second video:
- GPT-5 calls (~6000 tokens output): ~$0.20
- TTS-1-HD (~500 characters): ~$0.02
- **Total: ~$0.22 per video**

## Development

### Running Without Docker

If you prefer to run locally without Docker:

```bash
# Install system dependencies (macOS)
brew install ffmpeg

# Install LaTeX (for Manim)
brew install --cask mactex

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Run
python main.py
```

### Testing Manim Code

To test the sample Manim animation:

```bash
# Inside the container
docker-compose run --rm manim-video-generator manim -pql examples/sample_manim.py PhysicsSolution

# Or locally
manim -pql examples/sample_manim.py PhysicsSolution
```

## Troubleshooting

### Timing Mismatch
If the video and audio have significantly different durations (>5 seconds), the system will warn you. This usually means the Manim code generation needs adjustment. The system will still produce output using the shortest duration.

### Manim Rendering Fails
Check `output/manim_code/animation_TIMESTAMP.py` for syntax errors. The system validates Python syntax but can't catch all Manim-specific errors.

### FFmpeg Errors
Ensure FFmpeg is properly installed in the Docker container. The Dockerfile includes FFmpeg installation.

## Future Enhancements

- [ ] Add intro/outro sequences with branding
- [ ] Improve Manim code generation with better prompting
- [ ] Add retry logic for failed generations
- [ ] Create web UI (Streamlit/Gradio)
- [ ] Batch processing for multiple questions
- [ ] Quality scoring and automatic validation
- [ ] Support for chemistry, biology, and other subjects
- [ ] Multi-language support
- [ ] Custom voice selection

## License

MIT License - feel free to use and modify for your projects.

## Credits

Built with:
- [OpenAI API](https://platform.openai.com/)
- [Manim Community Edition](https://www.manim.community/)
- [FFmpeg](https://ffmpeg.org/)
