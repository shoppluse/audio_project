import streamlit as st
from audio_recorder_streamlit import audio_recorder
from deep_translator import GoogleTranslator
from gtts import gTTS
import speech_recognition as sr
from io import BytesIO

st.set_page_config(
    page_title="Audio Hub",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=DM+Sans:wght@300;400;500&display=swap');

:root {
  --white:      #ffffff;
  --bg:         #f5f7fa;
  --surface:    #ffffff;
  --border:     #dde2eb;
  --border-md:  #c5cdd8;
  --blue:       #1a56db;
  --blue-lt:    #e8effe;
  --blue-dk:    #1341b0;
  --grey-1:     #111827;
  --grey-2:     #374151;
  --grey-3:     #6b7280;
  --grey-4:     #9ca3af;
  --grey-5:     #e5e7eb;
  --success:    #065f46;
  --success-bg: #ecfdf5;
  --success-br: #a7f3d0;
  --info-text:  #1e40af;
  --info-bg:    #eff6ff;
  --info-br:    #bfdbfe;
  --error-bg:   #fef2f2;
  --error-br:   #fecaca;
  --error-text: #991b1b;
  --shadow-sm:  0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-md:  0 4px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04);
  --radius:     8px;
}

html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  font-family: 'Inter', sans-serif !important;
  color: var(--grey-1) !important;
}

[data-testid="stMainBlockContainer"] {
  max-width: 740px !important;
  margin: 0 auto !important;
  padding: 2rem 1.5rem 5rem !important;
}

/* ── Top bar ── */
.topbar {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 1.1rem 1.6rem;
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: 10px;
  margin-bottom: 1.6rem;
  box-shadow: var(--shadow-sm);
}
.topbar-logo {
  width: 38px;
  height: 38px;
  background: var(--blue);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
}
.topbar-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--grey-1);
  letter-spacing: -0.01em;
}
.topbar-sub {
  font-size: 0.72rem;
  color: var(--grey-3);
  margin-top: 2px;
}
.topbar-badge {
  margin-left: auto;
  background: var(--blue-lt);
  color: var(--blue);
  font-size: 0.62rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  padding: 4px 10px;
  border-radius: 20px;
  text-transform: uppercase;
  white-space: nowrap;
}

/* ── Card ── */
.card {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1.5rem 1.8rem;
  margin-bottom: 1rem;
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.2s;
}
.card:hover { box-shadow: var(--shadow-md); }

.section-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 1rem;
}
.step-num {
  width: 24px; height: 24px;
  background: var(--blue);
  color: #fff;
  border-radius: 50%;
  font-size: 0.68rem;
  font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.step-num.done { background: #059669; }
.section-title {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--grey-1);
}
.section-desc {
  margin-left: auto;
  font-size: 0.7rem;
  color: var(--grey-4);
}
.card-divider {
  border: none;
  border-top: 1px solid var(--grey-5);
  margin: 1.1rem 0;
}

/* ── Record hint ── */
.record-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.8rem 0 0.4rem;
  gap: 0.6rem;
}
.record-hint {
  font-size: 0.72rem;
  color: var(--grey-4);
}

/* ── Result labels ── */
.result-label {
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--grey-3);
  margin-bottom: 0.3rem;
}
.result-text {
  font-size: 0.88rem;
  color: var(--grey-1);
  line-height: 1.65;
  font-family: 'DM Sans', sans-serif;
  padding: 0.7rem 1rem;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}

/* ── Streamlit widget overrides ── */
[data-testid="stAudio"] {
  background: var(--bg) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 0.3rem !important;
}
[data-testid="stSelectbox"] label {
  font-size: 0.75rem !important;
  font-weight: 600 !important;
  color: var(--grey-2) !important;
  font-family: 'Inter', sans-serif !important;
}
[data-testid="stSelectbox"] > div > div {
  background: var(--white) !important;
  border: 1px solid var(--border-md) !important;
  border-radius: var(--radius) !important;
  color: var(--grey-1) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.85rem !important;
  box-shadow: var(--shadow-sm) !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stSelectbox"] > div > div:focus-within {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 3px rgba(26,86,219,0.12) !important;
}
[data-testid="stButton"] > button {
  width: 100% !important;
  background: var(--blue) !important;
  color: #fff !important;
  border: none !important;
  border-radius: var(--radius) !important;
  padding: 0.72rem 1.5rem !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.82rem !important;
  font-weight: 600 !important;
  cursor: pointer !important;
  box-shadow: 0 1px 3px rgba(26,86,219,0.25) !important;
  transition: background 0.15s, box-shadow 0.15s, transform 0.1s !important;
}
[data-testid="stButton"] > button:hover {
  background: var(--blue-dk) !important;
  box-shadow: 0 4px 14px rgba(26,86,219,0.35) !important;
  transform: translateY(-1px) !important;
}
[data-testid="stButton"] > button:active { transform: translateY(0) !important; }

