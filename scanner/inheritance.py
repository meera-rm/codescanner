"""
Inheritance Letter Generator - Creative Path H

Generates a first-person letter from a codebase to its next developer.
The letter confesses mistakes, warns of dangers, and suggests safe entry points.

No external dependencies. Pure Python, rule-based logic only.
"""

from typing import List, Dict, Any, Optional


# TONE SELECTION LOGIC
def select_tone(metrics_list: List[Dict[str, Any]]) -> str:
    """
    Select tone (apologetic/cautious/confident) based on aggregated metrics.

    Uses first-match priority order:
    1. Apologetic if: security_high_count ≥ 1 OR avg_quality < 55
    2. Cautious if: avg_quality 55-74 OR total_smells > 10
    3. Confident if: avg_quality ≥ 75 AND security clean AND smells ≤ 5
    4. Fallback: Cautious

    Args:
        metrics_list: List of per-file metrics dicts

    Returns:
        "apologetic", "cautious", or "confident"
    """
    if not metrics_list:
        return "cautious"

    # Aggregate metrics
    total_files = len(metrics_list)
    security_high_count = sum(
        len(f.get("security_findings", {}).get("high", []))
        for f in metrics_list
    )
    total_smells = sum(
        f.get("smells_count", 0)
        for f in metrics_list
    )
    avg_quality = sum(
        f.get("quality_score", 50) for f in metrics_list
    ) / total_files if total_files > 0 else 50

    # Priority 1: Apologetic
    if security_high_count >= 1 or avg_quality < 55:
        return "apologetic"

    # Priority 2: Cautious
    if (55 <= avg_quality <= 74) or total_smells > 10:
        return "cautious"

    # Priority 3: Confident
    security_clean = security_high_count == 0
    if avg_quality >= 75 and security_clean and total_smells <= 5:
        return "confident"

    # Fallback
    return "cautious"


