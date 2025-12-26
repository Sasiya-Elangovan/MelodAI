import json
import random
from pathlib import Path

TEMPLATE_PATH = Path("data/mood_templates.json")


class PromptEnhancer:
    def __init__(self):
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            self.mood_templates = json.load(f)

    def enhance(self, params, variations=1):
        """
        Generate enhanced music prompts from extracted parameters
        """
        prompts = []
        for _ in range(variations):
            prompt = self._build_prompt(params)
            if self._validate(prompt):
                prompts.append(prompt)
        return prompts

    def _build_prompt(self, params):
        mood = params.get("mood", "calm")
        tempo = params.get("tempo", "medium")
        style = params.get("style", "ambient")
        instruments = ", ".join(params.get("instruments", ["synth"]))
        energy = params.get("energy", 5)

        base_template = self.mood_templates.get(
            mood, self.mood_templates["calm"]
        )

        description = base_template.format(
            tempo=120 if tempo == "fast" else 90 if tempo == "medium" else 60
        )

        structure_hint = random.choice([
            "intro-verse-chorus structure",
            "gradual build-up with climax",
            "loop-friendly structure",
            "smooth progression without sharp transitions"
        ])

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
        return 20 < len(prompt) < 500
