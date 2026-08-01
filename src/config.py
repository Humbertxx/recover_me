"""Project paths for the local WhatsApp archive."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECRYPTED_DIR = ROOT / "data" / "decrypted"
OUTPUT_DIR = ROOT / "output"
TEMPLATES_DIR = ROOT / "templates"
ASSETS_DIR = ROOT / "assets"
