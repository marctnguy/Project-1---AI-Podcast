from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

from openai import OpenAI
from pydub import AudioSegment

from src.config import AUDIO_DIR, OPENAI_TTS_MODEL, OPENAI_TTS_VOICE, ensure_output_directories
from src.models import PodcastEpisode


class TTSGenerator:
    MAX_TTS_CHARS = 3800

    def __init__(
        self,
        model: str | None = None,
        voice: str | None = None,
    ):
        self.client = OpenAI()
        self.model = model or OPENAI_TTS_MODEL
        self.voice = voice or OPENAI_TTS_VOICE

    def _build_output_path(self, episode_title: str) -> Path:
        ensure_output_directories()

        safe_title = "".join(
            char.lower() if char.isalnum() else "_" for char in episode_title.strip()
        ).strip("_")

        if not safe_title:
            safe_title = "podcast_episode"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return AUDIO_DIR / f"{safe_title}_{timestamp}.mp3"

    def _split_script(self, script: str) -> List[str]:
        words = script.split()
        if not words:
            return []

        chunks: List[str] = []
        current_chunk: List[str] = []

        for word in words:
            candidate = " ".join(current_chunk + [word])
            if len(candidate) <= self.MAX_TTS_CHARS:
                current_chunk.append(word)
                continue

            if current_chunk:
                chunks.append(" ".join(current_chunk).strip())
                current_chunk = [word]
                continue

            # Fallback for a single very long token.
            chunks.append(word[: self.MAX_TTS_CHARS])
            remainder = word[self.MAX_TTS_CHARS :]
            current_chunk = [remainder] if remainder else []

        if current_chunk:
            chunks.append(" ".join(current_chunk).strip())

        return [chunk for chunk in chunks if chunk]

    def _generate_chunk_audio(self, text: str, output_path: Path) -> None:
        with self.client.audio.speech.with_streaming_response.create(
            model=self.model,
            voice=self.voice,
            input=text,
            instructions=(
                "Speak in a warm British English accent, with a polished podcast tone. "
                "Speak clearly, naturally, and in a conversational but passionate tone. "
                "Delivery should be engaging and dynamic, with appropriate pacing and emphasis "
                "to keep listeners interested."
            ),
        ) as response:
            response.stream_to_file(output_path)

    @staticmethod
    def _is_model_access_error(exc: Exception) -> bool:
        message = str(exc).lower()
        return "model_not_found" in message or "does not have access to model" in message

    def _candidate_models(self) -> List[str]:
        candidates = [self.model, "tts-1", "tts-1-hd"]
        seen: List[str] = []
        for candidate in candidates:
            if candidate and candidate not in seen:
                seen.append(candidate)
        return seen

    def generate_audio(self, episode: PodcastEpisode) -> str:
        if not episode.is_valid():
            raise ValueError("Podcast episode is invalid.")

        output_path = self._build_output_path(episode.episode_title)
        script_chunks = self._split_script(episode.script)

        if not script_chunks:
            raise ValueError("Podcast episode script is empty.")

        with TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            chunk_files: List[Path] = []

            last_error: Exception | None = None
            for model_name in self._candidate_models():
                try:
                    for index, chunk in enumerate(script_chunks, start=1):
                        chunk_path = temp_dir_path / f"chunk_{index:03d}.mp3"
                        self.model = model_name
                        self._generate_chunk_audio(chunk, chunk_path)
                        chunk_files.append(chunk_path)
                    break
                except Exception as exc:
                    last_error = exc
                    if not self._is_model_access_error(exc):
                        raise
                    chunk_files.clear()
                    continue

            if not chunk_files:
                raise ValueError(
                    f"TTS generation failed with available models. Last error: {last_error}"
                )

            combined_audio = AudioSegment.empty()
            for chunk_file in chunk_files:
                combined_audio += AudioSegment.from_file(chunk_file, format="mp3")

            combined_audio.export(output_path, format="mp3")

        return str(output_path)
