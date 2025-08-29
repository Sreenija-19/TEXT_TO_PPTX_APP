# Text→PPTX: Your Text, Your Style (Enhanced)

Streamlit app that converts bulk text/markdown into a PowerPoint using an uploaded PPTX/POTX template.

Enhancements:
- Preset guidance modes (Investor pitch, Sales deck, Research summary, Classroom lecture)
- File-size guardrail, improved error handling
- Slide previews (text thumbnails) and speaker notes (optional via LLM)


# Text to PPTX App

Turn bulk text, markdown, or prose into a fully formatted PowerPoint presentation that matches your chosen template’s look and feel.

## Demo
Try the live demo here: [https://text-to-pptx-app.onrender.com/](https://text-to-pptx-app.onrender.com/)

## Features
- Paste large blocks of text or markdown
- Upload your own PowerPoint template (.pptx/.potx)
- LLM-driven slide generation and speaker notes
- Retains template styles, colors, fonts, and images
- Supports OpenAI, Anthropic, Gemini API keys (user-provided, not stored)

## Installation
```bash
git clone https://github.com/Sreenija-19/TEXT_TO_PPTX_APP.git
cd TEXT_TO_PPTX_APP
pip install -r requirements.txt
streamlit run app.py

