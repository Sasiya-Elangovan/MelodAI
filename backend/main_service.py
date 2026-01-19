import logging

from backend.input_processor import InputProcessor
from backend.prompt_enhancer import PromptEnhancer

# --------------------------------------------------
# LOGGING
# --------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

INIT_ERROR = None

# --------------------------------------------------
# SAFE IMPORT: MusicGenerator
# --------------------------------------------------
try:
    from backend.music_generator import MusicGenerator
except Exception as e:
    MusicGenerator = None
    INIT_ERROR = str(e)

# --------------------------------------------------
# SAFE INITIALIZATION
# --------------------------------------------------
try:
    input_processor = InputProcessor()
    prompt_enhancer = PromptEnhancer()
except Exception as e:
    raise RuntimeError(f"Backend initialization failed: {e}")

if MusicGenerator:
    try:
        music_generator = MusicGenerator()
    except Exception as e:
        music_generator = None
        INIT_ERROR = str(e)
else:
    music_generator = None

# --------------------------------------------------
# PIPELINE FUNCTION (TASK 2.3 CONTRACT)
# --------------------------------------------------
def generate_music_pipeline(user_input: str) -> dict:
    """
    End-to-end backend music generation pipeline.

    MUST:
    - Return a dict with audio, params, prompt
    - NEVER return None
    - Raise clear exceptions on failure
    """

    logging.info("Music generation pipeline started")

    if music_generator is None:
        logging.error(f"Music generator unavailable: {INIT_ERROR}")
        raise RuntimeError(
            "Music generation is disabled. "
            "Required dependencies (PyTorch / MusicGen) are not available."
        )

    # 1️⃣ Input processing
    params = input_processor.process_input(user_input)
    logging.info(f"Input processed: {params}")

    # 2️⃣ Prompt enhancement
    enhanced_prompt = prompt_enhancer.enhance(params, variations=1)[0]
    logging.info(f"Enhanced prompt: {enhanced_prompt}")

    # 3️⃣ Music generation
    audio_result = music_generator.generate(
        prompt=enhanced_prompt,
        duration=params.get("duration", 30),
        energy_level=params.get("energy", "medium"),
        mood=params.get("mood", "calm")
    )

    if not audio_result or "file" not in audio_result:
        logging.error("Invalid audio result returned from generator")
        raise RuntimeError("Music generator returned invalid output.")

    # ✅ CONTRACT-COMPLIANT RETURN
    return {
        "audio": audio_result,     # {"file": "...wav"}
        "params": params,
        "prompt": enhanced_prompt
    }
