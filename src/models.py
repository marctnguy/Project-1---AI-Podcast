from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ArticleInput:
    title: str
    text: str
    source: Optional[str] = None

    def is_valid(self) -> bool:
        return bool(self.title.strip()) and bool(self.text.strip())


@dataclass
class PodcastSettings:
    tone: str = "conversational and passionate"
    audience: str = "cinephile niche listeners"
    target_length_minutes: int = 4
    language: str = "English"

    def is_valid(self) -> bool:
        return self.target_length_minutes > 0


@dataclass
class PodcastEpisode:
    episode_title: str
    script: str
    source_articles: List[ArticleInput] = field(default_factory=list)
    summary: Optional[str] = None

    def is_valid(self) -> bool:
        return bool(self.episode_title.strip()) and bool(self.script.strip())


@dataclass
class PipelineResult:
    success: bool
    episode: Optional[PodcastEpisode] = None
    audio_path: Optional[str] = None
    error_message: Optional[str] = None

    def is_valid(self) -> bool:
        if not self.success:
            return False
        return self.episode is not None and self.audio_path is not None
