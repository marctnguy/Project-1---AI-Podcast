from pathlib import Path
from typing import Any, Dict, List, Sequence, Union

from src.models import ArticleInput


def clean_text(text: str) -> str:
    """
    Normalize whitespace and remove empty lines.
    """
    if not text:
        return ""

    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return " ".join(lines).strip()


def build_article_input(title: str, text: str, source: str | None = None) -> ArticleInput:
    """
    Create a validated ArticleInput object from raw values.
    """
    article = ArticleInput(
        title=clean_text(title),
        text=clean_text(text),
        source=clean_text(source) if source else None,
    )

    if not article.is_valid():
        raise ValueError("Article must have a non-empty title and text.")

    return article


def normalize_articles(
    raw_articles: Sequence[Union[ArticleInput, Dict[str, Any]]]
) -> List[ArticleInput]:
    """
    Convert a list of raw article objects into a clean list of ArticleInput objects.

    Accepts:
    - ArticleInput objects
    - dictionaries with keys: title, text, source
    """
    articles: List[ArticleInput] = []

    for index, item in enumerate(raw_articles, start=1):
        if isinstance(item, ArticleInput):
            if not item.is_valid():
                raise ValueError(f"Article {index} is invalid.")
            articles.append(
                ArticleInput(
                    title=clean_text(item.title),
                    text=clean_text(item.text),
                    source=clean_text(item.source) if item.source else None,
                )
            )
            continue

        if isinstance(item, dict):
            title = item.get("title", "")
            text = item.get("text", "")
            source = item.get("source")
            articles.append(build_article_input(title=title, text=text, source=source))
            continue

        raise TypeError(
            f"Article {index} must be an ArticleInput or dict, got {type(item).__name__}."
        )

    if not articles:
        raise ValueError("At least one article is required.")

    return articles


def load_articles_from_text_file(file_path: str) -> List[ArticleInput]:
    """
    Load articles from a plain text file.

    Expected format:
    Each article is separated by a line with '---'
    and each block can use:
        Title: ...
        Source: ...
        Text: ...
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    content = path.read_text(encoding="utf-8").strip()
    if not content:
        raise ValueError("The article file is empty.")

    blocks = [block.strip() for block in content.split("\n---\n") if block.strip()]
    articles: List[ArticleInput] = []

    for block in blocks:
        title = ""
        source = None
        text_lines: List[str] = []
        reading_text = False

        for line in block.splitlines():
            stripped = line.strip()

            if stripped.lower().startswith("title:"):
                title = stripped.split(":", 1)[1].strip()
                continue

            if stripped.lower().startswith("source:"):
                source = stripped.split(":", 1)[1].strip()
                continue

            if stripped.lower().startswith("text:"):
                reading_text = True
                text_lines.append(stripped.split(":", 1)[1].strip())
                continue

            if reading_text:
                text_lines.append(stripped)

        article_text = clean_text("\n".join(text_lines))
        articles.append(build_article_input(title=title, text=article_text, source=source))

    return articles


def articles_to_dicts(articles: List[ArticleInput]) -> List[Dict[str, str]]:
    """
    Convert ArticleInput objects into plain dictionaries for prompt formatting
    or UI display.
    """
    return [
        {
            "title": article.title,
            "text": article.text,
            "source": article.source or "",
        }
        for article in articles
    ]
