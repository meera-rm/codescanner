"""
Codebase Personality Profiler
Rule-based personality matching assigns archetypes to codebases based on metrics.
No LLM calls - templates and rule-based logic only.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Archetype:
    """Represents a codebase archetype."""
    name: str
    emoji: str
    tagline: str
    primary_traits: List[str]


# Define the 6 archetypes
ARCHETYPES = {
    "anxious_overthinker": Archetype(
        name="The Anxious Overthinker",
        emoji="🤔",
        tagline="Logs everything, trusts nothing.",
        primary_traits=["overthinking", "anxiety"]
    ),
    "reckless_optimist": Archetype(
        name="The Reckless Optimist",
        emoji="🚀",
        tagline="Ships fast, secrets faster.",
        primary_traits=["recklessness"]
    ),
    "copy_paste_artist": Archetype(
        name="The Copy-Paste Artist",
        emoji="📋",
        tagline="Why write twice what you can paste thrice?",
        primary_traits=["duplication"]
    ),
    "chaotic_connector": Archetype(
        name="The Chaotic Connector",
        emoji="🔀",
        tagline="Everything depends on everything.",
        primary_traits=["chaos"]
    ),
    "cautious_perfectionist": Archetype(
        name="The Cautious Perfectionist",
        emoji="✅",
        tagline="Measure twice, commit once.",
        primary_traits=["perfectionism"]
    ),
    "quiet_newcomer": Archetype(
        name="The Quiet Newcomer",
        emoji="🤐",
        tagline="Small codebase, neutral scores.",
        primary_traits=[]
    ),
}


def compute_trait_scores(metrics: Dict) -> Dict[str, float]:
    """
    Compute the 6 trait scores from metrics.

    Args:
        metrics: RepoMetrics dict with all quality metrics

    Returns:
        Dict with trait scores (0-100 scale)
    """
    # Extract metrics with safe defaults
    avg_complexity = metrics.get("avg_complexity", 0.0)
    max_complexity = metrics.get("max_complexity", 0.0)
    security_high = metrics.get("security_high_count", 0)
    smell_count = metrics.get("smell_count", 0)
    doc_coverage = metrics.get("doc_coverage_ratio", 0.5)
    duplication = metrics.get("duplication_percentage", 0.0)
    circular_dep_count = metrics.get("circular_dep_count", 0)
    avg_imports = metrics.get("avg_imports_per_file", 0.0)
    total_logging = metrics.get("total_logging", 0)
    total_functions = metrics.get("total_functions", 1)
    error_handling = metrics.get("error_handling_density", 0.0)
    quality_score = metrics.get("avg_quality_score", 50.0)

    # Avoid division by zero
    if total_functions == 0:
        total_functions = 1

    # Trait formulas (from RESEARCH.md)
    overthinking = min(100, avg_complexity * 25 + max_complexity * 5)
    anxiety = min(100, (total_logging / max(total_functions, 1)) * 8 + smell_count)
    recklessness = min(100, security_high * 30 + max(0, 100 - error_handling))
    secrecy = min(100, (1 - doc_coverage) * 100) if doc_coverage > 0 else 50
    chaos = min(100, circular_dep_count * 40 + avg_imports / 5)
    perfectionism = quality_score  # 0-100

    return {
        "overthinking": overthinking,
        "anxiety": anxiety,
        "recklessness": recklessness,
        "secrecy": secrecy,
        "chaos": chaos,
        "perfectionism": perfectionism,
    }


def match_archetype(trait_scores: Dict[str, float], metrics: Dict) -> Archetype:
    """
    Match the best archetype based on trait scores and metrics.

    Tie-break order: Overthinking → Recklessness → Secrecy → Duplication → Chaos → Perfectionism
    Fallback: Quiet Newcomer (for small/neutral codebases)

    Args:
        trait_scores: Dict of trait scores
        metrics: RepoMetrics dict

    Returns:
        Matched Archetype
    """
    duplication = metrics.get("duplication_percentage", 0.0)
    total_lines = metrics.get("total_lines", 0)

    # Check for fallback: small codebase with neutral scores
    if total_lines < 1000 and all(0 <= s <= 40 for s in trait_scores.values()):
        return ARCHETYPES["quiet_newcomer"]

    # Tie-break order
    tie_break_order = [
        ("overthinking", ARCHETYPES["anxious_overthinker"]),
        ("recklessness", ARCHETYPES["reckless_optimist"]),
        ("secrecy", ARCHETYPES["copy_paste_artist"]),  # Note: secrecy used as placeholder
        ("chaos", ARCHETYPES["chaotic_connector"]),
        ("perfectionism", ARCHETYPES["cautious_perfectionist"]),
    ]

    # Check for duplication-based archetype first
    if duplication >= 18:
        return ARCHETYPES["copy_paste_artist"]

    # Find highest trait
    max_trait = max(trait_scores.items(), key=lambda x: x[1])
    max_trait_name, max_score = max_trait

    # Match by highest trait
    trait_to_archetype = {
        "overthinking": ARCHETYPES["anxious_overthinker"],
        "recklessness": ARCHETYPES["reckless_optimist"],
        "secrecy": ARCHETYPES["copy_paste_artist"],
        "chaos": ARCHETYPES["chaotic_connector"],
        "perfectionism": ARCHETYPES["cautious_perfectionist"],
        "anxiety": ARCHETYPES["anxious_overthinker"],
    }

    archetype = trait_to_archetype.get(max_trait_name, ARCHETYPES["quiet_newcomer"])

    # If all traits are low, return Quiet Newcomer
    if max_score < 20:
        return ARCHETYPES["quiet_newcomer"]

    return archetype


def build_evidence(metrics: Dict, archetype: Archetype) -> List[Dict]:
    """
    Build evidence citations for the archetype.
    Extract top metrics that support the archetype.

    Args:
        metrics: RepoMetrics dict
        archetype: Matched Archetype

    Returns:
        List of evidence dicts with file, signal, value
    """
    evidence = []
    per_file = metrics.get("per_file_metrics", {})

    # Based on archetype, pick supporting evidence
    if archetype == ARCHETYPES["anxious_overthinker"]:
        # High complexity and logging
        if metrics.get("avg_complexity", 0) > 2:
            evidence.append({
                "metric": "complexity_average",
                "value": round(metrics.get("avg_complexity", 0), 2),
                "context": "high average complexity"
            })
        if metrics.get("total_logging", 0) > 10:
            evidence.append({
                "metric": "logging_count",
                "value": metrics.get("total_logging", 0),
                "context": "extensive logging"
            })

    elif archetype == ARCHETYPES["reckless_optimist"]:
        # Security findings and low error handling
        if metrics.get("security_high_count", 0) > 0:
            evidence.append({
                "metric": "security_issues",
                "value": metrics.get("security_high_count", 0),
                "context": "high-severity security findings"
            })
        if metrics.get("error_handling_density", 0) < 30:
            evidence.append({
                "metric": "error_handling_density",
                "value": round(metrics.get("error_handling_density", 0), 2),
                "context": "low error handling coverage"
            })

    elif archetype == ARCHETYPES["copy_paste_artist"]:
        # Duplication
        if metrics.get("duplication_percentage", 0) >= 18:
            evidence.append({
                "metric": "duplication_percentage",
                "value": round(metrics.get("duplication_percentage", 0), 1),
                "context": "significant code duplication"
            })

    elif archetype == ARCHETYPES["chaotic_connector"]:
        # Circular dependencies and high coupling
        if metrics.get("circular_dep_count", 0) > 0:
            evidence.append({
                "metric": "circular_dependencies",
                "value": metrics.get("circular_dep_count", 0),
                "context": "circular module dependencies"
            })
        if metrics.get("avg_imports_per_file", 0) > 5:
            evidence.append({
                "metric": "avg_imports_per_file",
                "value": round(metrics.get("avg_imports_per_file", 0), 1),
                "context": "high import count per file"
            })

    elif archetype == ARCHETYPES["cautious_perfectionist"]:
        # High quality, clean security, good docs
        if metrics.get("avg_quality_score", 0) >= 85:
            evidence.append({
                "metric": "quality_score",
                "value": round(metrics.get("avg_quality_score", 0), 1),
                "context": "high overall quality score"
            })
        if metrics.get("doc_coverage_ratio", 0) >= 0.7:
            evidence.append({
                "metric": "doc_coverage",
                "value": round(metrics.get("doc_coverage_ratio", 0) * 100, 1),
                "context": "excellent documentation coverage"
            })

    return evidence


def generate_relationship_tips(archetype: Archetype, evidence: List[Dict]) -> List[str]:
    """
    Generate 3 actionable relationship tips based on archetype and evidence.

    Args:
        archetype: Matched Archetype
        evidence: List of evidence citations

    Returns:
        List of 3 tip strings
    """
    tips = {
        "anxious_overthinker": [
            "Pair with a reviewer who asks 'can this be simpler?'",
            "Break down complex functions into smaller, testable units",
            "Document the 'why' behind complex logic — future you will thank you"
        ],
        "reckless_optimist": [
            "Add a pre-commit security scan to catch secrets before commit",
            "Implement comprehensive error handling for all I/O and network calls",
            "Slow down: for every feature, add a security test"
        ],
        "copy_paste_artist": [
            "Extract duplicated code into shared utility functions",
            "Use a linter to flag identical blocks (pylint --duplicate-code)",
            "Refactor before adding features — DRY (Don't Repeat Yourself)"
        ],
        "chaotic_connector": [
            "Draw a module dependency graph; identify circular deps and break them",
            "Apply the Single Responsibility Principle — each module should do one thing",
            "Implement a facade pattern to reduce cross-module coupling"
        ],
        "cautious_perfectionist": [
            "Keep up the excellent documentation — it's your secret weapon",
            "Share your testing patterns with the team; they're a model for others",
            "Mentor on code quality — your standards raise the bar"
        ],
        "quiet_newcomer": [
            "As the codebase grows, establish coding standards early",
            "Document architectural decisions while they're fresh",
            "Set up pre-commit hooks to enforce quality from the start"
        ],
    }

    # Map archetype name to key
    archetype_name = archetype.name
    if "Anxious" in archetype_name:
        archetype_key = "anxious_overthinker"
    elif "Reckless" in archetype_name:
        archetype_key = "reckless_optimist"
    elif "Copy-Paste" in archetype_name:
        archetype_key = "copy_paste_artist"
    elif "Chaotic" in archetype_name:
        archetype_key = "chaotic_connector"
    elif "Cautious" in archetype_name:
        archetype_key = "cautious_perfectionist"
    else:
        archetype_key = "quiet_newcomer"

    return tips.get(archetype_key, tips["quiet_newcomer"])


def generate_personality_markdown_section(personality: Dict) -> str:
    """
    Generate Markdown section for personality profile.

    Args:
        personality: Personality profile dict from profile_codebase()

    Returns:
        Markdown string for inclusion in reports
    """
    archetype = personality["archetype"]
    emoji = personality["emoji"]
    tagline = personality["tagline"]
    trait_scores = personality["trait_scores"]
    evidence = personality["evidence"]
    strengths = personality["strengths"]
    blind_spots = personality["blind_spots"]
    tips = personality["relationship_tips"]

    lines = [
        "## Codebase Personality",
        "",
        f"### Archetype: {emoji} {archetype}",
        f'**"{tagline}"**',
        "",
        "### Trait Profile",
        "| Trait | Score |",
        "|-------|-------|",
    ]

    # Add trait scores in descending order
    sorted_traits = sorted(trait_scores.items(), key=lambda x: x[1], reverse=True)
    for trait, score in sorted_traits:
        # Format trait name nicely
        trait_name = trait.replace("_", " ").title()
        lines.append(f"| {trait_name} | {int(score)} |")

    lines.extend([
        "",
        "### Evidence",
    ])

    if evidence:
        for item in evidence:
            metric = item.get("metric", "unknown")
            value = item.get("value", "")
            context = item.get("context", "")
            lines.append(f"- `{metric}`: {value} ({context})")
    else:
        lines.append("- No specific evidence available")

    lines.extend([
        "",
        "### Strengths",
    ])
    for strength in strengths:
        lines.append(f"- {strength}")

    lines.extend([
        "",
        "### Blind Spots",
    ])
    for blind in blind_spots:
        lines.append(f"- {blind}")

    lines.extend([
        "",
        "### Relationship Tips for Developers",
    ])
    for i, tip in enumerate(tips, 1):
        lines.append(f"{i}. {tip}")

    return "\n".join(lines)


def compare_personalities(before: Dict, after: Dict) -> Dict:
    """
    Compare two personality profiles and show the shift.

    Args:
        before: Before personality profile dict
        after: After personality profile dict

    Returns:
        Comparison dict with archetype_changed, trait_deltas, summary_line
    """
    archetype_changed = before["archetype"] != after["archetype"]
    archetype_shift = ""
    if archetype_changed:
        archetype_shift = f"{before['emoji']} {before['archetype']} → {after['emoji']} {after['archetype']}"

    # Calculate trait deltas
    trait_deltas = {}
    before_scores = before.get("trait_scores", {})
    after_scores = after.get("trait_scores", {})

    for trait in before_scores:
        before_score = before_scores.get(trait, 0)
        after_score = after_scores.get(trait, 0)
        delta = after_score - before_score
        if delta != 0:
            trait_deltas[trait] = {
                "before": before_score,
                "after": after_score,
                "delta": delta,
                "direction": "↑" if delta > 0 else "↓",
            }

    # Find biggest change
    if trait_deltas:
        biggest_change = max(
            trait_deltas.items(),
            key=lambda x: abs(x[1]["delta"])
        )
        trait_name = biggest_change[0].replace("_", " ").title()
        delta_value = biggest_change[1]["delta"]
        direction = biggest_change[1]["direction"]

        summary_line = f"{direction} {trait_name} changed by {abs(int(delta_value))} points"
        if archetype_changed:
            summary_line += f" (archetype: {archetype_shift})"
    else:
        summary_line = "No changes detected between profiles"

    return {
        "archetype_changed": archetype_changed,
        "archetype_before": before["archetype"],
        "archetype_after": after["archetype"],
        "archetype_shift": archetype_shift,
        "trait_deltas": trait_deltas,
        "summary_line": summary_line,
    }


def generate_personality_html(personality: Dict) -> str:
    """
    Generate self-contained HTML personality card.

    Args:
        personality: Personality profile dict from profile_codebase()

    Returns:
        Complete HTML string (single file, inline CSS, no external deps)
    """
    archetype = personality["archetype"]
    emoji = personality["emoji"]
    tagline = personality["tagline"]
    trait_scores = personality["trait_scores"]
    evidence = personality["evidence"]
    strengths = personality["strengths"]
    blind_spots = personality["blind_spots"]
    tips = personality["relationship_tips"]

    # Sort traits by score descending
    sorted_traits = sorted(trait_scores.items(), key=lambda x: x[1], reverse=True)

    # Build trait bars HTML
    trait_bars_html = ""
    for trait, score in sorted_traits:
        trait_name = trait.replace("_", " ").title()
        bar_width = int(score)  # 0-100 maps to 0-100%
        trait_bars_html += f"""
        <div class="trait-row">
            <div class="trait-label">{trait_name}</div>
            <div class="trait-bar-container">
                <div class="trait-bar" style="width: {bar_width}%"></div>
            </div>
            <div class="trait-score">{int(score)}</div>
        </div>
        """

    # Build evidence HTML
    evidence_html = ""
    if evidence:
        for item in evidence:
            metric = item.get("metric", "unknown")
            value = item.get("value", "")
            context = item.get("context", "")
            evidence_html += f'<div class="evidence-item">• <code>{metric}</code>: {value} ({context})</div>\n'
    else:
        evidence_html = '<div class="evidence-item">No specific evidence available</div>\n'

    # Build strengths HTML
    strengths_html = "".join([f"<li>{s}</li>" for s in strengths])

    # Build blind spots HTML
    blind_spots_html = "".join([f"<li>{b}</li>" for b in blind_spots])

    # Build tips HTML
    tips_html = "".join([f"<li>{tip}</li>" for tip in tips])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Codebase Personality: {archetype}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 40px;
            text-align: center;
        }}

        .header .emoji {{
            font-size: 80px;
            margin-bottom: 20px;
        }}

        .header h1 {{
            font-size: 40px;
            margin-bottom: 15px;
            font-weight: 700;
        }}

        .header .tagline {{
            font-size: 20px;
            font-style: italic;
            opacity: 0.95;
        }}

        .content {{
            padding: 50px 40px;
        }}

        .section {{
            margin-bottom: 50px;
        }}

        .section h2 {{
            font-size: 22px;
            color: #333;
            margin-bottom: 25px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}

        .trait-row {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            gap: 15px;
        }}

        .trait-label {{
            min-width: 120px;
            font-weight: 600;
            color: #555;
            font-size: 14px;
        }}

        .trait-bar-container {{
            flex: 1;
            height: 24px;
            background: #e0e0e0;
            border-radius: 12px;
            overflow: hidden;
        }}

        .trait-bar {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            transition: width 0.3s ease;
        }}

        .trait-score {{
            min-width: 40px;
            text-align: right;
            font-weight: 700;
            color: #667eea;
            font-size: 14px;
        }}

        .evidence-item {{
            background: #f5f5f5;
            padding: 12px 15px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
            border-radius: 4px;
            font-size: 14px;
            color: #555;
        }}

        .evidence-item code {{
            background: #e8e8e8;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            color: #333;
        }}

        .list-section {{
            background: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}

        .list-section ul {{
            list-style-position: inside;
            margin: 0;
        }}

        .list-section li {{
            margin-bottom: 12px;
            color: #555;
            line-height: 1.5;
        }}

        .list-section li:last-child {{
            margin-bottom: 0;
        }}

        .footer {{
            background: #f5f5f5;
            padding: 30px 40px;
            text-align: center;
            color: #999;
            font-size: 12px;
            border-top: 1px solid #e0e0e0;
        }}

        @media (max-width: 768px) {{
            .header {{
                padding: 40px 20px;
            }}

            .header h1 {{
                font-size: 28px;
            }}

            .header .emoji {{
                font-size: 60px;
            }}

            .content {{
                padding: 30px 20px;
            }}

            .trait-label {{
                min-width: 100px;
                font-size: 13px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="emoji">{emoji}</div>
            <h1>{archetype}</h1>
            <div class="tagline">{tagline}</div>
        </div>

        <div class="content">
            <div class="section">
                <h2>Trait Profile</h2>
                {trait_bars_html}
            </div>

            <div class="section">
                <h2>Evidence</h2>
                {evidence_html}
            </div>

            <div class="section">
                <h2>Strengths</h2>
                <div class="list-section">
                    <ul>
                        {strengths_html}
                    </ul>
                </div>
            </div>

            <div class="section">
                <h2>Blind Spots</h2>
                <div class="list-section">
                    <ul>
                        {blind_spots_html}
                    </ul>
                </div>
            </div>

            <div class="section">
                <h2>Relationship Tips</h2>
                <div class="list-section">
                    <ol>
                        {tips_html}
                    </ol>
                </div>
            </div>
        </div>

        <div class="footer">
            Generated by Code Scanner Personality Profiler
        </div>
    </div>
</body>
</html>
"""

    return html


