# Podcast Studio

Podcast Studio is an automated podcast generation app that turns multiple article inputs into a single podcast-style episode.

It uses:
- Python
- Gradio for the user interface
- OpenAI for script generation
- OpenAI TTS for audio generation

## Features

- Paste up to 3 articles into the app
- Generate one combined podcast script
- Convert the script into an audio file
- Save the generated script locally
- Adjust tone, audience, length, language, and voice

## Project Structure

```text
podcast-studio/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── data_processor.py
│   ├── llm_processor.py
│   ├── tts_generator.py
│   └── main.py
├── outputs/
│   ├── audio/
│   └── scripts/
├── requirements.txt
├── README.md
├── .env
├── .env.example
└── .gitignore
```

## Requirements

- Python 3.8+
- OpenAI API key
- Internet connection

## Setup

### 1. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

On macOS / Linux:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and add your API key:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5.4-mini
OPENAI_TTS_MODEL=tts-1
OPENAI_TTS_VOICE=onyx
```

### 4. Run the app

```bash
python -m src.main
```

The Gradio interface should open in your browser.

## How to Use

1. Paste article 1 title and text
2. Paste article 2 title and text if needed
3. Paste article 3 title and text if needed
4. Choose the tone, audience, target length, language, and voice
5. Click **Generate Podcast**
6. Listen to or download the generated audio file
7. Review the generated script

## Output

The app creates:
- a podcast script file in `outputs/scripts/`
- an audio file in `outputs/audio/`

## Notes

- The app currently supports up to 3 articles in the Gradio form
- The output is one combined podcast episode
- The script and audio are generated automatically from the article inputs
- Make sure `.env` is never committed to version control

## Possible Improvements

- Support for article URLs
- PDF upload support
- Dynamic number of article inputs
- Better speaker segmentation
- Transcript preview before audio generation
- More voice and accent controls
- RSS/news feed input

## Presentation Outline

### 1. Introduction
I'm Marc Tanguy, student of Ironhack's Part-time AC for AI consulting and implementation. For this deliverable project, I've built a Podcast Studio.

### 2. Problem
Content like articles, essays or research pieces is written to be read, not heard. Dense paragraphs, passive constructions, and text-native formatting like headers and hyperlinks don't survive the transition to audio. The result, when content is read aloud directly, is something that feels flat, hard to follow, and easy to tune out.

At the same time, audio consumption is growing. People listen while commuting, exercising, cooking — contexts where reading isn't possible. The demand for audio content has never been higher, but the supply of content genuinely *designed* for audio hasn't kept pace.

This tool bridges that gap. It takes any article or written source and transforms it into a script built for listening: conversational in tone, structured for the ear, and shaped around how attention actually works when there's no page to return to.

### 3. Demo
->see recording sent in Slack.

### 4. Takeaways
During this project, I learned how to break an AI application into a clear pipeline: data input, LLM processing, and audio generation. I also learned how important it is to separate responsibilities between files, because keeping the article processing, script generation, and TTS in different modules made the app much easier to debug. On the frontend side, I learned how to use Gradio to build a simple interface that connects directly to the backend pipeline.

If I improved the project next, I would add URL-based article input instead of only pasted text, so the app could automatically fetch and clean articles from the web. I would also make the article input dynamic, so users could add as many articles as they want instead of being limited to three. Another improvement would be better podcast structure, with clearer sections, speaker turns, and smoother transitions. I would also refine the voice controls, add progress indicators in the UI, and improve the error messages so the user gets more precise feedback when something fails.
