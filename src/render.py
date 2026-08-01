"""Render recovered WhatsApp conversations as local HTML."""

from pathlib import Path
import shutil
from collections.abc import Sequence
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import ASSETS_DIR, OUTPUT_DIR, TEMPLATES_DIR
from .models import Chat, ChatSummary


STATIC_ASSETS = ("conversation.js", "conversation.css")


def render_chats(
    chats: Sequence[Chat],
    output_dir: Path = OUTPUT_DIR,
    *,
    sidebar_chats: Sequence[ChatSummary] | None = None,
    navigation_enabled: bool = False,
) -> Path:
    """Render an index and one HTML page for each conversation."""
    output_dir.mkdir(parents=True, exist_ok=True)
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html", "xml"]),
    )
    for asset in STATIC_ASSETS:
        shutil.copy2(ASSETS_DIR / asset, output_dir / asset)
    index_path = output_dir / "index.html"
    index_path.write_text(env.get_template("index.html").render(chats=chats), encoding="utf-8")
    chat_template = env.get_template("chat.html")
    navigation = sidebar_chats if sidebar_chats is not None else chats
    for chat in chats:
        (output_dir / f"chat-{chat.id}.html").write_text(
            chat_template.render(
                chat=chat,
                sidebar_chats=navigation,
                navigation_enabled=navigation_enabled,
            ),
            encoding="utf-8",
        )
    return index_path


def render_index(chats: Sequence[Chat], output_dir: Path = OUTPUT_DIR) -> Path:
    """Backward-compatible alias for rendering conversations."""
    return render_chats(chats, output_dir)
