import os
import sys
import time
import random
import streamlit as st

# ==================================================
# STEP 2: SAFE BACKEND IMPORT
# ==================================================

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from backend.main_service import generate_music_pipeline
    BACKEND_AVAILABLE = True
except Exception as e:
    BACKEND_AVAILABLE = False
    BACKEND_ERROR = str(e)

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="MelodAI - AI Music Generator",
    page_icon="🎵",
    layout="wide"
)

# ==================================================
# STEP 3: SESSION STATE FOR GENERATION
# ==================================================
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

if "current_audio" not in st.session_state:
    st.session_state.current_audio = None

if "generation_params" not in st.session_state:
    st.session_state.generation_params = None

if "generation_prompt" not in st.session_state:
    st.session_state.generation_prompt = None

if "generation_error" not in st.session_state:
    st.session_state.generation_error = None

# ==================================================
# HEADER
# ==================================================
st.title("🎵 MelodAI")
st.caption("AI-powered music generation from text prompts")

st.divider()

# ==================================================
# SIDEBAR – GENERATION SETTINGS
# ==================================================
st.sidebar.header("🎛️ Generation Settings")

duration = st.sidebar.slider("Duration (seconds)", 10, 120, 30)
temperature = st.sidebar.slider("Creativity (Temperature)", 0.5, 1.5, 1.0)
model = st.sidebar.selectbox(
    "Model",
    ["musicgen-small", "musicgen-medium", "musicgen-large"]
)

st.sidebar.divider()
st.sidebar.subheader("⚙ Advanced Parameters")

top_k = st.sidebar.slider("Top-K", 10, 250, 50)
top_p = st.sidebar.slider("Top-P", 0.10, 1.00, 0.90)
cfg = st.sidebar.slider("CFG Coefficient", 1.00, 10.00, 3.00)

st.sidebar.divider()
st.sidebar.subheader("🕘 Generation History")
st.sidebar.info("History will be added in later tasks")

# ==================================================
# MAIN INPUT INTERFACE
# ==================================================
st.subheader("✨ Describe Your Music")

user_input = st.text_area(
    "Describe the music you want",
    value=st.session_state.user_input,
    placeholder="E.g., energetic workout music with electronic beats",
    height=120
)

st.session_state.user_input = user_input

char_count = len(user_input)
st.caption(f"{char_count} / 300 characters")

if char_count == 0:
    st.warning("⚠ Please enter a description.")
elif char_count < 10:
    st.warning("⚠ Description is too short.")
elif char_count > 300:
    st.error("❌ Description is too long.")

# --------------------------------------------------
# QUICK MOOD SELECTOR
# --------------------------------------------------
st.subheader("🎭 Quick Mood")

mood = st.selectbox(
    "Select mood",
    ["Happy", "Sad", "Energetic", "Calm", "Romantic", "Dramatic"]
)

# --------------------------------------------------
# EXAMPLE PROMPTS
# --------------------------------------------------
st.subheader("💡 Example Prompts")

EXAMPLES = {
    "Happy": [
        "Happy pop music for a road trip",
        "Bright cheerful background music",
        "Joyful acoustic guitar track",
        "Upbeat summer vibes music"
    ],
    "Energetic": [
        "High-energy EDM workout music",
        "Fast-paced gym motivation track",
        "Powerful electronic beats",
        "Intense running music"
    ],
    "Calm": [
        "Relaxing ambient meditation music",
        "Soft piano music for studying",
        "Peaceful lo-fi background music",
        "Nature-inspired calm music"
    ],
    "Romantic": [
        "Romantic piano dinner music",
        "Soft acoustic love song",
        "Warm romantic instrumental",
        "Gentle candlelight dinner music"
    ],
    "Sad": [
        "Emotional piano music",
        "Slow sad violin melody",
        "Melancholic breakup music",
        "Deep emotional instrumental"
    ]
}

examples = random.sample(EXAMPLES[mood], 2)
cols = st.columns(2)
for i, ex in enumerate(examples):
    if cols[i].button(ex):
        st.session_state.user_input = ex
        st.rerun()

# ==================================================
# STEP 4: GENERATION WORKFLOW
# ==================================================
st.divider()

if st.button("🎶 Generate Music", type="primary"):
    if not BACKEND_AVAILABLE:
        st.error("Backend is not available. Please check setup.")
    elif not user_input or len(user_input) < 10:
        st.warning("Please enter a more detailed description.")
    else:
        try:
            progress = st.progress(0)
            status = st.empty()

            status.info("🧠 Processing input...")
            progress.progress(25)
            time.sleep(0.5)

            status.info("🎼 Generating music...")
            progress.progress(60)

            with st.spinner("Creating your music..."):
                result = generate_music_pipeline(user_input)

            progress.progress(100)
            status.success("✅ Music generated successfully!")

            st.session_state.current_audio = result["audio"]["file"]
            st.session_state.generation_params = result["params"]
            st.session_state.generation_prompt = result["prompt"]
            st.session_state.generation_error = None

        except Exception as e:
            st.session_state.generation_error = str(e)
            st.error("❌ Music generation failed.")

# ==================================================
# STEP 5: OUTPUT DISPLAY
# ==================================================
st.subheader("🎧 Generated Output")

audio_path = st.session_state.current_audio

if audio_path and os.path.exists(audio_path):
    st.audio(audio_path)

    with st.expander("📄 Generation Details"):
        st.markdown("**Enhanced Prompt**")
        st.code(st.session_state.generation_prompt)

        st.markdown("**Generation Parameters**")
        st.json(st.session_state.generation_params)
else:
    st.info("No music generated yet.")

# ==================================================
# STEP 6: ERROR HANDLING + RETRY
# ==================================================
if st.session_state.generation_error:
    st.error(st.session_state.generation_error)

    col1, col2 = st.columns(2)
    if col1.button("🔁 Retry"):
        st.session_state.generation_error = None
        st.rerun()

    if col2.button("💡 Try Example Prompt"):
        st.session_state.user_input = "Calm piano music for studying"
        st.session_state.generation_error = None
        st.rerun()

# ==================================================
# STEP 7: CANCEL GENERATION (UX SAFE)
# ==================================================
if st.button("🛑 Cancel Generation"):
    st.warning("Generation cancelled by user.")
    st.stop()
