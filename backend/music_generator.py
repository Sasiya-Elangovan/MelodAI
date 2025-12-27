import torch
import time
import json
import numpy as np
import soundfile as sf
from pathlib import Path
from transformers import MusicgenForConditionalGeneration, AutoProcessor

CONFIG_PATH = Path("config/generation_params.json")
OUTPUT_DIR = Path("outputs/samples")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class MusicGenerator:
    def __init__(self, model_name="facebook/musicgen-small"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        print("Loading MusicGen model...")
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = MusicgenForConditionalGeneration.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()

        with open(CONFIG_PATH) as f:
            self.config = json.load(f)

        print("MusicGenerator ready")

    def generate(self, prompt, duration=30, energy_level="medium", mood="calm"):
        start_time = time.time()

        energy_cfg = self.config["energy_mapping"][energy_level]
        temperature = energy_cfg["temperature"]
        cfg_coef = energy_cfg["cfg_coef"]

        inputs = self.processor(
            text=[prompt],
            return_tensors="pt",
            padding=True
        ).to(self.device)

        with torch.no_grad():
            audio = self.model.generate(
                **inputs,
                max_new_tokens=duration * 50,
                temperature=temperature,
                guidance_scale=cfg_coef
            )

        # 🔥 ABSOLUTE FIX: extract mono channel
        audio_np = audio[0, 0].cpu().numpy().astype(np.float32)

        # Normalize safely
        peak = np.max(np.abs(audio_np))
        if peak > 0:
            audio_np /= peak

        file_path = OUTPUT_DIR / f"{mood}_{energy_level}_{int(time.time())}.wav"

        # ✅ SAFE WAV WRITE
        sf.write(
            file=str(file_path),
            data=audio_np,
            samplerate=32000,
            subtype="PCM_16"
        )

        return {
            "file": str(file_path),
            "duration": duration,
            "mood": mood,
            "energy": energy_level,
            "generation_time_sec": round(time.time() - start_time, 2),
            "model": "musicgen-small"
        }