# SECTION BUILDERS
def build_proud_section(metrics_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Identify top 3 files to be proud of.

    Selection: Top 3 files by quality_score (if available);
    else lowest complexity + has error handling.

    Returns:
        List of dicts: {"file": str, "quality": int, "reason": str}
    """
    if not metrics_list:
        return []

    # Sort by quality_score descending
    sorted_files = sorted(
        metrics_list,
        key=lambda f: f.get("quality_score", 0),
        reverse=True
    )

    proud = []
    for f in sorted_files[:3]:
        proud.append({
            "file": f.get("filepath", "unknown"),
            "quality": f.get("quality_score", 0),
            "reason": f"Quality score: {f.get('quality_score', 0)}/100"
        })

    return proud


def build_not_proud_section(metrics_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Identify top 3 files with worst metrics.

    Selection: Lowest quality_score, highest complexity, most smells.

    Returns:
        List of dicts: {"file": str, "quality": int, "issue": str}
    """
    if not metrics_list:
        return []

    # Sort by quality_score ascending (worst first)
    sorted_files = sorted(
        metrics_list,
        key=lambda f: f.get("quality_score", 100)
    )

    not_proud = []
    for f in sorted_files[:3]:
        quality = f.get("quality_score", 0)
        complexity = f.get("complexity_average", 0)
        smells = f.get("smells_count", 0)

        issue = "Low quality"
        if complexity > 5:
            issue = f"Complex ({complexity:.1f} avg)"
        if smells > 0:
            issue = f"{smells} code smells"

        not_proud.append({
            "file": f.get("filepath", "unknown"),
            "quality": quality,
            "issue": issue
        })

    return not_proud


def build_secrets_section(metrics_list: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Extract high-severity security findings as confessions.

    Returns:
        List of dicts: {"file": str, "line": int, "confession": str}
    """
    secrets = []

    for f in metrics_list:
        filepath = f.get("filepath", "unknown")
        high_findings = f.get("security_findings", {}).get("high", [])

        for finding in high_findings:
            confession = f"I left a {finding.get('type', 'security issue')} in {filepath}"
            if "line" in finding:
                confession += f" (line {finding['line']})"
            confession += ". I'm sorry."

            secrets.append({
                "file": filepath,
                "line": finding.get("line", 0),
                "confession": confession
            })

    return secrets


def build_avoid_section(metrics_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Identify top 3 complex functions to avoid first.

    Selection: Top 3 by cyclomatic complexity.
    Fallback: If < 3 functions, return what exists.

    Returns:
        List of dicts: {"function": str, "file": str, "complexity": float}
    """
    avoid = []

    for f in metrics_list:
        filepath = f.get("filepath", "unknown")
        functions = f.get("functions", [])

        for func in functions:
            avoid.append({
                "function": func.get("name", "unknown"),
                "file": filepath,
                "complexity": func.get("complexity", 1)
            })

    # Sort by complexity descending
    avoid = sorted(avoid, key=lambda x: x["complexity"], reverse=True)

    # Return top 3 (or fewer if not enough)
    return avoid[:3]


def build_start_here_section(metrics_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Identify safe entry points for new developers.

    Selection: 1-2 files where complexity ≤ 3, no security findings,
    has error handling, quality > 70.

    Fallback: If no clean files, recommend lowest-complexity file.

    Returns:
        List of dicts: {"file": str, "complexity": float, "reason": str}
    """
    # Find candidates: complexity ≤ 3, no security, quality > 70
    candidates = [
        f for f in metrics_list
        if f.get("complexity_average", 0) <= 3
        and len(f.get("security_findings", {}).get("high", [])) == 0
        and f.get("quality_score", 0) > 70
    ]

    # Sort by complexity ascending
    candidates = sorted(candidates, key=lambda x: x.get("complexity_average", 0))

    start_here = []
    for f in candidates[:2]:
        start_here.append({
            "file": f.get("filepath", "unknown"),
            "complexity": f.get("complexity_average", 0),
            "reason": "Safe entry point: low complexity, clean"
        })

    # Fallback: If no candidates, use lowest complexity file
    if not start_here and metrics_list:
        fallback = sorted(metrics_list, key=lambda x: x.get("complexity_average", 0))[0]
        start_here.append({
            "file": fallback.get("filepath", "unknown"),
            "complexity": fallback.get("complexity_average", 0),
            "reason": "All entry points are complex; start here anyway"
        })

    return start_here


def build_first_week_tips(metrics_list: List[Dict[str, Any]], tone: str) -> List[str]:
    """
    Generate actionable first-week tips based on tone and actual codebase metrics.
    Tips are personalized to this specific codebase's dominant issues.

    Args:
        metrics_list: List of metrics (can be per-file or aggregate)
        tone: "apologetic", "cautious", or "confident"

    Returns:
        List of 3 actionable tips
    """
    tips = []

    if not metrics_list:
        # Fallback generic tips
        return [
            "Start by reading documentation and setup guides",
            "Run tests to understand the codebase behavior",
            "Ask team members about key components"
        ]

    # Analyze metrics to find dominant issues
    total_files = len(metrics_list)
    avg_quality = sum(f.get("quality_score", 50) for f in metrics_list) / total_files if total_files > 0 else 50
    total_smells = sum(f.get("smells_count", 0) for f in metrics_list)
    avg_complexity = sum(f.get("complexity_average", 1.0) for f in metrics_list) / total_files if total_files > 0 else 1.0
    doc_coverage = sum(f.get("doc_coverage", 0.5) for f in metrics_list) / total_files if total_files > 0 else 0.5
    security_issues = sum(len(f.get("security_findings", {}).get("high", [])) for f in metrics_list)

    # Determine primary issues
    has_high_complexity = avg_complexity > 8
    has_low_docs = doc_coverage < 0.5
    has_smells = total_smells > 5
    has_security = security_issues > 0
    has_low_quality = avg_quality < 60

    if tone == "apologetic":
        # High priority: security and critical issues
        if has_security:
            tips.append(f"🚨 Fix {security_issues} security issue(s) immediately - audit your code")
        elif has_low_quality:
            tips.append("Start with critical fixes in the lowest-quality code sections")
        else:
            tips.append("Enable pre-commit hooks to catch issues before they spread")

        if has_smells:
            tips.append(f"Address {total_smells} code smells via systematic refactoring")
        elif has_high_complexity:
            tips.append("Break down complex functions to improve maintainability")
        else:
            tips.append("Improve test coverage for fragile areas")

        if has_low_docs:
            tips.append("Document critical functions - this code needs clarity")
        else:
            tips.append("Pair program with the team on risky areas")

    elif tone == "cautious":
        # Medium priority: improvements and careful refactoring
        if has_high_complexity:
            tips.append(f"Refactor complex functions (avg complexity: {avg_complexity:.1f} - target <10)")
        elif has_low_docs:
            tips.append(f"Add docstrings - {int((1-doc_coverage)*100)}% of code lacks documentation")
        else:
            tips.append("Understand patterns in high-quality files before making changes")

        if has_smells:
            tips.append(f"Refactor to fix {total_smells} code smells and improve quality")
        elif has_low_quality:
            tips.append("Incrementally improve code quality with small refactors")
        else:
            tips.append("Run tests frequently - they catch subtle regressions")

        if has_low_docs and not has_high_complexity:
            tips.append("Document the main entry points first")
        elif has_high_complexity and not has_low_docs:
            tips.append("Extract smaller functions from the complex ones")
        else:
            tips.append("Study existing patterns before writing new code")

    elif tone == "confident":
        # Low priority: growth and optimization
        if avg_complexity > 5:
            tips.append(f"Optimize high-complexity areas (avg: {avg_complexity:.1f})")
        else:
            tips.append("Review architecture - identify patterns to reinforce")

        if total_smells > 0:
            tips.append(f"Eliminate {total_smells} code smells to reach A grade")
        elif doc_coverage < 1.0:
            tips.append("Complete documentation coverage - add examples")
        else:
            tips.append("Write integration tests - this code is solid")

        tips.append("Share knowledge - mentor others on your patterns")

    # Ensure we have exactly 3 tips (fallback if something went wrong)
    if len(tips) < 3:
        tips.extend([
            "Read documentation thoroughly",
            "Understand the test suite first",
            "Ask team members for context"
        ])

    return tips[:3]  # Return first 3 tips


def generate_letter(metrics_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate complete inheritance letter from metrics.

    Args:
        metrics_list: List of per-file metrics dicts

    Returns:
        Dict with: tone, proud, not_proud, secrets, avoid, start_here, tips, sign_off
    """
    tone = select_tone(metrics_list)

    return {
        "tone": tone,
        "proud": build_proud_section(metrics_list),
        "not_proud": build_not_proud_section(metrics_list),
        "secrets": build_secrets_section(metrics_list),
        "avoid": build_avoid_section(metrics_list),
        "start_here": build_start_here_section(metrics_list),
        "first_week_tips": build_first_week_tips(metrics_list, tone),
        "sign_off": _get_sign_off(tone)
    }


def _get_sign_off(tone: str) -> str:
    """Get tone-matched sign-off."""
    sign_offs = {
        "apologetic": "Yours apologetically,",
        "cautious": "Yours cautiously,",
        "confident": "Yours confidently,"
    }
    return sign_offs.get(tone, "Yours cautiously,")


def render_letter_markdown(letter: Dict[str, Any]) -> str:
    """
    Render letter as Markdown.

    Args:
        letter: Dict from generate_letter()

    Returns:
        Markdown-formatted letter
    """
    lines = [
        "# Inheritance Letter",
        "",
        f"**Tone:** {letter['tone'].capitalize()}",
        "",
    ]

    # What I'm proud of
    if letter.get("proud"):
        lines.append("## What I'm Proud Of")
        lines.append("")
        for item in letter["proud"]:
            lines.append(f"- **{item['file']}**: {item['reason']}")
        lines.append("")

    # What I'm not proud of
    if letter.get("not_proud"):
        lines.append("## What I'm Not Proud Of")
        lines.append("")
        for item in letter["not_proud"]:
            lines.append(f"- **{item['file']}**: {item['issue']}")
        lines.append("")

    # Secrets
    if letter.get("secrets"):
        lines.append("## Secrets I've Been Keeping")
        lines.append("")
        for item in letter["secrets"]:
            lines.append(f"- {item['confession']}")
        lines.append("")
    else:
        lines.append("## Secrets I've Been Keeping")
        lines.append("")
        lines.append("I have no secrets I'm aware of.")
        lines.append("")

    # Rooms to avoid
    if letter.get("avoid"):
        lines.append("## Rooms You Should Avoid First")
        lines.append("")
        for item in letter["avoid"]:
            lines.append(f"- **{item['function']}** in {item['file']} (complexity: {item['complexity']:.1f})")
        lines.append("")

    # Where to start
    if letter.get("start_here"):
        lines.append("## Where to Start Instead")
        lines.append("")
        for item in letter["start_here"]:
            lines.append(f"- **{item['file']}**: {item['reason']}")
        lines.append("")

    # First week tips
    if letter.get("first_week_tips"):
        lines.append("## How to Survive Your First Week")
        lines.append("")
        for i, tip in enumerate(letter["first_week_tips"], 1):
            lines.append(f"{i}. {tip}")
        lines.append("")

    # Sign-off
    lines.append(letter["sign_off"])
    lines.append("A codebase that knows too much about itself")

    return "\n".join(lines)


def compare_letter_tones(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare two letters to show tone shift and improvements.

    Args:
        before: Letter dict before fixes
        after: Letter dict after fixes

    Returns:
        Dict with: tone_changed, before_tone, after_tone, summary_line
    """
    tone_changed = before.get("tone") != after.get("tone")

    summary = f"Tone shifted from {before.get('tone')} to {after.get('tone')}"

    # Count secrets change
    secrets_before = len(before.get("secrets", []))
    secrets_after = len(after.get("secrets", []))
    if secrets_before > secrets_after:
        summary += f" — {secrets_before - secrets_after} fewer secrets"

    return {
        "tone_changed": tone_changed,
        "before_tone": before.get("tone"),
        "after_tone": after.get("tone"),
        "summary_line": summary
    }


def render_letter_html(letter: Dict[str, Any]) -> str:
    """
    Render letter as self-contained HTML with tone-matched styling.

    Features:
    - Inline CSS (no external dependencies)
    - Tone colors: apologetic=red, cautious=amber, confident=green
    - Secrets section visually distinct with background color
    - Printable and responsive design
    - Readable from 10 feet away (18px+ fonts)

    Args:
        letter: Dict from generate_letter()

    Returns:
        Complete HTML document as string
    """
    tone = letter.get("tone", "cautious")

    # Color schemes by tone
    tone_colors = {
        "apologetic": {"primary": "#e63946", "light": "#f8d7da", "dark": "#a4161a"},
        "cautious": {"primary": "#f77f00", "light": "#ffe8c7", "dark": "#d66400"},
        "confident": {"primary": "#06d6a0", "light": "#d4f4e8", "dark": "#028a61"}
    }
    colors = tone_colors.get(tone, tone_colors["cautious"])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inheritance Letter - {tone.capitalize()}</title>
    <style>
        * {{margin: 0; padding: 0; box-sizing: border-box;}}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: linear-gradient(135deg, {colors['primary']} 0%, {colors['dark']} 100%);
            min-height: 100vh;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        .container {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 900px;
            width: 100%;
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, {colors['primary']} 0%, {colors['dark']} 100%);
            color: white;
            padding: 60px 40px;
            text-align: center;
        }}
        .header h1 {{font-size: 40px; margin-bottom: 15px; font-weight: 700;}}
        .header .tone {{font-size: 18px; opacity: 0.95; font-weight: 500;}}
        .content {{padding: 50px 40px;}}
        .section {{margin-bottom: 50px;}}
        .section h2 {{
            font-size: 22px;
            color: {colors['dark']};
            margin-bottom: 25px;
            padding-bottom: 10px;
            border-bottom: 3px solid {colors['primary']};
        }}
        ul {{list-style: none;}}
        li {{padding: 15px 0; border-bottom: 1px solid #eee; color: #555; line-height: 1.6;}}
        li:last-child {{border-bottom: none;}}
        .file-name {{font-weight: 600; color: {colors['dark']};}}
        .metric {{color: {colors['primary']}; font-weight: 600;}}
        .secrets-section {{
            background: {colors['light']};
            padding: 25px;
            border-left: 5px solid {colors['primary']};
            border-radius: 4px;
            margin-bottom: 20px;
        }}
        .secret-item {{padding: 12px 0; color: #333; line-height: 1.6;}}
        .secret-item:not(:last-child) {{border-bottom: 1px solid rgba(0,0,0,0.1);}}
        .tips-list {{counter-reset: tip-counter; list-style: none;}}
        .tips-list li {{counter-increment: tip-counter; padding: 15px 0 15px 40px; position: relative;}}
        .tips-list li:before {{
            content: counter(tip-counter);
            position: absolute;
            left: 0;
            top: 12px;
            width: 28px;
            height: 28px;
            background: {colors['primary']};
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 14px;
        }}
        .empty-section {{padding: 20px; background: #f9f9f9; border-radius: 4px; color: #999; font-style: italic;}}
        .footer {{
            background: #f5f5f5;
            padding: 30px 40px;
            text-align: center;
            color: #666;
            font-size: 12px;
            border-top: 1px solid #eee;
        }}
        .sign-off {{margin-top: 30px; font-weight: 500; color: {colors['dark']}; font-size: 14px;}}
        @media (max-width: 768px) {{
            .header {{padding: 40px 20px;}}
            .header h1 {{font-size: 28px;}}
            .content {{padding: 30px 20px;}}
            .section h2 {{font-size: 18px;}}
        }}
        @media print {{
            body {{background: white; padding: 0;}}
            .container {{box-shadow: none; border-radius: 0;}}
            .header {{padding: 40px;}}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Inheritance Letter</h1>
            <div class="tone">Tone: <span style="text-transform: capitalize;">{tone}</span></div>
        </div>
        <div class="content">
"""

    # Proud section
    if letter.get("proud"):
        html += "            <div class=\"section\">\n                <h2>What I'm Proud Of</h2>\n                <ul>\n"
        for item in letter["proud"]:
            html += f"                    <li><span class=\"file-name\">{item['file']}</span>: {item['reason']}</li>\n"
        html += "                </ul>\n            </div>\n"

    # Not proud section
    if letter.get("not_proud"):
        html += "            <div class=\"section\">\n                <h2>What I'm Not Proud Of</h2>\n                <ul>\n"
        for item in letter["not_proud"]:
            html += f"                    <li><span class=\"file-name\">{item['file']}</span>: {item['issue']}</li>\n"
        html += "                </ul>\n            </div>\n"

    # Secrets section
    html += "            <div class=\"section\">\n                <h2>Secrets I've Been Keeping</h2>\n"
    if letter.get("secrets"):
        for item in letter["secrets"]:
            html += f"                <div class=\"secrets-section\">\n                    <div class=\"secret-item\">{item['confession']}</div>\n                </div>\n"
    else:
        html += "                <div class=\"empty-section\">I have no secrets I'm aware of.</div>\n"
    html += "            </div>\n"

    # Avoid section
    if letter.get("avoid"):
        html += "            <div class=\"section\">\n                <h2>Rooms You Should Avoid First</h2>\n                <ul>\n"
        for item in letter["avoid"]:
            html += f"                    <li><span class=\"file-name\">{item['function']}</span> in {item['file']} <span class=\"metric\">(complexity: {item['complexity']:.1f})</span></li>\n"
        html += "                </ul>\n            </div>\n"

    # Start here section
    if letter.get("start_here"):
        html += "            <div class=\"section\">\n                <h2>Where to Start Instead</h2>\n                <ul>\n"
        for item in letter["start_here"]:
            html += f"                    <li><span class=\"file-name\">{item['file']}</span>: {item['reason']}</li>\n"
        html += "                </ul>\n            </div>\n"

    # First week tips
    if letter.get("first_week_tips"):
        html += "            <div class=\"section\">\n                <h2>How to Survive Your First Week</h2>\n                <ul class=\"tips-list\">\n"
        for tip in letter["first_week_tips"]:
            html += f"                    <li>{tip}</li>\n"
        html += "                </ul>\n            </div>\n"

        html += f"            <div class=\"sign-off\">\n                {letter['sign_off']}<br>\n                A codebase that knows too much about itself\n            </div>\n"

    html += """        </div>
        <div class="footer">
            Generated by Code Scanner - Inheritance Letter (Creative Path H)
        </div>
    </div>
</body>
</html>
"""

    return html
