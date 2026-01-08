# backend/music_variations.py

import uuid

class MusicVariationEngine:
    def __init__(self, music_generator):
        if music_generator is None:
            raise RuntimeError("MusicGenerator unavailable")
        self.music_generator = music_generator

    def generate_variations(self, base_prompt, base_params, num_variations=3):
        """
        Generate multiple musical variations by tweaking parameters.
        Returns list of audio result dicts.
        """
        variations = []

        for i in range(num_variations):
            varied_params = base_params.copy()

            # Parameter variations
            varied_params["temperature"] = min(
                1.5, base_params.get("temperature", 1.0) + (i * 0.15)
            )
            varied_params["energy"] = ["low", "medium", "high"][i % 3]

            audio = self.music_generator.generate(
                prompt=base_prompt,
                duration=base_params.get("duration", 30),
                energy_level=varied_params["energy"],
                mood=base_params.get("mood", "calm")
            )

            if not audio or "file" not in audio:
                raise RuntimeError("Variation generation failed")

            variations.append({
                "id": str(uuid.uuid4()),
                "audio": audio,
                "params": varied_params
            })

        return variations

    def extend_music(self, prompt, base_audio_path, extend_duration=30):
        """
        Extend existing music.
        NOTE: Placeholder for MusicGen continuation
        """
        raise RuntimeError(
            "Music extension requires MusicGen continuation support (GPU only)"
        )
