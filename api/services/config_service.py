import json
from pathlib import Path
from typing import Dict, Optional, List


class ConfigService:
    def __init__(self, config_path: str = "api/config.json"):
        self.config_path = Path(config_path)
        self.default_config = {
            "ignore_patterns": [
                "__pycache__",
                ".git",
                "node_modules",
                ".venv",
                "venv",
                ".pytest_cache",
                "*.pyc",
            ],
            "languages": ["python", "javascript", "sql"],
            "rules": {
                "security": True,
                "quality_score": True,
                "code_smells": True,
                "doc_coverage": True,
                "complexity": True,
            },
            "thresholds": {
                "quality_min": 60.0,
                "complexity_max": 15,
                "doc_coverage_min": 50.0,
            },
        }
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    return json.load(f)
            except Exception:
                return self.default_config.copy()
        return self.default_config.copy()

    def _save_config(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=2)

    def get_config(self) -> Dict:
        return self.config.copy()

    def get_default_config(self) -> Dict:
        return self.default_config.copy()

    def update_config(self, updates: Dict) -> bool:
        try:
            if "ignore_patterns" in updates:
                self.config["ignore_patterns"] = updates["ignore_patterns"]

            if "languages" in updates:
                self.config["languages"] = updates["languages"]

            if "rules" in updates:
                self.config["rules"].update(updates["rules"])

            if "thresholds" in updates:
                self.config["thresholds"].update(updates["thresholds"])

            self._save_config()
            return True

        except Exception:
            return False

    def reset_to_defaults(self) -> bool:
        try:
            self.config = self.default_config.copy()
            self._save_config()
            return True
        except Exception:
            return False

    def validate_config(self) -> List[str]:
        errors = []

        if not isinstance(self.config.get("ignore_patterns"), list):
            errors.append("ignore_patterns must be a list")

        if not isinstance(self.config.get("languages"), list):
            errors.append("languages must be a list")

        if not isinstance(self.config.get("rules"), dict):
            errors.append("rules must be a dict")

        if not isinstance(self.config.get("thresholds"), dict):
            errors.append("thresholds must be a dict")

        return errors
