print("✅ test_input_processor.py started")

from backend.input_processor import InputProcessor

print("✅ Imported InputProcessor")

processor = InputProcessor()
print("✅ InputProcessor initialized")

tests = [
    "I need energetic music for my workout",
    "Something calming for meditation",
    "Happy birthday party music",
    "Sad breakup song",
    "Focus music for studying"
]

for text in tests:
    print("\nInput:", text)
    result = processor.process_input(text)
    print("Output:", result)

print("\n✅ Test execution completed")