def profile_codebase(metrics: Dict) -> Dict:
    """
    Generate a complete personality profile for the codebase.

    Args:
        metrics: RepoMetrics dict with all quality metrics

    Returns:
        Complete personality profile dict with archetype, traits, evidence, tips
    """
    # Compute traits
    trait_scores = compute_trait_scores(metrics)

    # Match archetype
    archetype = match_archetype(trait_scores, metrics)

    # Build evidence
    evidence = build_evidence(metrics, archetype)

    # Generate tips
    tips = generate_relationship_tips(archetype, evidence)

    # Strengths and blind spots based on archetype name
    strengths_map = {
        "The Anxious Overthinker": [
            "Defensive logging practices",
            "Thorough error paths in critical functions"
        ],
        "The Reckless Optimist": [
            "Fast iteration and deployment",
            "Willing to take calculated risks"
        ],
        "The Copy-Paste Artist": [
            "Quick prototyping",
            "Familiar patterns reduce learning curve"
        ],
        "The Chaotic Connector": [
            "Feature-rich, well-integrated components",
            "Flexible module interactions"
        ],
        "The Cautious Perfectionist": [
            "High code quality and reliability",
            "Excellent documentation and test coverage"
        ],
        "The Quiet Newcomer": [
            "Small, manageable codebase",
            "Room to establish best practices early"
        ],
    }

    blind_spots_map = {
        "The Anxious Overthinker": [
            "Complexity hotspots in utility functions",
            "Over-engineering simple solutions"
        ],
        "The Reckless Optimist": [
            "Security vulnerabilities (hardcoded secrets, SQL injection)",
            "Lack of error handling and edge case coverage"
        ],
        "The Copy-Paste Artist": [
            "Maintenance burden: fixing bugs requires updates in multiple places",
            "Inconsistent implementations of the same logic"
        ],
        "The Chaotic Connector": [
            "Hard to understand global flow; changes ripple everywhere",
            "Refactoring is risky due to tangled dependencies"
        ],
        "The Cautious Perfectionist": [
            "May be slow to ship due to perfectionism",
            "Over-documentation can obscure intent"
        ],
        "The Quiet Newcomer": [
            "Insufficient signal to provide targeted advice",
            "Opportunity to establish patterns before they calcify"
        ],
    }

    return {
        "archetype": archetype.name,
        "emoji": archetype.emoji,
        "tagline": archetype.tagline,
        "trait_scores": trait_scores,
        "dominant_traits": [
            trait for trait, score in trait_scores.items() if score >= 70
        ],
        "evidence": evidence,
        "strengths": strengths_map.get(archetype.name, []),
        "blind_spots": blind_spots_map.get(archetype.name, []),
        "relationship_tips": tips,
    }