[data-testid="stSuccess"] {
  background: var(--success-bg) !important;
  border: 1px solid var(--success-br) !important;
  border-radius: var(--radius) !important;
  color: var(--success) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.82rem !important;
}
[data-testid="stInfo"] {
  background: var(--info-bg) !important;
  border: 1px solid var(--info-br) !important;
  border-radius: var(--radius) !important;
  color: var(--info-text) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.82rem !important;
}
[data-testid="stError"] {
  background: var(--error-bg) !important;
  border: 1px solid var(--error-br) !important;
  border-radius: var(--radius) !important;
  color: var(--error-text) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.82rem !important;
}

[data-testid="stImage"] img {
  border-radius: 50% !important;
  border: 2px solid var(--border) !important;
  object-fit: cover !important;
  max-width: 72px !important;
  max-height: 72px !important;
  box-shadow: var(--shadow-sm) !important;
}

/* ── Footer ── */
.page-footer {
  text-align: center;
  padding: 2rem 0 0;
  font-size: 0.68rem;
  color: var(--grey-4);
  border-top: 1px solid var(--grey-5);
  margin-top: 1.5rem;
}

#MainMenu, footer, header { visibility: hidden; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border-md); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
langs_dict = GoogleTranslator().get_supported_languages(as_dict=True)

# ── Top bar ───────────────────────────────────────────────────────────────────
logo_col, img_col = st.columns([0.87, 0.13])

with logo_col:
    st.markdown("""
    <div class="topbar">
      <div class="topbar-logo">🎙️</div>
      <div>
        <div class="topbar-title">Audio Hub</div>
        <div class="topbar-sub">Speech Recognition &amp; Translation Platform</div>
      </div>
      <div class="topbar-badge">● Live</div>
    </div>
    """, unsafe_allow_html=True)

with img_col:
    try:
        st.image("lord-chaitanya.jpg")
    except Exception:
        pass

# ── Step 1 — Record ───────────────────────────────────────────────────────────
st.markdown("""
<div class="card">
  <div class="section-head">
    <div class="step-num">1</div>
    <div class="section-title">Record Audio</div>
    <div class="section-desc">Speak clearly into your microphone</div>
  </div>
  <hr class="card-divider">
  <div class="record-area">
""", unsafe_allow_html=True)

audio_bytes = audio_recorder(
    text="",
    recording_color="#dc2626",
    neutral_color="#1a56db",
    icon_name="microphone",
    icon_size="2x",
    pause_threshold=3.0,
)

st.markdown("""
    <div class="record-hint">Click to start · Click again to stop recording</div>
  </div>
""", unsafe_allow_html=True)

if audio_bytes:
    st.markdown('<hr class="card-divider">', unsafe_allow_html=True)
    st.audio(audio_bytes, format="audio/wav")

st.markdown("</div>", unsafe_allow_html=True)

# ── Steps 2 & 3 ───────────────────────────────────────────────────────────────
if audio_bytes:

    # Step 2
    st.markdown("""
    <div class="card">
      <div class="section-head">
        <div class="step-num done">✓</div>
        <div class="section-title">Select Target Language</div>
      </div>
      <hr class="card-divider">
    """, unsafe_allow_html=True)

    target_lang = st.selectbox(
        "Translate to",
        list(langs_dict.keys()),
        index=list(langs_dict.keys()).index("hindi") if "hindi" in langs_dict else 0,
    )
    target_code = langs_dict[target_lang]
    st.markdown("</div>", unsafe_allow_html=True)

    # Step 3
    st.markdown("""
    <div class="card">
      <div class="section-head">
        <div class="step-num">3</div>
        <div class="section-title">Transcribe &amp; Translate</div>
        <div class="section-desc">AI-powered processing</div>
      </div>
      <hr class="card-divider">
    """, unsafe_allow_html=True)

    if st.button("Run Transcription & Translation", use_container_width=True):
        with st.spinner("Processing audio…"):
            try:
                recognizer = sr.Recognizer()
                with sr.AudioFile(BytesIO(audio_bytes)) as source:
                    audio_data = recognizer.record(source)
                    original_text = recognizer.recognize_google(audio_data)

                translated_text = GoogleTranslator(
                    source="auto", target=target_code
                ).translate(original_text)

                st.markdown('<hr class="card-divider">', unsafe_allow_html=True)
                st.markdown(f'<div class="result-label">Original Transcript</div><div class="result-text">{original_text}</div>', unsafe_allow_html=True)
                st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="result-label">Translation — {target_lang.title()}</div><div class="result-text">{translated_text}</div>', unsafe_allow_html=True)
                st.markdown('<hr class="card-divider"><div class="result-label">Audio Playback</div>', unsafe_allow_html=True)

                tts = gTTS(text=translated_text, lang=target_code)
                tts_fp = BytesIO()
                tts.write_to_fp(tts_fp)
                st.audio(tts_fp)

            except sr.UnknownValueError:
                st.error("Speech not recognised — please speak clearly and try again.")
            except sr.RequestError as e:
                st.error(f"Recognition service unavailable: {e}")
            except Exception as e:
                st.error(f"An error occurred: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-footer">
  Audio Hub &nbsp;·&nbsp; Speech Recognition &amp; Translation &nbsp;·&nbsp; All rights reserved
</div>
""", unsafe_allow_html=True)
