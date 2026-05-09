from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List

import gradio as gr

from src.config import SCRIPT_DIR, ensure_output_directories
from src.data_processor import build_article_input, clean_text, normalize_articles
from src.llm_processor import LLMProcessor
from src.models import ArticleInput, PodcastSettings
from src.tts_generator import TTSGenerator


def save_script_to_file(episode_title: str, script: str) -> str:
    ensure_output_directories()

    safe_title = "".join(
        char.lower() if char.isalnum() else "_" for char in episode_title.strip()
    ).strip("_")

    if not safe_title:
        safe_title = "podcast_script"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    script_path = SCRIPT_DIR / f"{safe_title}_{timestamp}.txt"
    script_path.write_text(script, encoding="utf-8")
    return str(script_path)


def parse_articles_from_form(
    title_1: str,
    text_1: str,
    title_2: str,
    text_2: str,
    title_3: str,
    text_3: str,
) -> List[ArticleInput]:
    raw_articles = []

    if clean_text(title_1) and clean_text(text_1):
        raw_articles.append({"title": title_1, "text": text_1})

    if clean_text(title_2) and clean_text(text_2):
        raw_articles.append({"title": title_2, "text": text_2})

    if clean_text(title_3) and clean_text(text_3):
        raw_articles.append({"title": title_3, "text": text_3})

    return normalize_articles(raw_articles)


def generate_podcast(
    title_1: str,
    text_1: str,
    title_2: str,
    text_2: str,
    title_3: str,
    text_3: str,
    tone: str,
    audience: str,
    target_length_minutes: int,
    language: str,
    voice: str,
) -> tuple[str, str, str]:
    try:
        articles = parse_articles_from_form(
            title_1=title_1,
            text_1=text_1,
            title_2=title_2,
            text_2=text_2,
            title_3=title_3,
            text_3=text_3,
        )

        settings = PodcastSettings(
            tone=tone,
            audience=audience,
            target_length_minutes=target_length_minutes,
            language=language,
        )

        llm = LLMProcessor()
        episode = llm.generate_podcast_episode(articles=articles, settings=settings)

        tts = TTSGenerator(voice=voice)
        audio_path = tts.generate_audio(episode)

        script_path = save_script_to_file(episode.episode_title, episode.script)

        transcript = f"""Episode title: {episode.episode_title}

Summary:
{episode.summary or "No summary returned."}

Script:
{episode.script}

Sources:
{chr(10).join(f"- {article.title}" for article in episode.source_articles)}
"""

        return transcript, audio_path, script_path

    except Exception as exc:
        return f"Error: {exc}", None, None


with gr.Blocks(title="Podcast Studio") as demo:
    gr.Markdown("# Podcast Studio")
    gr.Markdown(
        "Paste up to three articles, choose the style, and generate a podcast script plus audio."
    )

    with gr.Row():
        with gr.Column():
            gr.Markdown("## Article 1")
            title_1 = gr.Textbox(label="Title 1", placeholder="Article title")
            text_1 = gr.Textbox(
                label="Text 1",
                placeholder="Paste the full article text here",
                lines=8,
            )

        with gr.Column():
            gr.Markdown("## Article 2")
            title_2 = gr.Textbox(label="Title 2", placeholder="Article title")
            text_2 = gr.Textbox(
                label="Text 2",
                placeholder="Paste the full article text here",
                lines=8,
            )

        with gr.Column():
            gr.Markdown("## Article 3")
            title_3 = gr.Textbox(label="Title 3", placeholder="Article title")
            text_3 = gr.Textbox(
                label="Text 3",
                placeholder="Paste the full article text here",
                lines=8,
            )

    with gr.Row():
        tone = gr.Dropdown(
            choices=[
                "conversational and passionate",
                "casual and fun",
                "professional and informative",
                "warm and reflective",
            ],
            value="conversational and passionate",
            label="Tone",
        )

        audience = gr.Textbox(
            label="Audience",
            value="cinephile niche listeners",
            placeholder="Who is this podcast for?",
        )

        target_length_minutes = gr.Slider(
            minimum=1,
            maximum=10,
            value=4,
            step=1,
            label="Target length (minutes)",
        )

        language = gr.Textbox(
            label="Language",
            value="English",
            placeholder="English, British English, Spanish, etc.",
        )

        voice = gr.Dropdown(
            choices=["alloy", "ash", "ballad", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"],
            value="onyx",
            label="Voice",
        )

    generate_button = gr.Button("Generate Podcast", variant="primary")

    with gr.Row():
        output_script = gr.Textbox(label="Generated Script", lines=18)
        output_audio = gr.Audio(label="Generated Audio", type="filepath")
        output_script_file = gr.File(label="Saved Script File")

    generate_button.click(
        fn=generate_podcast,
        inputs=[
            title_1,
            text_1,
            title_2,
            text_2,
            title_3,
            text_3,
            tone,
            audience,
            target_length_minutes,
            language,
            voice,
        ],
        outputs=[output_script, output_audio, output_script_file],
    )


if __name__ == "__main__":
    ensure_output_directories()
    demo.launch()
