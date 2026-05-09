from __future__ import annotations

from typing import List

from openai import OpenAI

from src.config import OPENAI_MODEL
from src.data_processor import articles_to_dicts
from src.models import ArticleInput, PodcastEpisode, PodcastSettings


class LLMProcessor:
    def __init__(self, model: str | None = None):
        self.client = OpenAI()
        self.model = model or OPENAI_MODEL

    def _build_system_prompt(self, settings: PodcastSettings) -> str:
        return f"""
You are a podcast script writer.

Write a short podcast episode based on multiple articles.

Style:
- Tone: {settings.tone}
- Audience: {settings.audience}
- Language: {settings.language}
- Target length: about {settings.target_length_minutes} minutes
- Use British English spelling and phrasing

Rules:
- Make it sound natural for spoken audio.
- Add a short intro, smooth transitions, and a closing.
- Do not mention that you are an AI.
- Do not use bullet points in the final script.
- Turn the source material into a coherent episode.
- Keep the output clear, engaging, and easy to read aloud.

Return the response in this format:

Episode Title: ...
Summary: ...
Script: ...
""".strip()

    def _build_user_prompt(self, articles: List[ArticleInput]) -> str:
        article_dicts = articles_to_dicts(articles)

        chunks = []
        for index, article in enumerate(article_dicts, start=1):
            chunks.append(
                f"""
Article {index}
Title: {article["title"]}
Source: {article["source"] or "N/A"}
Text:
{article["text"]}
""".strip()
            )

        return "\n\n".join(chunks)

    def generate_podcast_episode(
        self,
        articles: List[ArticleInput],
        settings: PodcastSettings,
    ) -> PodcastEpisode:
        if not articles:
            raise ValueError("At least one article is required to generate a podcast episode.")

        if not settings.is_valid():
            raise ValueError("Invalid podcast settings.")

        system_prompt = self._build_system_prompt(settings)
        user_prompt = self._build_user_prompt(articles)

        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        text = response.output_text.strip()
        if not text:
            raise ValueError("The LLM returned an empty response.")

        episode_title = "Podcast Episode"
        summary = None
        script_lines: list[str] = []
        reading_script = False

        for line in [line.strip() for line in text.splitlines() if line.strip()]:
            lowered = line.lower()

            if lowered.startswith("episode title:"):
                episode_title = line.split(":", 1)[1].strip() or episode_title
                continue

            if lowered.startswith("summary:"):
                summary = line.split(":", 1)[1].strip() or None
                continue

            if lowered.startswith("script:"):
                reading_script = True
                script_lines.append(line.split(":", 1)[1].strip())
                continue

            if reading_script:
                script_lines.append(line)

        script = "\n".join(script_lines).strip()

        if not script:
            script = text

        return PodcastEpisode(
            episode_title=episode_title,
            script=script,
            source_articles=articles,
            summary=summary,
        )
