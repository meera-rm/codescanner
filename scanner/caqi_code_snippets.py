# CAQI Implementation Reference - Copy-Paste Code Snippets

# ============================================================================
# CAQI FORMULAS (Sub-score calculations - each 0-100)
# ============================================================================

def complexity_score(avg_cyclomatic, max_fn_cyclomatic):
    """Complexity: min(avg * 20 + max_fn * 10, 100)"""
    return min(avg_cyclomatic * 20 + max_fn_cyclomatic * 10, 100)

def security_score(high_vulns, medium_vulns):
    """Security: min(high * 40 + medium * 20, 100)"""
    return min(high_vulns * 40 + medium_vulns * 20, 100)

def smells_score(code_smell_count):
    """Smells: min(count * 12.5, 100) — 8+ smells → 100"""
    return min(code_smell_count * 12.5, 100)

def docs_score(coverage_ratio):
    """Docs: (1 - coverage_ratio) * 100 — inverted (missing = pollution)"""
    return (1 - coverage_ratio) * 100

def duplication_score(duplicate_percentage):
    """Duplication: duplicate_percentage (capped at 100)"""
    return min(duplicate_percentage, 100)

def coupling_score(import_count, has_circular_deps):
    """Coupling: min(imports * 5, 100) + 50 if circular deps"""
    base = min(import_count * 5, 100)
    circular_penalty = 50 if has_circular_deps else 0
    return min(base + circular_penalty, 100)

# ============================================================================
# REPO CAQI CALCULATION
# ============================================================================

def calculate_repo_caqi(pollutants_dict):
    """
    CAQI = round(max_pollutant * 3.5 + mean(top_3_pollutants) * 1.5)
    Clamped to [0, 500]
    primary_pollutant = argmax(pollutants)
    """
    max_pollutant = max(pollutants_dict.values())
    top_3 = sorted(pollutants_dict.values(), reverse=True)[:3]
    mean_top_3 = sum(top_3) / len(top_3)
    
    caqi_raw = max_pollutant * 3.5 + mean_top_3 * 1.5
    caqi = round(caqi_raw)
    caqi_clamped = max(0, min(caqi, 500))
    
    primary_pollutant = max(pollutants_dict, key=pollutants_dict.get)
    
    return {
        "score": caqi_clamped,
        "primary_pollutant": primary_pollutant,
        "pollutants": pollutants_dict
    }

# ============================================================================
# EPA-STYLE BANDS
# ============================================================================

EPA_BANDS = {
    "0-50": {"level": "Good", "color": "#96c480", "meaning": "Healthy codebase"},
    "51-100": {"level": "Moderate", "color": "#f1f1f0", "meaning": "Some concerns"},
    "101-150": {"level": "Unhealthy for Sensitive Groups", "color": "#f1f7f8", "meaning": "New devs will struggle"},
    "151-200": {"level": "Unhealthy", "color": "#ff9999", "meaning": "Active remediation needed"},
    "201-300": {"level": "Very Unhealthy", "color": "#873f97", "meaning": "High incident risk"},
    "301-500": {"level": "Hazardous", "color": "#7e9023", "meaning": "Do not deploy"}
}

def get_caqi_band(score):
    """Return band info (level, color, meaning) for CAQI score"""
    if 0 <= score <= 50:
        return EPA_BANDS["0-50"]
    elif 51 <= score <= 100:
        return EPA_BANDS["51-100"]
    elif 101 <= score <= 150:
        return EPA_BANDS["101-150"]
    elif 151 <= score <= 200:
        return EPA_BANDS["151-200"]
    elif 201 <= score <= 300:
        return EPA_BANDS["201-300"]
    else:
        return EPA_BANDS["301-500"]

# ============================================================================
# JSON OUTPUT SHAPE
# ============================================================================

json_output_template = {
    "caqi": {
        "score": 455,
        "level": "Hazardous",
        "color": "#7e9023",
        "primary_pollutant": "security",
        "primary_source": "examples/insecure.py",
        "pollutants": {
            "complexity": 10.0,
            "security": 100.0,
            "smells": 0.0,
            "docs": 100.0,
            "duplication": 0.0,
            "coupling": 0
        },
        "per_file": [
            # top 10 worst files by CAQI
        ],
        "health_advice": "Health warning of emergency conditions. Do not deploy."
    }
}

# ============================================================================
# CLI COMMANDS (BASH)
# ============================================================================

# Basic CAQI scan
"""
python -m scanner examples/ \
  --caqi \
  --caqi-html output/caqi.html \
  --security --quality-score --code-smells --doc-coverage \
  --output output/report.json \
  --report-md output/report.md
"""

# Creative suite (all three paths: G + H + I)
"""
python -m scanner examples/ \
  --caqi --caqi-html output/caqi.html \
  --personality --personality-html output/personality.html \
  --inheritance-letter output/letter.md --inheritance-html output/letter.html \
  --security --quality-score --code-smells --doc-coverage \
  --output output/report.json --report-md output/report.md
"""

# ============================================================================
# MARKDOWN ONE-LINER (Output at top of report)
# ============================================================================

def generate_markdown_caqi_line(caqi_score, primary_pollutant, primary_source):
    """Generate: CAQI: 455 — Hazardous / Primary pollutant: security (insecure.py)"""
    band_info = get_caqi_band(caqi_score)
    level = band_info["level"]
    return f"CAQI: {caqi_score} — {level} / Primary pollutant: {primary_pollutant} ({primary_source})"

# ============================================================================
# EXAMPLE: BEFORE/AFTER DEMO
# ============================================================================

# BEFORE: Scan with secrets
before = {
    "complexity": 10.0,
    "security": 100.0,  # <- BLOCKER (secrets detected)
    "smells": 0.0,
    "docs": 100.0,
    "duplication": 0.0,
    "coupling": 0
}
caqi_before = calculate_repo_caqi(before)
# Result: CAQI ≈ 455 Hazardous, primary = security

# AFTER: Secrets removed + error handling added
after = {
    "complexity": 60.0,   # <- Now visible (was masked by security)
    "security": 0.0,      # <- Fixed
    "smells": 40.0,
    "docs": 20.0,
    "duplication": 0.0,
    "coupling": 0
}
caqi_after = calculate_repo_caqi(after)
# Result: CAQI ≈ 287 Very Unhealthy (~213 point drop), primary = complexity

# Talking point: "Security was the blocker. Now we see the real architectural debt."

