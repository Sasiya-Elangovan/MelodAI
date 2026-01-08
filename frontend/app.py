# ==================================================
# MelodAI – Streamlit Frontend (Tasks 2.1 → 2.6)
# ==================================================

import os
import sys
import uuid
import json
import io
import zipfile
from datetime import datetime
from collections import Counter

import streamlit as st
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt

# --------------------------------------------------
# PATH FIX (IMPORTANT)
# --------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# --------------------------------------------------
# BACKEND IMPORTS (SAFE)
# --------------------------------------------------
try:
    from backend.main_service import (
        generate_music_pipeline,
        generate_music_variations,
        extend_generated_music
    )
    BACKEND_AVAILABLE = True
except Exception as e:
    BACKEND_AVAILABLE = False
    BACKEND_ERROR = str(e)

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="MelodAI - AI Music Generator",
    page_icon="🎵",
    layout="wide"
)

# --------------------------------------------------
# SESSION STATE DEFAULTS
# --------------------------------------------------
for key, default in {
    "history": [],
    "current_audio": None,
    "error": None,
    "example_text": "",
    "show_favorites_only": False,
    "generation_times": [],
    "variations": []
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("🎵 MelodAI")
st.caption("AI-powered music generation from text prompts")

if not BACKEND_AVAILABLE:
    st.warning("⚠ Backend not available locally. UI demo mode enabled.")

st.divider()

# --------------------------------------------------
# SIDEBAR – GENERATION SETTINGS
# --------------------------------------------------
st.sidebar.header("🎛️ Generation Settings")

duration = st.sidebar.slider("Duration (seconds)", 10, 120, 30, step=5)
temperature = st.sidebar.slider("Creativity (Temperature)", 0.5, 1.5, 1.0, step=0.1)
model = st.sidebar.selectbox("Model", ["musicgen-small"])

# --------------------------------------------------
# SIDEBAR – ADVANCED PARAMETERS (TASK 2.6)
# --------------------------------------------------
st.sidebar.divider()
expert_mode = st.sidebar.toggle("🧪 Expert Mode")

if expert_mode:
    top_k = st.sidebar.slider("Top-K", 10, 250, 50)
    top_p = st.sidebar.slider("Top-P", 0.1, 1.0, 0.9)
    cfg = st.sidebar.slider("CFG Coefficient", 1.0, 10.0, 3.0)
else:
    top_k = top_p = cfg = None

# --------------------------------------------------
# SIDEBAR – HISTORY (TASK 2.5)
# --------------------------------------------------
st.sidebar.divider()
st.sidebar.subheader("🕘 Generation History")

if not st.session_state.history:
    st.sidebar.info("No history yet.")
else:
    st.session_state.show_favorites_only = st.sidebar.checkbox(
        "⭐ Show favorites only",
        value=st.session_state.show_favorites_only
    )

    for item in st.session_state.history:
        if st.session_state.show_favorites_only and not item["favorite"]:
            continue

        with st.sidebar.expander(item["prompt"][:30] + "..."):
            st.caption(item["timestamp"].strftime("%Y-%m-%d %H:%M:%S"))
            st.caption(f"Mood: {item['mood']}")

            if os.path.exists(item["audio_file"]):
                st.audio(item["audio_file"])

            c1, c2, c3 = st.columns(3)

            if c1.button("⭐" if not item["favorite"] else "💔", key=f"fav_{item['id']}"):
                item["favorite"] = not item["favorite"]
                st.rerun()

            if c2.button("▶ Replay", key=f"rep_{item['id']}"):
                st.session_state.current_audio = item
                st.rerun()

            if c3.button("🗑", key=f"del_{item['id']}"):
                st.session_state.history.remove(item)
                st.rerun()

    if st.sidebar.button("🧹 Clear All History"):
        st.session_state.history.clear()
        st.rerun()

# --------------------------------------------------
# MAIN LAYOUT
# --------------------------------------------------
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("✨ Describe Your Music")
    user_input = st.text_area(
        "Describe the music you want",
        value=st.session_state.example_text,
        height=120
    )

with right_col:
    st.subheader("🎭 Select Mood")
    mood = st.selectbox(
        "Mood",
        ["Happy", "Sad", "Energetic", "Calm", "Romantic", "Dramatic"]
    )

# --------------------------------------------------
# EXAMPLE PROMPTS
# --------------------------------------------------
st.subheader("💡 Example Prompts")

EXAMPLES = {
    "Happy": ["Happy road trip pop music"],
    "Energetic": ["Energetic EDM gym music"],
    "Calm": ["Relaxing ambient meditation music"],
    "Romantic": ["Romantic piano dinner music"],
    "Sad": ["Emotional violin background score"]
}

if st.button("🎲 Try an Example"):
    st.session_state.example_text = np.random.choice(EXAMPLES[mood])
    st.rerun()

# --------------------------------------------------
# GENERATE MUSIC
# --------------------------------------------------
st.divider()

params = {
    "duration": duration,
    "temperature": temperature,
    "mood": mood,
    "top_k": top_k,
    "top_p": top_p,
    "cfg": cfg
}

if st.button("🎵 Generate Music", type="primary"):
    if len(user_input) < 10:
        st.error("Please enter a detailed description.")
    elif not BACKEND_AVAILABLE:
        st.error("Backend not available locally.")
    else:
        try:
            start = datetime.now()
            with st.spinner("🎶 Creating your music..."):
                result = generate_music_pipeline(user_input)
            gen_time = (datetime.now() - start).total_seconds()

            item = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now(),
                "prompt": user_input,
                "enhanced_prompt": result["prompt"],
                "audio_file": result["audio"]["file"],
                "params": params,
                "mood": mood,
                "favorite": False,
                "gen_time": gen_time
            }

            st.session_state.history.insert(0, item)
            st.session_state.history = st.session_state.history[:10]
            st.session_state.generation_times.append(gen_time)
            st.session_state.current_audio = item

            st.success("✅ Music generated successfully!")

        except Exception as e:
            st.session_state.error = str(e)
            st.error(str(e))

