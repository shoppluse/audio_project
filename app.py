import streamlit as st
from audio_recorder_streamlit import audio_recorder
from deep_translator import GoogleTranslator
from gtts import gTTS
import speech_recognition as sr
from io import BytesIO

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Audio Hub",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Google Fonts ── */
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300&family=Space+Mono:wght@400;700&display=swap');

  /* ── Root palette ── */
  :root {
    --bg:        #0a0a0f;
    --surface:   #12121a;
    --border:    #2a2a3d;
    --accent:    #7c6dfa;
    --accent2:   #fa6d9f;
    --gold:      #e8c97a;
    --text:      #e8e8f0;
    --muted:     #7a7a99;
    --glow:      rgba(124, 109, 250, 0.35);
  }

  /* ── Base reset ── */
  html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Space Mono', monospace !important;
  }

  /* ── Noise-grain overlay ── */
  [data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 9999;
    opacity: 0.6;
  }

  /* ── Animated background orbs ── */
  [data-testid="stAppViewContainer"]::after {
    content: "";
    position: fixed;
    inset: 0;
    background:
      radial-gradient(ellipse 50% 40% at 20% 20%, rgba(124,109,250,0.12) 0%, transparent 60%),
      radial-gradient(ellipse 40% 50% at 80% 80%, rgba(250,109,159,0.10) 0%, transparent 60%),
      radial-gradient(ellipse 35% 35% at 50% 50%, rgba(232,201,122,0.05) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
    animation: pulse-orbs 8s ease-in-out infinite alternate;
  }

  @keyframes pulse-orbs {
    0%   { opacity: 0.8; transform: scale(1); }
    100% { opacity: 1;   transform: scale(1.05); }
  }

  /* ── Main block wrapper ── */
  [data-testid="stMainBlockContainer"] {
    position: relative;
    z-index: 1;
    max-width: 720px !important;
    margin: 0 auto !important;
    padding: 2rem 1.5rem 4rem !important;
  }

  /* ── Hero header ── */
  .hero-wrap {
    text-align: center;
    padding: 3rem 0 2.5rem;
    position: relative;
  }
  .hero-tag {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.35em;
    color: var(--accent);
    text-transform: uppercase;
    margin-bottom: 1rem;
    opacity: 0.85;
  }
  .hero-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(2.8rem, 8vw, 5rem);
    font-weight: 300;
    letter-spacing: -0.02em;
    line-height: 1;
    color: var(--text);
    margin: 0 0 0.4rem;
  }
  .hero-title span {
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 50%, var(--gold) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .hero-sub {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    color: var(--muted);
    letter-spacing: 0.12em;
    margin-top: 0.8rem;
  }
  .hero-line {
    width: 60px;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    margin: 1.8rem auto 0;
  }

  /* ── Card container ── */
  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem;
    margin: 1.5rem 0;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s, box-shadow 0.3s;
  }
  .card::before {
    content: "";
    position: absolute;
    inset: 0;
    border-radius: 16px;
    background: linear-gradient(135deg, rgba(124,109,250,0.04) 0%, transparent 60%);
    pointer-events: none;
  }
  .card:hover {
    border-color: rgba(124,109,250,0.4);
    box-shadow: 0 0 30px rgba(124,109,250,0.08);
  }

  /* ── Section labels ── */
  .section-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;
  }
  .section-label::after {
    content: "";
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--border), transparent);
  }

  /* ── Step badge ── */
  .step-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    border: 1px solid var(--accent);
    color: var(--accent);
    font-size: 0.65rem;
    font-family: 'Space Mono', monospace;
    margin-right: 0.6rem;
    flex-shrink: 0;
  }

  /* ── Audio recorder override ── */
  .audio-recorder-wrap {
    display: flex;
    justify-content: center;
    padding: 1.5rem 0;
  }

  /* ── Streamlit widget polish ── */
  [data-testid="stSelectbox"] > div > div {
    background: #1a1a28 !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.8rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
  }
  [data-testid="stSelectbox"] > div > div:hover,
  [data-testid="stSelectbox"] > div > div:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(124,109,250,0.15) !important;
  }
  [data-testid="stSelectbox"] label {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
  }

  /* ── Primary button ── */
  [data-testid="stButton"] > button {
    width: 100% !important;
    background: linear-gradient(135deg, var(--accent) 0%, #5a4fd4 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.85rem 2rem !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    cursor: pointer !important;
    transition: all 0.25s ease !important;
    position: relative !important;
    overflow: hidden !important;
    box-shadow: 0 4px 20px rgba(124,109,250,0.35) !important;
  }
  [data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(124,109,250,0.5) !important;
  }
  [data-testid="stButton"] > button:active {
    transform: translateY(0) !important;
  }

  /* ── Audio player ── */
  [data-testid="stAudio"] {
    background: #1a1a28 !important;
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
    padding: 0.5rem !important;
    margin: 0.6rem 0 !important;
  }

  /* ── Alert boxes ── */
  [data-testid="stSuccess"] {
    background: rgba(124,109,250,0.08) !important;
    border: 1px solid rgba(124,109,250,0.3) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
  }
  [data-testid="stInfo"] {
    background: rgba(250,109,159,0.08) !important;
    border: 1px solid rgba(250,109,159,0.3) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
  }
  [data-testid="stError"] {
    background: rgba(250,80,80,0.08) !important;
    border: 1px solid rgba(250,80,80,0.3) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
  }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

  /* ── Image centering ── */
  [data-testid="stImage"] {
    display: flex;
    justify-content: center;
  }
  [data-testid="stImage"] img {
    border-radius: 50% !important;
    border: 2px solid var(--accent) !important;
    box-shadow: 0 0 30px var(--glow) !important;
    max-width: 110px !important;
    max-height: 110px !important;
    object-fit: cover !important;
  }

  /* ── Hide Streamlit chrome ── */
  #MainMenu, footer, header { visibility: hidden; }

  /* ── Result grid ── */
  .result-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-top: 0.5rem;
  }
  .result-item {
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem;
  }
  .result-item .label {
    font-size: 0.55rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.4rem;
  }
  .result-item .value {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.1rem;
    color: var(--text);
    line-height: 1.4;
  }

  /* ── Footer ── */
  .footer {
    text-align: center;
    padding: 3rem 0 1rem;
    font-size: 0.6rem;
    letter-spacing: 0.25em;
    color: var(--muted);
    text-transform: uppercase;
  }
  .footer span {
    color: var(--accent2);
  }
