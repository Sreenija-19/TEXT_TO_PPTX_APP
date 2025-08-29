# SPDX-License-Identifier: MIT
# Streamlit front-end — Enhanced
import io
import streamlit as st
from datetime import datetime

from slide_maker import build_presentation
from parser import outline_from_text, heuristic_outline
from llm_router import make_outline_with_llm, ProviderConfig

# Basic limits
MAX_UPLOAD_BYTES = 12 * 1024 * 1024  # 12 MB max template size

st.set_page_config(page_title="Text→PPTX: Your Text, Your Style", page_icon="📊", layout="wide")

st.title("📊 Your Text, Your Style – Auto-Generate a Presentation")

st.markdown("""
Turn bulk text, markdown, or prose into a **fully formatted PowerPoint** that matches your **uploaded template** (PPTX/POTX).
- Paste your text
- Optional one-line guidance (e.g. "turn into an investor pitch deck") or choose a preset
- Choose LLM provider and paste your **own API key** (never stored)
- Upload a **PowerPoint template or presentation** to inherit styles, colors, fonts, and images
- Download the generated **.pptx** — *no AI image generation; we only reuse template images.*
""")

with st.sidebar:
    st.header("LLM (Optional)")
    st.caption("Use an LLM to propose slide titles and structure. If omitted, we use a smart heuristic.")
    provider = st.selectbox("Provider", ["None (heuristic)", "OpenAI", "Anthropic", "Gemini"], index=0)
    api_key = st.text_input("API Key (never stored)", type="password")
    model_name = st.text_input("Model name (optional)", placeholder={
        "OpenAI": "gpt-4o-mini or o4-mini",
        "Anthropic": "claude-3-5-sonnet-latest",
        "Gemini": "gemini-1.5-pro"
    }.get(provider, ""))
    st.caption("Keys are used only in-memory for the current request and never logged or written to disk.")

left, right = st.columns([3,2], gap="large")

PRESET_GUIDE = {
    "None": "",
    "Investor pitch": "Create an investor pitch deck: problem, solution, market, traction, business model, ask.",
    "Sales deck": "Create a sales deck focused on customer pain points, solution fit, value propositions, and next steps.",
    "Research summary": "Summarize the research into concise slides: motivation, methods, results, conclusions, future work.",
    "Classroom lecture": "Convert into a clear lecture with learning objectives, key points, examples, and summary.",
}

with left:
    st.subheader("1) Paste your text or markdown")
    user_text = st.text_area("Input", height=300, placeholder="Paste a long article, notes, markdown with headings, etc.")
    st.subheader("2) Optional: one-line guidance")
    guidance = st.text_input("e.g., 'turn into an investor pitch deck' (optional)")

    st.markdown("**Or choose a preset guidance**")
    preset = st.selectbox("Preset guidance", ["None","Investor pitch","Sales deck","Research summary","Classroom lecture"], index=0)
    if preset != "None" and not guidance:
        guidance = PRESET_GUIDE.get(preset, "")

    st.subheader("3) Generation options")
    auto_notes = st.checkbox("Auto-generate speaker notes (LLM)", value=False, help="Optional enhancement")
    preview = st.checkbox("Show slide previews (beta)", value=True, help="Optional enhancement")
    max_slides = st.slider("Max slides", 3, 40, 14)

with right:
    st.subheader("4) Upload template (.pptx or .potx)")
    template_file = st.file_uploader("Upload a PowerPoint template or presentation", type=["pptx","potx"])
    st.caption("We will infer slide layouts, colors, fonts, and **reuse images found in the template**.")

    st.write("")
    generate_btn = st.button("Generate Presentation", type="primary", use_container_width=True)

if generate_btn:
    # Validation
    if not user_text or not template_file:
        st.error("Please paste input text and upload a PowerPoint template.")
        st.stop()

    # Size guardrail
    try:
        template_file.seek(0, io.SEEK_END)
        size = template_file.tell()
        template_file.seek(0)
        if size > MAX_UPLOAD_BYTES:
            st.error(f"Uploaded template is too large ({size/1024/1024:.1f} MB). Max allowed is {MAX_UPLOAD_BYTES/1024/1024:.1f} MB.")
            st.stop()
    except Exception:
        st.warning("Could not determine upload size; proceeding carefully.")

    # Decide outline
    outline = None
    provider_cfg = None
    if provider != "None (heuristic)":
        if not api_key:
            st.warning("You chose an LLM provider but did not provide an API key. Falling back to heuristic parsing.")
        else:
            provider_cfg = ProviderConfig(name=provider, api_key=api_key, model=model_name or None)
            try:
                with st.spinner("Asking LLM to map text into slides..."):
                    outline = make_outline_with_llm(user_text, guidance, provider_cfg, max_slides=max_slides)
            except Exception as e:
                st.warning(f"LLM failed, falling back to heuristic outline. Details: {str(e)[:300]}")
                outline = None

    if outline is None:
        outline = outline_from_text(user_text, guidance=guidance, max_slides=max_slides) or heuristic_outline(user_text, max_slides=max_slides)

    st.success(f"Planned {len(outline)} slides. Building presentation...")

    # Build presentation with template
    try:
        pptx_bytes, preview_imgs = build_presentation(
            text=user_text,
            outline=outline,
            template_stream=template_file,
            guidance=guidance,
            provider_cfg=provider_cfg if auto_notes else None,
            preview=preview
        )
    except Exception as e:
        st.exception(e)
        st.stop()

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    fname = f"TextToPPTX-{ts}.pptx"
    st.download_button("⬇️ Download .pptx", data=pptx_bytes, file_name=fname, mime="application/vnd.openxmlformats-officedocument.presentationml.presentation", use_container_width=True)

    if preview and preview_imgs:
        st.subheader("Slide Previews (beta)")
        cols = st.columns(2)
        for i, img in enumerate(preview_imgs, start=1):
            with cols[(i-1) % 2]:
                st.image(img, caption=f"Slide {i}", use_column_width=True)

st.markdown("---")
st.markdown("**Privacy:** API keys are only used in-memory and never logged or stored. Files are processed transiently in memory when possible.")
st.caption("© MIT License")
