import os
import json
from openai import OpenAI
from src.models import SolutionSteps, VoiceoverScript, ScriptSegment


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


SYSTEM_PROMPT = """You are an expert educational content writer creating Hinglish voiceover scripts for Indian students.

CRITICAL: Write in HINGLISH - a natural mix of Hindi and English that Indian students speak daily.

Language Style (Hinglish):
- Mix Hindi and English naturally, as Indians speak in real life
- Use Hindi for common words: "toh" (so), "kya" (what), "aur" (and), "ab" (now), "yeh" (this), "hai" (is)
- Use English for technical terms: velocity, acceleration, energy, force, equation
- Use Hindi connectors: "matlab" (means), "toh" (so/then), "kyunki" (because), "agar" (if)
- Use Hindi filler words: "dekho" (see/look), "samjho" (understand), "chalo" (let's), "theek hai" (okay)

Examples of GOOD Hinglish:
✅ "Chalo, ek ball rolling problem solve karte hain."
✅ "Toh yahaan height hai 3 meters, aur angle 30 degrees."
✅ "Ab dekho, energy conservation ka concept use karenge."
✅ "Matlab PE convert hoti hai KE mein, samjhe?"
✅ "Final velocity nikalta hai 6.5 meters per second."

Examples of BAD (pure English - AVOID):
❌ "Let's solve a ball rolling problem."
❌ "So here the height is 3 meters and angle is 30 degrees."
❌ "Now see, we'll use the concept of energy conservation."

Requirements:
1. Use conversational, friendly Hinglish tone (like a tutor explaining to an Indian student)
2. Mix Hindi and English naturally - DON'T write pure English
3. CRITICAL: Match exact timing requirements - KEEP SCRIPTS CONCISE!
4. Speaking rate: Assume ~2.5 words per second for Hinglish narration
5. Calculate: For a 10-second segment, write MAX 25 words (including Hindi/English)
6. Use Hindi transitions: "toh ab" (so now), "dekho" (see), "iske baad" (after this)
7. Explain concepts clearly but BRIEFLY in Hinglish
8. For equations, mix: "v squared equals" → "v squared ka value hai"
9. Use common Hindi phrases: "yeh samajh mein aaya?" (understood?), "bilkul" (exactly)
10. BREVITY IS CRITICAL - shorter scripts fit better with animation timing!

Style guidelines:
- Start with Hinglish hook: "Chalo solve karte hain...", "Aaj hum dekhenge...", "Toh is problem mein..."
- Use phrases like: "Ab dekho yeh important hai...", "Notice karo...", "Yeh batata hai ki..."
- End with summary: "Toh humne dekha ki...", "Matlab final answer hai..."
- Equations: "v squared equals v naught squared plus 2 a d" → "v square ka value hai v naught square plus 2 a d"

Tone: Friendly, encouraging, like Physics Wallah or Unacademy teachers - casual Hinglish!

Output JSON structure:
{
    "full_script": "complete script as one string",
    "segments": [
        {
            "start_time": 0.0,
            "end_time": 5.0,
            "text": "segment text",
            "scene_id": "intro"
        }
    ],
    "total_duration": 75.0
}"""


async def generate_voiceover_script(solution: SolutionSteps) -> VoiceoverScript:
    """Generate natural voiceover script with timestamps synced to animation scenes"""

    # Build scene timeline if not already done
    timeline = solution.build_scene_timeline()

    # Format scenes for the prompt
    scenes_text = []
    for scene in timeline:
        scenes_text.append(f"""
Scene: {scene.scene_id} ({scene.scene_type})
Start: {scene.start_time:.2f}s
End: {scene.end_time:.2f}s
Duration: {scene.duration:.2f}s
Description: {scene.description}
Visual elements: {', '.join(scene.visual_elements) if scene.visual_elements else 'None'}
Equations: {', '.join(scene.equations) if scene.equations else 'None'}
""")

    user_prompt = f"""Create a HINGLISH voiceover script for this physics/math solution:

Topic: {solution.analysis.topic}
Difficulty: {solution.analysis.difficulty}
Total Duration: {solution.total_duration} seconds
Question: {solution.question}

CRITICAL: Match narration to these EXACT scene timings:
{''.join(scenes_text)}

Requirements:
- Write in HINGLISH (Hindi + English mix) - NOT pure English!
- Create ONE segment for EACH scene above
- Each segment MUST match the exact start/end times of its scene
- CRITICAL: KEEP SCRIPTS CONCISE! Speaking rate ~2.5 words/second
- For 10s scene → write MAX 25 words. For 5s scene → MAX 12 words
- Calculate words carefully: segment duration × 2.5 = max word count
- Narration must fit precisely within the scene duration
- Use Hindi connectors: toh, aur, ab, dekho, matlab, kyunki
- Use English for technical terms: velocity, energy, force, acceleration
- Make it engaging like Physics Wallah or Unacademy teachers - but BRIEF!

Example segment structures (HINGLISH):
{{
  "start_time": 0.0,
  "end_time": 3.75,
  "text": "Chalo, aaj hum solve karenge ek ball rolling problem inclined plane par.",
  "scene_id": "intro"
}}

{{
  "start_time": 3.75,
  "end_time": 12.0,
  "text": "Toh dekho, yahaan height hai 3 meters, angle 30 degrees, aur ball starts from rest. Matlab v naught equals zero hai.",
  "scene_id": "setup"
}}

{{
  "start_time": 21.0,
  "end_time": 34.2,
  "text": "Ab energy conservation ka concept use karenge. Initial mein PE hai, final mein kinetic energy. Toh m g h equals half m v squared plus half I omega squared.",
  "scene_id": "concept"
}}

Return ONLY valid JSON with full_script (concatenated Hinglish text) and segments array (one per scene)."""

    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )

    script_data = json.loads(response.choices[0].message.content)

    return VoiceoverScript(**script_data)


def validate_timing(script: VoiceoverScript, expected_duration: float) -> bool:
    """Validate that script timing matches expected duration"""
    if not script.validate_timing():
        return False

    # Check if total duration is within acceptable range
    diff = abs(script.total_duration - expected_duration)
    return diff < 5.0  # Allow 5 second tolerance
