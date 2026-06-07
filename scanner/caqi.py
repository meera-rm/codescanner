from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from metrics_aggregator import RepoMetrics


@dataclass
class Pollutants:
    """Six code quality pollutants (0-100 scale)."""
    complexity: float
    security: float
    smells: float
    docs: float
    duplication: float
    coupling: float

    def as_dict(self) -> dict:
        """Return as dictionary."""
        return {
            "complexity": self.complexity,
            "security": self.security,
            "smells": self.smells,
            "docs": self.docs,
            "duplication": self.duplication,
            "coupling": self.coupling,
        }

    def caqi_score(self) -> int:
        """Calculate CAQI (Code Air Quality Index) from pollutants (0-500)."""
        # CAQI = max_pollutant * 3.5 + mean(top_3) * 1.5
        pollutant_list = [
            self.complexity,
            self.security,
            self.smells,
            self.docs,
            self.duplication,
            self.coupling,
        ]

        max_pollutant = max(pollutant_list)
        top_3 = sorted(pollutant_list, reverse=True)[:3]
        top_3_mean = sum(top_3) / len(top_3)

        score = max_pollutant * 3.5 + top_3_mean * 1.5
        return min(500, max(0, int(round(score))))

    def level(self) -> str:
        """Return EPA-style level (Good, Moderate, Unhealthy, etc.)."""
        score = self.caqi_score()

        if score <= 50:
            return "Good"
        elif score <= 100:
            return "Moderate"
        elif score <= 150:
            return "Unhealthy for Sensitive Groups"
        elif score <= 200:
            return "Unhealthy"
        elif score <= 300:
            return "Very Unhealthy"
        else:
            return "Hazardous"

    def color(self) -> str:
        """Return EPA color code for level."""
        level = self.level()
        colors = {
            "Good": "#96c480",
            "Moderate": "#f1f1f0",
            "Unhealthy for Sensitive Groups": "#f1f7f8",
            "Unhealthy": "#ff9999",
            "Very Unhealthy": "#873f97",
            "Hazardous": "#7e9023",
        }
        return colors.get(level, "#000000")

    def primary_pollutant(self) -> str:
        """Return name of worst pollutant."""
        pollutants = [
            ("complexity", self.complexity),
            ("security", self.security),
            ("smells", self.smells),
            ("docs", self.docs),
            ("duplication", self.duplication),
            ("coupling", self.coupling),
        ]
        return max(pollutants, key=lambda x: x[1])[0]

    def health_advice(self) -> str:
        """Return health advice template based on level."""
        level = self.level()
        advice = {
            "Good": "Excellent code health. Focus on maintaining standards.",
            "Moderate": "Code is generally healthy. Address minor concerns.",
            "Unhealthy for Sensitive Groups": "New developers will struggle. Plan onboarding carefully.",
            "Unhealthy": "Active remediation recommended. Schedule refactoring.",
            "Very Unhealthy": "High incident risk. Prioritize security and architecture fixes.",
            "Hazardous": "Health warning of emergency conditions. Do not deploy.",
        }
        return advice.get(level, "Unknown level")


