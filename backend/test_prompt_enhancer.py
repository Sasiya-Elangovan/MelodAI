from backend.prompt_enhancer import PromptEnhancer

enhancer = PromptEnhancer()

params = {
    "mood": "energetic",
    "energy": 8,
    "style": "edm",
    "tempo": "fast",
    "instruments": ["synth", "drums"]
}

print("\nBASIC PROMPT:")
print("energetic EDM music")

print("\nENHANCED PROMPTS:")
enhanced = enhancer.enhance(params, variations=3)

for i, prompt in enumerate(enhanced, 1):
    print(f"\nVariation {i}:")
    print(prompt)
