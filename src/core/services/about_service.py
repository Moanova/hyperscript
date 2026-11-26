# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : about_service.py
# Version      : 1
# Date         : 2026-11-10
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
import json
import os

class AboutService:
    """Reads the application about info from config/about.json."""
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def get_about_info(self) -> dict:
        """Return the about info dict (title, version, year, author, built_by)."""
        config_path = os.path.join(self.BASE_DIR, "config", "about.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "title": "Hyperscript",
                "version": "0.1.0-alpha",
                "year": "AA-MM-AAAA",
                "author": "TSC",
                "built_by": "Mistral Vibe + TSC"
            }