class CAQICalculator:
    """Calculates CAQI scores from repository metrics."""

    def calculate_pollutants(self, metrics: RepoMetrics) -> Pollutants:
        """
        Calculate six pollutants from metrics.

        Args:
            metrics: RepoMetrics from aggregator

        Returns:
            Pollutants with scores 0-100
        """
        complexity = self._calculate_complexity(metrics.avg_complexity, metrics.max_complexity)
        security = self._calculate_security(metrics.security_high_count, metrics.security_medium_count)
        smells = self._calculate_smells(metrics.smell_count)
        docs = self._calculate_docs(metrics.doc_coverage_ratio)
        duplication = self._calculate_duplication(metrics.duplication_percentage)
        coupling = self._calculate_coupling(metrics.avg_imports_per_file, metrics.has_circular_deps)

        return Pollutants(
            complexity=complexity,
            security=security,
            smells=smells,
            docs=docs,
            duplication=duplication,
            coupling=coupling,
        )

    @staticmethod
    def _calculate_complexity(avg: float, max_val: float) -> float:
        """Complexity = min(avg * 20 + max * 10, 100)"""
        score = avg * 20 + max_val * 10
        return min(score, 100.0)

    @staticmethod
    def _calculate_security(high_count: int, medium_count: int) -> float:
        """Security = min(high * 40 + medium * 20, 100)"""
        score = high_count * 40 + medium_count * 20
        return min(score, 100.0)

    @staticmethod
    def _calculate_smells(count: int) -> float:
        """Smells = min(count * 12.5, 100)"""
        score = count * 12.5
        return min(score, 100.0)

    @staticmethod
    def _calculate_docs(coverage_ratio: float) -> float:
        """Docs (inverted) = (1 - coverage_ratio) * 100"""
        return max(0.0, (1.0 - coverage_ratio) * 100.0)

    @staticmethod
    def _calculate_duplication(percentage: float) -> float:
        """Duplication = percentage (capped at 100)"""
        return min(percentage, 100.0)

    @staticmethod
    def _calculate_coupling(avg_imports: float, has_circular: bool) -> float:
        """Coupling = min(avg_imports * 5, 100) + (50 if circular)"""
        score = min(avg_imports * 5, 100.0)
        if has_circular:
            score += 50
        return min(score, 100.0)

    def calculate_per_file_caqi(
        self, metrics: RepoMetrics, pollutants: Pollutants
    ) -> List[Dict]:
        """
        Calculate per-file CAQI scores.

        Uses per-file metrics from aggregator to compute file-level CAQI.
        """
        per_file_results = []

        for filepath, file_metrics in metrics.per_file_metrics.items():
            # Estimate per-file metrics (simplified for MVP)
            file_complexity = 0.0  # Would need per-function data
            file_security = file_metrics.get("security_issues", 0)
            file_smells = file_metrics.get("smells", 0)
            file_docs = 1.0 - file_metrics.get("doc_coverage", 0.0)
            file_duplication = 0.0  # Global metric, not per-file
            file_coupling = 0.0  # Global metric, not per-file

            # Rough per-file CAQI (weighted toward detectable metrics)
            file_security_score = min(file_security * 40, 100.0)
            file_smells_score = min(file_smells * 12.5, 100.0)
            file_docs_score = file_docs * 100

            file_pollutants = [file_security_score, file_smells_score, file_docs_score]
            max_pollutant = max(file_pollutants) if file_pollutants else 0.0
            top_3_mean = sum(sorted(file_pollutants, reverse=True)[:3]) / 3 if file_pollutants else 0.0

            file_caqi = min(500, max(0, int(round(max_pollutant * 3.5 + top_3_mean * 1.5))))

            # Determine level
            if file_caqi <= 50:
                level = "Good"
            elif file_caqi <= 100:
                level = "Moderate"
            elif file_caqi <= 150:
                level = "Unhealthy for Sensitive Groups"
            elif file_caqi <= 200:
                level = "Unhealthy"
            elif file_caqi <= 300:
                level = "Very Unhealthy"
            else:
                level = "Hazardous"

            per_file_results.append(
                {
                    "file": filepath,
                    "caqi": file_caqi,
                    "level": level,
                    "lines": file_metrics.get("lines", 0),
                    "issues": file_metrics.get("security_issues", 0),
                }
            )

        return sorted(per_file_results, key=lambda x: x["caqi"], reverse=True)


