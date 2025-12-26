# backend/prompt_templates.py

EXTRACTION_PROMPT = """
You are an AI music assistant.

From the user input below, extract the following fields
and return them strictly in JSON format.

Fields:
- mood (happy, sad, energetic, calm, romantic, dramatic, focus)
- energy (1 to 10)
- style (music genre)
- tempo (slow, medium, fast)
- instruments (list of instruments)
- context (situation or use case)

User Input:
"{user_input}"

Return ONLY valid JSON.
"""
