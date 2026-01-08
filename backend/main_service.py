import logging

from backend.input_processor import InputProcessor
from backend.prompt_enhancer import PromptEnhancer

try:
    from backend.music_generator import MusicGenerator
except Exception as e:
    MusicGenerator = None
    INIT_ERROR = str(e)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

input_processor = InputProcessor()
prompt_enhancer = PromptEnhancer()

if MusicGenerator:
    try:
        music_generator = MusicGenerator()
    except Exception as e:
        music_generator = None
        INIT_ERROR = str(e)
else:
    music_generator = None


def generate_music_pipeline(user_input: str) -> dict:
    """
    End-to-end backend music generation pipeline.
    NEVER returns None.
    """

    logging.info("Pipeline started")

    if music_generator is None:
        raise RuntimeError(
            "Music generation is disabled locally. "
            "PyTorch / MusicGen not available."
        )

    # 1️⃣ Input processing
    params = input_processor.process_input(user_input)

    # 2️⃣ Prompt enhancement
    enhanced_prompt = prompt_enhancer.enhance(params, variations=1)[0]

    # 3️⃣ Music generation
    audio_result = music_generator.generate(
        prompt=enhanced_prompt,
        duration=params.get("duration", 30),
        energy_level=params.get("energy", "medium"),
        mood=params.get("mood", "calm")
    )

    if not audio_result or "file" not in audio_result:
        raise RuntimeError("Music generator returned invalid output.")

    # ✅ ALWAYS return a dict
    return {
        "audio": audio_result,
        "params": params,
        "prompt": enhanced_prompt
    }