# --------------------------------------------------
# OUTPUT
# --------------------------------------------------
st.divider()
st.subheader("🎧 Generated Output")

item = st.session_state.current_audio

if item and os.path.exists(item["audio_file"]):
    st.audio(item["audio_file"])
else:
    st.info("No audio generated yet.")

# --------------------------------------------------
# VARIATIONS (TASK 2.6)
# --------------------------------------------------
st.divider()
st.subheader("🎛 Music Variations")

if item and st.button("🎶 Generate 3 Variations"):
    try:
        with st.spinner("Creating variations..."):
            st.session_state.variations = generate_music_variations(
                prompt=item["enhanced_prompt"],
                params=item["params"],
                num_variations=3
            )
    except Exception as e:
        st.error(str(e))

if st.session_state.variations:
    cols = st.columns(len(st.session_state.variations))
    for col, var in zip(cols, st.session_state.variations):
        with col:
            st.audio(var["audio"]["file"])
            st.caption(f"Energy: {var['params'].get('energy')}")
            st.button("👍 Vote", key=var["id"])

# --------------------------------------------------
# EXTEND MUSIC (TASK 2.6)
# --------------------------------------------------
st.divider()
st.subheader("⏱ Extend Music")

if item:
    extend_by = st.selectbox("Extend by (seconds)", [15, 30, 45])
    if st.button("➕ Extend Music"):
        try:
            extend_generated_music(
                prompt=item["enhanced_prompt"],
                audio_file=item["audio_file"],
                extend_by=extend_by
            )
        except Exception as e:
            st.error(str(e))

# --------------------------------------------------
# BATCH GENERATION (TASK 2.6)
# --------------------------------------------------
st.divider()
st.subheader("📦 Batch Generation")

batch_input = st.text_area(
    "Enter one prompt per line",
    placeholder="Happy pop\nCalm piano\nEnergetic EDM"
)

if st.button("⚡ Generate Batch"):
    prompts = [p.strip() for p in batch_input.splitlines() if p.strip()]
    for p in prompts:
        try:
            result = generate_music_pipeline(p)
            st.session_state.history.insert(0, {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now(),
                "prompt": p,
                "enhanced_prompt": result["prompt"],
                "audio_file": result["audio"]["file"],
                "params": result["params"],
                "mood": result["params"].get("mood", "unknown"),
                "favorite": False,
                "gen_time": 0.0
            })
        except Exception:
            st.warning(f"Failed: {p}")

# --------------------------------------------------
# STATS
# --------------------------------------------------
st.divider()
st.subheader("📊 History Statistics")

st.metric("Total Generations", len(st.session_state.history))

if st.session_state.history:
    mood_counts = Counter(h["mood"] for h in st.session_state.history)
    st.metric("Most Used Mood", mood_counts.most_common(1)[0][0])

# --------------------------------------------------
# ERROR DISPLAY
# --------------------------------------------------
if st.session_state.error:
    st.error(st.session_state.error)
