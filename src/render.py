"""Render extracted models as HTML."""

from pathlib import Path
import shutil
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import ASSETS_DIR, OUTPUT_DIR, TEMPLATES_DIR
from .models import Chat


def render_chats(chats: list[Chat], output_dir: Path = OUTPUT_DIR) -> Path:
    """Render an index and one HTML page for each conversation."""
    output_dir.mkdir(parents=True, exist_ok=True)
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html", "xml"]),
    )
    shutil.copy2(ASSETS_DIR / "conversation.js", output_dir / "conversation.js")
    index_path = output_dir / "index.html"
    index_path.write_text(env.get_template("index.html").render(chats=chats), encoding="utf-8")
    chat_template = env.get_template("chat.html")
    for chat in chats:
        (output_dir / f"chat-{chat.id}.html").write_text(
            chat_template.render(chat=chat),
            encoding="utf-8",
        )
    return index_path


def render_index(chats: list[Chat], output_dir: Path = OUTPUT_DIR) -> Path:
    """Backward-compatible alias for rendering conversations."""
    return render_chats(chats, output_dir)
