from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class AnimationScene(BaseModel):
    """Represents a distinct animation scene with precise timing"""
    scene_id: str  # e.g., "intro", "setup", "motion", "concept", "solve_1", "answer"
    scene_type: str  # "intro", "setup", "visualization", "concept", "math", "answer"
    start_time: float
    end_time: float
    duration: float
    description: str
    visual_elements: List[str] = []
    equations: List[str] = []


class SolutionStep(BaseModel):
    step_number: int
    title: str
    explanation: str
    equations: List[str] = []
    key_visual_elements: List[str] = []
    duration_seconds: float = Field(ge=5, le=20)
    # Scene-level breakdown for precise timing
    scenes: List[AnimationScene] = []


class QuestionAnalysis(BaseModel):
    topic: str
    subtopic: Optional[str] = None
    difficulty: str
    concepts: List[str]
    prerequisite_knowledge: List[str] = []


class SolutionSteps(BaseModel):
    question: str
    analysis: QuestionAnalysis
    steps: List[SolutionStep]
    total_duration: float = Field(ge=80, le=180)
    # Complete scene timeline for synchronization
    scene_timeline: List[AnimationScene] = []

    @property
    def estimated_duration(self) -> float:
        return sum(step.duration_seconds for step in self.steps)

    def build_scene_timeline(self) -> List[AnimationScene]:
        """Build complete timeline from steps if not already set"""
        if self.scene_timeline:
            return self.scene_timeline

        timeline = []
        current_time = 0.0

        # Add intro scene (5% of total)
        intro_duration = self.total_duration * 0.05
        timeline.append(AnimationScene(
            scene_id="intro",
            scene_type="intro",
            start_time=0.0,
            end_time=intro_duration,
            duration=intro_duration,
            description="Title and introduction",
            visual_elements=["title"],
            equations=[]
        ))
        current_time = intro_duration

        # Process each step and its scenes
        for step in self.steps:
            if step.scenes:
                for scene in step.scenes:
                    timeline.append(scene)
                    current_time = scene.end_time
            else:
                # Create default scene from step
                scene = AnimationScene(
                    scene_id=f"step_{step.step_number}",
                    scene_type="math" if step.equations else "concept",
                    start_time=current_time,
                    end_time=current_time + step.duration_seconds,
                    duration=step.duration_seconds,
                    description=step.title,
                    visual_elements=step.key_visual_elements,
                    equations=step.equations
                )
                timeline.append(scene)
                current_time += step.duration_seconds

        self.scene_timeline = timeline
        return timeline


class ScriptSegment(BaseModel):
    start_time: float
    end_time: float
    text: str
    scene_id: str


class VoiceoverScript(BaseModel):
    full_script: str
    segments: List[ScriptSegment]
    total_duration: float

    def validate_timing(self) -> bool:
        """Ensure segments don't overlap and cover full duration"""
        if not self.segments:
            return False

        for i in range(len(self.segments) - 1):
            if self.segments[i].end_time > self.segments[i + 1].start_time:
                return False

        last_segment = self.segments[-1]
        return abs(last_segment.end_time - self.total_duration) < 1.0


class ManimCode(BaseModel):
    code: str
    class_name: str = "PhysicsSolution"
    estimated_duration: float

    def save_to_file(self, filepath: str):
        with open(filepath, 'w') as f:
            f.write(self.code)


class VideoOutput(BaseModel):
    question: str
    video_path: str
    duration: float
    generated_at: str
    metadata: dict
