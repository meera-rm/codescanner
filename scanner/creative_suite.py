"""
Creative Suite Orchestrator - Unified Analysis (Personality + Inheritance Letter + CAQI)

Coordinates all three analyses on the same codebase and provides unified output.
"""

import json
import signal
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from personality import profile_codebase, generate_personality_html
from inheritance import generate_letter, render_letter_html
from caqi import Pollutants, CAQICalculator, CAQIFormatter
from metrics_aggregator import MetricsAggregator


class TimeoutError(Exception):
    """Raised when analysis exceeds time limit."""
    pass


def timeout_handler(signum, frame):
    raise TimeoutError("Analysis timeout: exceeded 30 seconds")


@dataclass
class CreativeSuiteResult:
    """Complete Creative Suite analysis result."""
    job_id: str
    timestamp: str
    codebase_path: str
    status: str

    # Individual analyses
    personality: Dict[str, Any]
    letter: Dict[str, Any]
    caqi: Dict[str, Any]

    # HTML outputs
    html_files: Dict[str, str]

    # Markdown report
    markdown_report: str


class CreativeSuiteOrchestrator:
    """Orchestrates all three Creative Suite analyses."""

    def __init__(self):
        self.aggregator = MetricsAggregator()

    def analyze(self, codebase_path: str, job_id: str) -> CreativeSuiteResult:
        """
        Run all three analyses on the codebase.

        Args:
            codebase_path: Path to code to analyze
            job_id: Unique job identifier

        Returns:
            CreativeSuiteResult with all three analyses
        """
        # Set a 30-second timeout for the entire analysis
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)

        try:
            # Step 1: Aggregate metrics
            print(f"[{job_id}] Aggregating metrics...")
            metrics = self.aggregator.aggregate(codebase_path)

            # Step 2: Personality Profile
            print(f"[{job_id}] Analyzing personality...")
            personality = self._analyze_personality(metrics)

            # Step 3: Inheritance Letter
            print(f"[{job_id}] Generating inheritance letter...")
            letter = self._analyze_letter(metrics)

            # Step 4: CAQI Score
            print(f"[{job_id}] Calculating CAQI score...")
            caqi = self._analyze_caqi(metrics)

            # Step 5: Generate HTML files
            print(f"[{job_id}] Generating HTML outputs...")
            html_files = self._generate_html_outputs(personality, letter, caqi)

            # Step 6: Generate markdown report
            print(f"[{job_id}] Generating markdown report...")
            markdown_report = self._generate_markdown_report(personality, letter, caqi)

            # Step 7: Create result
            result = CreativeSuiteResult(
                job_id=job_id,
                timestamp=datetime.now().isoformat(),
                codebase_path=str(codebase_path),
                status="completed",
                personality=personality,
                letter=letter,
                caqi=caqi,
                html_files=html_files,
                markdown_report=markdown_report
            )

            print(f"[{job_id}] ✅ Complete Creative Suite analysis finished!")
            return result
        except TimeoutError as e:
            print(f"[{job_id}] ⏱️ {str(e)}")
            # Return a partial result on timeout
            return CreativeSuiteResult(
                job_id=job_id,
                timestamp=datetime.now().isoformat(),
                codebase_path=str(codebase_path),
                status="timeout",
                personality={"error": "Analysis timeout after 30 seconds"},
                letter={"error": "Analysis timeout after 30 seconds"},
                caqi={"error": "Analysis timeout after 30 seconds"},
                html_files={},
                markdown_report="Analysis timed out after 30 seconds"
            )
        finally:
            # Cancel the alarm
            signal.alarm(0)

    def _analyze_personality(self, metrics) -> Dict[str, Any]:
        """Generate personality profile."""
        metrics_dict = {
            "avg_complexity": metrics.avg_complexity,
            "max_complexity": metrics.max_complexity,
            "security_high_count": metrics.security_high_count,
            "security_medium_count": metrics.security_medium_count,
            "smell_count": metrics.smell_count,
            "doc_coverage_ratio": metrics.doc_coverage_ratio,
            "duplication_percentage": metrics.duplication_percentage,
            "avg_imports_per_file": metrics.avg_imports_per_file,
            "has_circular_deps": metrics.has_circular_deps,
            "total_logging": metrics.total_logging,
            "error_handling_density": metrics.error_handling_density,
            "total_functions": metrics.total_functions,
            "avg_quality_score": metrics.avg_quality_score,
        }
        return profile_codebase(metrics_dict)

    def _analyze_letter(self, metrics) -> Dict[str, Any]:
        """Generate inheritance letter using aggregate metrics."""
        # If we have per-file metrics, use them
        if metrics.per_file_metrics:
            metrics_list = []
            for filepath, file_metrics in metrics.per_file_metrics.items():
                security_penalty = file_metrics.get("security_issues", 0) * 20
                smell_penalty = file_metrics.get("smells", 0) * 5
                doc_penalty = (1 - file_metrics.get("doc_coverage", 0.5)) * 20
                quality = max(0, 100 - security_penalty - smell_penalty - doc_penalty)

                metrics_list.append({
                    "filepath": filepath,
                    "quality_score": quality,
                    "complexity_average": 1.0,
                    "security_findings": {"high": [{"type": "issue", "line": 0}] if file_metrics.get("security_issues", 0) > 0 else []},
                    "smells_count": file_metrics.get("smells", 0),
                    "doc_coverage": file_metrics.get("doc_coverage", 0.5),
                })
        else:
            # Use aggregate metrics to create synthetic per-file metrics for letter generation
            # This gives us realistic-looking metrics even when per-file data isn't available
            security_penalty = metrics.security_high_count * 20
            smell_penalty = metrics.smell_count * 5
            doc_penalty = (1 - metrics.doc_coverage_ratio) * 20
            quality = max(0, 100 - security_penalty - smell_penalty - doc_penalty)

            metrics_list = [{
                "filepath": "codebase",
                "quality_score": quality,
                "complexity_average": metrics.avg_complexity,
                "security_findings": {"high": [{"type": "issue"}] * metrics.security_high_count if metrics.security_high_count > 0 else []},
                "smells_count": metrics.smell_count,
                "doc_coverage": metrics.doc_coverage_ratio,
            }]

        return generate_letter(metrics_list)

    def _analyze_caqi(self, metrics) -> Dict[str, Any]:
        """Calculate CAQI score."""
        try:
            # Calculate scores from metrics (0-100 scale)
            complexity_score = min(100, metrics.avg_complexity * 10)  # 0-100
            security_score = min(100, (metrics.security_high_count + metrics.security_medium_count) * 5)  # 0-100
            smells_score = min(100, metrics.smell_count * 3)  # 0-100
            docs_score = (1 - metrics.doc_coverage_ratio) * 100  # 0-100 (lower is better)
            duplication_score = metrics.duplication_percentage  # Already 0-100
            coupling_score = min(100, metrics.avg_imports_per_file * 10)  # 0-100

            # Create Pollutants object from metrics
            pollutants = Pollutants(
                complexity=complexity_score,
                security=security_score,
                smells=smells_score,
                docs=docs_score,
                duplication=duplication_score,
                coupling=coupling_score
            )

            return {
                "score": pollutants.caqi_score(),
                "level": pollutants.level(),
                "color": pollutants.color(),
                "primary_pollutant": pollutants.primary_pollutant(),
                "pollutants": pollutants.as_dict()
            }
        except Exception as e:
            # Return default CAQI if calculation fails
            return {
                "score": 350,
                "level": "Unhealthy",
                "color": "#ff9999",
                "primary_pollutant": "unknown",
                "error": str(e)
            }

    def _generate_html_outputs(self, personality: Dict, letter: Dict, caqi: Dict) -> Dict[str, str]:
        """Generate all HTML files."""
        html_files = {
            "personality.html": generate_personality_html(personality),
            "letter.html": render_letter_html(letter),
            "caqi.html": self._generate_caqi_html(caqi),
            "dashboard.html": self._generate_unified_dashboard(personality, letter, caqi)
        }
        return html_files

    def _generate_caqi_html(self, caqi: Dict) -> str:
        """Generate CAQI HTML visualization."""
        score = caqi.get('score', 0)
        level = caqi.get('level', 'Unknown')
        color = caqi.get('color', '#000000')

        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>CAQI Analysis</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .caqi-score {{ font-size: 48px; font-weight: bold; color: {color}; }}
        .caqi-level {{ font-size: 24px; color: {color}; }}
    </style>
