"""Vercel Python Function entry point; reuse the local app's HTTP handler."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import Handler


class handler(Handler):
    pass