class CAQIFormatter:
    """Formats CAQI results for various outputs."""

    @staticmethod
    def json_output(
        pollutants: Pollutants,
        metrics: RepoMetrics,
        per_file: List[Dict],
    ) -> dict:
        """Generate JSON output."""
        primary = pollutants.primary_pollutant()

        return {
            "caqi": {
                "score": pollutants.caqi_score(),
                "level": pollutants.level(),
                "color": pollutants.color(),
                "primary_pollutant": primary,
                "pollutants": pollutants.as_dict(),
                "per_file": per_file[:5],  # Top 5 worst files
                "health_advice": pollutants.health_advice(),
                "metadata": {
                    "files_analyzed": metrics.files_analyzed,
                    "total_lines": metrics.total_lines,
                },
            }
        }

    @staticmethod
    def markdown_summary(pollutants: Pollutants) -> str:
        """Generate markdown one-liner."""
        score = pollutants.caqi_score()
        level = pollutants.level()
        primary = pollutants.primary_pollutant()
        return f"**CAQI: {score} — {level}** | Primary pollutant: **{primary}**"

    @staticmethod
    def markdown_full(
        pollutants: Pollutants,
        metrics: RepoMetrics,
        per_file: List[Dict],
    ) -> str:
        """Generate full markdown report."""
        lines = [
            "## Code Air Quality Index",
            "",
            f"**CAQI: {pollutants.caqi_score()} — {pollutants.level()}**",
            "",
            f"Primary pollutant: **{pollutants.primary_pollutant()}**",
            "",
            "### Pollution Breakdown",
            "",
        ]

        pollutants_dict = pollutants.as_dict()
        labels = {
            "complexity": "Complexity (hard to understand/test)",
            "security": "Security (vulnerabilities & hardcoded secrets)",
            "smells": "Code Smells (long functions, deep nesting)",
            "docs": "Documentation (missing docstrings)",
            "duplication": "Duplication (copy-paste code)",
            "coupling": "Coupling (import dependencies)",
        }

        for key, label in labels.items():
            score = pollutants_dict[key]
            lines.append(f"- {label}: {score:.0f}")

        lines.extend([
            "",
            f"Health advice: {pollutants.health_advice()}",
            "",
            "### Top Files by CAQI",
            "",
        ])

        for i, file_info in enumerate(per_file[:3], 1):
            lines.append(f"{i}. `{file_info['file']}` — CAQI {file_info['caqi']} ({file_info['level']})")

        lines.append("")

        return "\n".join(lines)

    @staticmethod
    def html_gauge(pollutants: Pollutants) -> str:
        """Generate HTML gauge visualization."""
        score = pollutants.caqi_score()
        level = pollutants.level()
        color = pollutants.color()
        percentage = (score / 500) * 100

        html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>CAQI Gauge - {level}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .gauge {{ position: relative; width: 300px; height: 150px; margin: 30px auto; }}
        .gauge-bg {{ position: absolute; width: 100%; height: 100%; background: linear-gradient(to right, #96c480, #f1f1f0, #f1f7f8, #ff9999, #873f97, #7e9023); border-radius: 150px 150px 0 0; }}
        .gauge-value {{ position: absolute; bottom: 10px; left: 50%; transform: translateX(-50%); font-size: 48px; font-weight: bold; color: #333; }}
        .gauge-label {{ position: absolute; bottom: -40px; left: 50%; transform: translateX(-50%); font-size: 20px; font-weight: bold; width: 100%; text-align: center; color: {color}; }}
        .info {{ text-align: center; margin-top: 60px; }}
        .level {{ font-size: 24px; font-weight: bold; color: {color}; margin: 20px 0; }}
        .advice {{ font-size: 16px; color: #666; line-height: 1.6; margin: 20px 0; }}
        .pollutants {{ margin-top: 40px; padding-top: 20px; border-top: 2px solid #eee; }}
        .pollutant-bar {{ margin: 15px 0; }}
        .pollutant-label {{ font-weight: bold; font-size: 14px; margin-bottom: 5px; }}
        .pollutant-meter {{ width: 100%; height: 20px; background: #eee; border-radius: 10px; overflow: hidden; }}
        .pollutant-fill {{ height: 100%; background: linear-gradient(to right, #96c480, #ff9999); transition: width 0.3s; }}
    </style>
</head>
<body>
    <div class="container">
        <h1 style="text-align: center; color: #333;">Code Air Quality Index</h1>

        <div class="gauge">
            <div class="gauge-bg"></div>
            <div class="gauge-value">{score}</div>
            <div class="gauge-label">{level}</div>
        </div>

        <div class="info">
            <p class="advice">{pollutants.health_advice()}</p>
        </div>

        <div class="pollutants">
            <h3>Pollution Breakdown</h3>
            <div class="pollutant-bar">
                <div class="pollutant-label">Complexity: {pollutants.complexity:.0f}</div>
                <div class="pollutant-meter">
                    <div class="pollutant-fill" style="width: {pollutants.complexity}%"></div>
                </div>
            </div>
            <div class="pollutant-bar">
                <div class="pollutant-label">Security: {pollutants.security:.0f}</div>
                <div class="pollutant-meter">
                    <div class="pollutant-fill" style="width: {pollutants.security}%"></div>
                </div>
            </div>
            <div class="pollutant-bar">
                <div class="pollutant-label">Code Smells: {pollutants.smells:.0f}</div>
                <div class="pollutant-meter">
                    <div class="pollutant-fill" style="width: {pollutants.smells}%"></div>
                </div>
            </div>
            <div class="pollutant-bar">
                <div class="pollutant-label">Documentation: {pollutants.docs:.0f}</div>
                <div class="pollutant-meter">
                    <div class="pollutant-fill" style="width: {pollutants.docs}%"></div>
                </div>
            </div>
            <div class="pollutant-bar">
                <div class="pollutant-label">Duplication: {pollutants.duplication:.0f}</div>
                <div class="pollutant-meter">
                    <div class="pollutant-fill" style="width: {pollutants.duplication}%"></div>
                </div>
            </div>
            <div class="pollutant-bar">
                <div class="pollutant-label">Coupling: {pollutants.coupling:.0f}</div>
                <div class="pollutant-meter">
                    <div class="pollutant-fill" style="width: {pollutants.coupling}%"></div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''
        return html
