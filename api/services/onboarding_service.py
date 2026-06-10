import sys
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scanner"))

try:
    from creative_suite import CreativeSuiteOrchestrator
except ImportError:
    CreativeSuiteOrchestrator = None


class OnboardingService:
    def __init__(self):
        self.onboarding_jobs: Dict[str, Dict[str, Any]] = {}
        self.orchestrator = CreativeSuiteOrchestrator() if CreativeSuiteOrchestrator else None

    def _resolve_path(self, path_input: str) -> str:
        """Resolve path: try exact path first, then search common locations."""
        path = Path(path_input)

        # Try exact path first
        if path.exists():
            return str(path.resolve())

        # If it's just a directory name, search common locations
        if '/' not in path_input and '\\' not in path_input:
            common_locations = [
                Path.home() / 'Documents' / path_input,
                Path.home() / 'Documents' / 'assignments' / 'pursuit' / path_input,
                Path.home() / 'Documents' / 'codescanner' / path_input,
                Path.home() / 'Documents' / 'claudeassisted' / path_input,
                Path.home() / 'Documents' / 'Bronze_to_silver' / path_input,
                Path.cwd() / path_input,
            ]
            for candidate in common_locations:
                if candidate.exists():
                    return str(candidate.resolve())

        # Path not found
        raise ValueError(f"Path not found: {path_input}. Try using the full absolute path (e.g., /Users/meera/Documents/claudeassisted/nba-etl-pipeline)")

    def generate_profile(
        self,
        directory_path: str,
        tone: str = "neutral",
        include_creative_suite: bool = True,
        format: str = "json",
    ) -> Dict[str, Any]:
        job_id = f"onboard_{uuid.uuid4().hex[:12]}"
        start_time = datetime.utcnow()

        try:
            # Resolve path first
            resolved_path = self._resolve_path(directory_path)

            profile = {
                "overview": self._generate_overview(resolved_path),
                "architecture": self._generate_architecture(resolved_path),
                "getting_started": self._generate_getting_started(resolved_path),
                "important_files": self._generate_important_files(resolved_path),
                "learning_path": self._generate_learning_path(resolved_path),
                "common_tasks": self._generate_common_tasks(resolved_path),
                "troubleshooting": self._generate_troubleshooting(resolved_path),
            }

            if include_creative_suite and self.orchestrator:
                try:
                    creative_result = self.orchestrator.analyze(resolved_path)
                    profile["creative_suite"] = {
                        "personality": creative_result.personality,
                        "letter": creative_result.letter,
                        "caqi": creative_result.caqi,
                    }
                except Exception:
                    profile["creative_suite"] = None

            html = None
            markdown = None

            if format in ["html", "all"]:
                html = self._generate_html(profile, tone)

            if format in ["markdown", "all"]:
                markdown = self._generate_markdown(profile, tone)

            result = {
                "job_id": job_id,
                "status": "completed",
                "profile": profile,
                "html": html,
                "markdown": markdown,
                "timestamp": start_time.isoformat(),
            }

            self.onboarding_jobs[job_id] = result
            return result

        except Exception as e:
            return {
                "job_id": job_id,
                "status": "error",
                "error": str(e),
                "profile": None,
                "html": None,
                "markdown": None,
            }

    def get_profile(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self.onboarding_jobs.get(job_id)

    def _generate_overview(self, directory_path: str) -> Dict[str, str]:
        return {
            "summary": f"Codebase at {directory_path}",
            "purpose": "Analyze and understand the codebase structure",
            "key_metrics": "Files, functions, complexity",
        }

    def _generate_architecture(self, directory_path: str) -> Dict[str, Any]:
        path = Path(directory_path)
        structure = {}

        if path.exists():
            for item in path.iterdir():
                if item.is_dir() and not item.name.startswith("."):
                    structure[item.name] = f"Directory: {item.name}"

        return {
            "folder_structure": structure,
            "key_components": list(structure.keys())[:5],
            "entry_points": ["main.py", "index.js", "app.py"],
        }

    def _generate_getting_started(self, directory_path: str) -> Dict[str, str]:
        return {
            "prerequisites": "Python 3.8+, pip/npm",
            "installation": "pip install -r requirements.txt",
            "running_locally": "python main.py or npm start",
            "first_steps": "Read README.md and explore src/ directory",
        }

    def _generate_important_files(self, directory_path: str) -> Dict[str, str]:
        return {
            "README": "Project documentation",
            "requirements.txt": "Python dependencies",
            "package.json": "Node.js dependencies",
            "config.py": "Configuration settings",
            "main.py": "Application entry point",
        }

    def _generate_learning_path(self, directory_path: str) -> list:
        return [
            {"step": 1, "task": "Read README and understand project goals"},
            {"step": 2, "task": "Explore directory structure and key files"},
            {"step": 3, "task": "Set up local development environment"},
            {"step": 4, "task": "Run tests and verify setup"},
            {"step": 5, "task": "Make small changes and submit PR"},
        ]

    def _generate_common_tasks(self, directory_path: str) -> Dict[str, str]:
        return {
            "running_tests": "pytest tests/ or npm test",
            "building": "python setup.py build or npm build",
            "deploying": "See deployment guide in docs/",
            "debugging": "Use debugger or add logging statements",
            "contributing": "Fork, branch, commit, push, PR",
        }

    def _generate_troubleshooting(self, directory_path: str) -> Dict[str, str]:
        return {
            "import_errors": "Check PYTHONPATH and virtual environment",
            "dependency_issues": "Run pip install -r requirements.txt again",
            "port_already_in_use": "Change port in config or kill process",
            "test_failures": "Check recent changes and git status",
            "slow_performance": "Profile code and optimize bottlenecks",
        }

    def _generate_html(self, profile: Dict, tone: str) -> str:
        html_content = f"""
        <html>
        <head>
            <title>Codebase Onboarding Profile</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                h2 {{ color: #666; margin-top: 20px; }}
                .section {{ margin-bottom: 30px; padding: 15px; background: #f9f9f9; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>Codebase Onboarding Profile ({tone.upper()})</h1>
            <div class="section">
                <h2>Overview</h2>
                <p>{profile['overview']['summary']}</p>
            </div>
            <div class="section">
                <h2>Architecture</h2>
                <p>Key components: {', '.join(profile['architecture']['key_components'])}</p>
            </div>
            <div class="section">
                <h2>Getting Started</h2>
                <p>{profile['getting_started']['installation']}</p>
            </div>
        </body>
        </html>
        """
        return html_content

    def _generate_markdown(self, profile: Dict, tone: str) -> str:
        markdown = f"""
# Codebase Onboarding Profile

## Overview
{profile['overview']['summary']}

## Architecture
Key components: {', '.join(profile['architecture']['key_components'])}

## Getting Started
{profile['getting_started']['installation']}

## Learning Path
"""
        for step in profile["learning_path"]:
            markdown += f"\n{step['step']}. {step['task']}"

        return markdown
