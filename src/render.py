"""Render extracted models as HTML."""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from .config import OUTPUT_DIR, TEMPLATES_DIR, DESTINATION
from .models import Chat


def render_index(chats: list[Chat], output_dir: Path = OUTPUT_DIR):
    """Render the conversation index and return its path."""
    output_dir.mkdir(parents=True, exist_ok=True)
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    
    DESTINATION.write_text(env.get_template("index.html").render(chats=chats), encoding="utf-8")

