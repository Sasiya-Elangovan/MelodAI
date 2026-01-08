import json
import random
from pathlib import Path

TEMPLATE_PATH = Path("data/mood_templates.json")


class PromptEnhancer:
    def __init__(self):
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            self.mood_templates = json.load(f)

        # Predefined structure variations
        self.structures = [
            "intro-verse-chorus structure",
            "gradual build-up with climax",
            "loop-friendly structure",
            "smooth progression without sharp transitions"
        ]

    def enhance(self, params, variations=1):
        """
        Generate multiple enhanced music prompts with guaranteed uniqueness
        """
        prompts = []

        # Ensure we don't request more variations than available structures
        structure_pool = random.sample(
            self.structures,
            k=min(variations, len(self.structures))
        )

        for structure in structure_pool:
            prompt = self._build_prompt(params, structure)
            if self._validate(prompt):
                prompts.append(prompt)

        return prompts

    def _build_prompt(self, params, structure_hint):
        mood = params.get("mood", "calm")
        tempo = params.get("tempo", "medium")
        style = params.get("style", "ambient")
        instruments = ", ".join(params.get("instruments", ["synth"]))
        energy = params.get("energy", 5)

        base_template = self.mood_templates.get(
            mood, self.mood_templates["calm"]
        )

        bpm = 120 if tempo == "fast" else 90 if tempo == "medium" else 60

        description = base_template.format(tempo=bpm)

        enhanced_prompt = (
            f"{description}. "
            f"Style: {style}. "
            f"Instruments: {instruments}. "
            f"Energy level: {energy}/10. "
            f"Structure: {structure_hint}."
        )

        return enhanced_prompt

    def _validate(self, prompt):
        """
        Validate prompt length and coherence
        """
        return 30 < len(prompt) < 500