</style>
""", unsafe_allow_html=True)

# ── Language data ─────────────────────────────────────────────────────────────
langs_dict = GoogleTranslator().get_supported_languages(as_dict=True)

# ── Hero section ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
  <div class="hero-tag">✦ Powered by AI ✦</div>
  <h1 class="hero-title">Audio <span>Hub</span></h1>
  <p class="hero-sub">Record · Transcribe · Translate · Speak</p>
  <div class="hero-line"></div>
</div>
""", unsafe_allow_html=True)

# Profile image (centered, styled via CSS)
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    try:
        st.image("lord-chaitanya.jpg")
    except Exception:
        pass

# ── Step 1 — Record ───────────────────────────────────────────────────────────
st.markdown("""
<div class="card">
  <div class="section-label"><span class="step-badge">1</span>Capture Voice</div>
""", unsafe_allow_html=True)

st.markdown('<div class="audio-recorder-wrap">', unsafe_allow_html=True)
audio_bytes = audio_recorder(
    text="",
    recording_color="#fa6d9f",
    neutral_color="#7c6dfa",
    icon_name="microphone",
    icon_size="3x",
    pause_threshold=3.0,
)
st.markdown("</div>", unsafe_allow_html=True)

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
st.markdown("</div>", unsafe_allow_html=True)   # close card

# ── Step 2 — Configure ────────────────────────────────────────────────────────
if audio_bytes:
    st.markdown("""
<div class="card">
  <div class="section-label"><span class="step-badge">2</span>Configure Translation</div>
""", unsafe_allow_html=True)

    target_lang = st.selectbox(
        "Target Language",
        list(langs_dict.keys()),
        index=list(langs_dict.keys()).index("hindi") if "hindi" in langs_dict else 0,
    )
    target_code = langs_dict[target_lang]
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Step 3 — Process ─────────────────────────────────────────────────────
    st.markdown("""
<div class="card">
  <div class="section-label"><span class="step-badge">3</span>Process & Translate</div>
""", unsafe_allow_html=True)

    if st.button("⟶  PROCESS AUDIO", use_container_width=True):
        with st.spinner(""):
            try:
                # Speech → Text
                recognizer = sr.Recognizer()
                with sr.AudioFile(BytesIO(audio_bytes)) as source:
                    audio_data = recognizer.record(source)
                    original_text = recognizer.recognize_google(audio_data)

                # Translation
                translated_text = GoogleTranslator(
                    source="auto", target=target_code
                ).translate(original_text)

                # Results display
                st.success(f"**Original**  \n{original_text}")
                st.info(f"**{target_lang.title()}**  \n{translated_text}")

                # Text → Speech
                tts = gTTS(text=translated_text, lang=target_code)
                tts_fp = BytesIO()
                tts.write_to_fp(tts_fp)

                st.markdown("""
<div class="section-label" style="margin-top:1.5rem">
  <span class="step-badge">♪</span>Translated Audio
</div>""", unsafe_allow_html=True)
                st.audio(tts_fp)

            except sr.UnknownValueError:
                st.error("Could not understand audio — try speaking more clearly.")
            except sr.RequestError as e:
                st.error(f"Speech recognition service error: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  Crafted with <span>♥</span> · Audio Hub · All systems operational
</div>
""", unsafe_allow_html=True)