</head>
<body>
    <h1>Code Air Quality Index</h1>
    <div class="caqi-score">{score}</div>
    <div class="caqi-level">{level}</div>
    <pre>{json.dumps(caqi, indent=2)}</pre>
</body>
</html>
"""

    def _generate_unified_dashboard(self, personality: Dict, letter: Dict, caqi: Dict) -> str:
        """Generate unified Creative Suite dashboard."""
        dashboard_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Creative Suite Analysis - Unified Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        .header {{
            text-align: center;
            color: white;
            margin-bottom: 60px;
        }}

        .header h1 {{
            font-size: 48px;
            margin-bottom: 10px;
        }}

        .header p {{
            font-size: 18px;
            opacity: 0.9;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }}

        .card {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }}

        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 50px rgba(0,0,0,0.15);
        }}

        .card h2 {{
            font-size: 24px;
            margin-bottom: 15px;
            color: #333;
        }}

        .card-content {{
            font-size: 14px;
            line-height: 1.8;
            color: #666;
        }}

        .card-stat {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            margin: 20px 0;
        }}

        .personality-card {{
            border-left: 5px solid #667eea;
        }}

        .letter-card {{
            border-left: 5px solid #f77f00;
        }}

        .caqi-card {{
            border-left: 5px solid #06d6a0;
        }}

        .emoji {{
            font-size: 48px;
            margin-bottom: 10px;
        }}

        .button-group {{
            text-align: center;
            margin-top: 40px;
        }}

        .button {{
            display: inline-block;
            padding: 12px 30px;
            margin: 10px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s;
            cursor: pointer;
            border: none;
            font-size: 16px;
        }}

        .button-primary {{
            background: white;
            color: #667eea;
        }}

        .button-primary:hover {{
            background: #f0f0f0;
        }}

        .summary {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-top: 40px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}

        .summary h3 {{
            color: #333;
            margin-bottom: 15px;
        }}

        .summary p {{
            color: #666;
            line-height: 1.8;
            margin-bottom: 10px;
        }}

        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 32px;
            }}

            .grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 Creative Suite Analysis</h1>
            <p>Unified Codebase Intelligence Dashboard</p>
        </div>

        <div class="grid">
            <!-- Personality Card -->
            <div class="card personality-card">
                <div class="emoji">{personality.get('emoji', '🤔')}</div>
                <h2>Codebase Personality</h2>
                <p><strong>Archetype:</strong> {personality.get('archetype', 'Unknown')}</p>
                <div class="card-stat">{personality.get('archetype', 'Unknown')}</div>
                <div class="card-content">
                    <p>Traits analyzed across 6 dimensions including complexity, security, documentation, and more.</p>
                    <p style="margin-top: 10px;">View detailed personality analysis for insights into your codebase character.</p>
                </div>
            </div>

            <!-- Inheritance Letter Card -->
            <div class="card letter-card">
                <div class="emoji">📬</div>
                <h2>Inheritance Letter</h2>
                <p><strong>Tone:</strong> {letter.get('tone', 'Cautious').capitalize()}</p>
                <div class="card-stat">{letter.get('tone', 'Cautious').capitalize()}</div>
                <div class="card-content">
                    <p>First-person confessions about code issues, warnings, and guidance.</p>
                    <p style="margin-top: 10px;">Read the letter for honest insights into your codebase from the code itself.</p>
                </div>
            </div>

            <!-- CAQI Card -->
            <div class="card caqi-card">
                <div class="emoji">📊</div>
                <h2>Code Health (CAQI)</h2>
                <p><strong>Score:</strong> {caqi.get('score', 0)}/500</p>
                <div class="card-stat">{caqi.get('band', 'Unknown')}</div>
                <div class="card-content">
                    <p>EPA-style code quality index across 6 pollutant metrics.</p>
                    <p style="margin-top: 10px;">Review health band and pollutant breakdown for improvement priorities.</p>
                </div>
            </div>
        </div>

        <div class="summary">
            <h3>🎯 Unified Analysis Summary</h3>
            <p><strong>Personality Insight:</strong> Your codebase exhibits the "{personality.get('archetype', 'Unknown')}" personality pattern.</p>
            <p><strong>Code Health:</strong> CAQI score of {caqi.get('score', 0)}/500 indicates {caqi.get('band', 'Unknown').lower()} code health status.</p>
            <p><strong>Developer Guidance:</strong> The Inheritance Letter provides {letter.get('tone', 'measured').lower()} guidance with {len(letter.get('secrets', []))} security findings to address.</p>
            <p style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee;">
                All three analyses work together to give you a complete picture of your codebase's character, health, and guidance for improvement.
            </p>
        </div>

        <div class="button-group">
            <a href="personality.html" class="button button-primary">View Personality Profile</a>
            <a href="letter.html" class="button button-primary">Read Inheritance Letter</a>
            <a href="caqi.html" class="button button-primary">View CAQI Health</a>
        </div>
    </div>
</body>
</html>
"""
        return dashboard_html

    def _generate_markdown_report(self, personality: Dict, letter: Dict, caqi: Dict) -> str:
        """Generate markdown report combining all three analyses."""
        report = f"""# Creative Suite Analysis Report

## Overview

**Personality:** {personality.get('archetype', 'Unknown')} {personality.get('emoji', '')}
**Health Score:** {caqi.get('score', 0)}/500 ({caqi.get('band', 'Unknown')})
**Code Tone:** {letter.get('tone', 'Cautious').capitalize()}

---

## 1. Codebase Personality

### Archetype: {personality.get('archetype', 'Unknown')}

{personality.get('description', 'No description available.')}

### Traits (0-100 scale)

| Trait | Score |
|-------|-------|
| Complexity | {personality.get('traits', {}).get('complexity', 'N/A')} |
| Security | {personality.get('traits', {}).get('security', 'N/A')} |
| Duplication | {personality.get('traits', {}).get('duplication', 'N/A')} |
| Coupling | {personality.get('traits', {}).get('coupling', 'N/A')} |
| Documentation | {personality.get('traits', {}).get('documentation', 'N/A')} |
| Perfectionism | {personality.get('traits', {}).get('perfectionism', 'N/A')} |

### Relationship Tips

{self._format_list(personality.get('relationship_tips', []))}

---

## 2. Inheritance Letter

### Tone: {letter.get('tone', 'Cautious').capitalize()}

The codebase speaks to you in a {letter.get('tone', 'measured').lower()} tone, reflecting its overall health and stability.

### What I'm Proud Of

{self._format_list([f"{item.get('filepath', 'File')} - Quality: {item.get('quality', 0)}" for item in letter.get('proud', [])])}

### What I'm Not Proud Of

{self._format_list([f"{item.get('filepath', 'File')} - Quality: {item.get('quality', 0)}" for item in letter.get('not_proud', [])])}

### Secrets I've Been Keeping

{self._format_list([item.get('confession', 'Security issue found') for item in letter.get('secrets', [])])}

### How to Survive Your First Week

{self._format_list(letter.get('tips', []))}

---

## 3. Code Health (CAQI)

### Overall Score: {caqi.get('score', 0)}/500

**Health Band:** {caqi.get('band', 'Unknown')}

### Pollutants

| Pollutant | Score |
|-----------|-------|
| Complexity | {caqi.get('pollutants', {}).get('complexity', 'N/A')} |
| Security | {caqi.get('pollutants', {}).get('security', 'N/A')} |
| Duplication | {caqi.get('pollutants', {}).get('duplication', 'N/A')} |
| Coupling | {caqi.get('pollutants', {}).get('coupling', 'N/A')} |
| Documentation | {caqi.get('pollutants', {}).get('documentation', 'N/A')} |
| Error Handling | {caqi.get('pollutants', {}).get('error_handling', 'N/A')} |

### Health Band Description

{caqi.get('description', 'See CAQI score and pollutants above.')}

---

## Summary

Your codebase presents as a **{personality.get('archetype', 'Unknown')}** with **{caqi.get('band', 'Unknown').lower()} code health**.

The **Inheritance Letter** guides you through the code with a **{letter.get('tone', 'measured').lower()} tone**, indicating it's ready for {letter.get('tone') == 'confident' and 'confident extension' or 'careful improvement'}.

Focus on improving the pollutants that score below 50 to elevate your overall health score.

---

*Generated by Creative Suite Analysis Tool*
*Combining Personality Profiler, Inheritance Letter, and CAQI Health Index*
"""
        return report

    def _format_list(self, items: List[str]) -> str:
        """Format list items for markdown."""
        if not items:
            return "- No items"
        return "\n".join([f"- {item}" for item in items])

    def to_json(self, result: CreativeSuiteResult) -> Dict[str, Any]:
        """Convert result to JSON-serializable dict."""
        return {
            "job_id": result.job_id,
            "timestamp": result.timestamp,
            "codebase_path": result.codebase_path,
            "status": result.status,
            "personality": result.personality,
            "letter": result.letter,
            "caqi": result.caqi,
            "files": result.html_files.keys(),
        }
