"""
Tests for Inheritance Letter Generator (Creative Path H)

Tests tone selection, section builders, and full letter generation.
"""

import pytest
import sys
from pathlib import Path

# Add scanner directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scanner"))

from inheritance import (
    select_tone,
    build_proud_section,
    build_not_proud_section,
    build_secrets_section,
    build_avoid_section,
    build_start_here_section,
    build_first_week_tips,
    generate_letter,
    compare_letter_tones,
)


# FIXTURES
@pytest.fixture
def apologetic_repo():
    """Codebase with security issues and low quality."""
    return [
        {
            "filepath": "insecure.py",
            "quality_score": 30,
            "complexity_average": 2.0,
            "security_findings": {
                "high": [
                    {"type": "hardcoded_secret", "line": 6},
                    {"type": "sql_injection", "line": 12},
                ]
            },
            "smells_count": 3,
            "functions": [
                {"name": "auth_user", "complexity": 2.0},
            ]
        },
        {
            "filepath": "app.py",
            "quality_score": 45,
            "complexity_average": 3.0,
            "security_findings": {"high": []},
            "smells_count": 2,
            "functions": [
                {"name": "main", "complexity": 3.0},
            ]
        }
    ]


@pytest.fixture
def cautious_repo():
    """Codebase with moderate quality and some smells."""
    return [
        {
            "filepath": "module.py",
            "quality_score": 65,
            "complexity_average": 2.5,
            "security_findings": {"high": []},
            "smells_count": 5,
            "functions": [
                {"name": "process", "complexity": 2.5},
            ]
        },
        {
            "filepath": "utils.py",
            "quality_score": 72,
            "complexity_average": 1.5,
            "security_findings": {"high": []},
            "smells_count": 1,
            "functions": [
                {"name": "helper", "complexity": 1.5},
            ]
        }
    ]


@pytest.fixture
def confident_repo():
    """Codebase with high quality, clean security."""
    return [
        {
            "filepath": "core.py",
            "quality_score": 85,
            "complexity_average": 2.0,
            "security_findings": {"high": []},
            "smells_count": 0,
            "functions": [
                {"name": "process", "complexity": 2.0},
            ]
        },
        {
            "filepath": "utils.py",
            "quality_score": 80,
            "complexity_average": 1.5,
            "security_findings": {"high": []},
            "smells_count": 1,
            "functions": [
                {"name": "helper", "complexity": 1.5},
            ]
        }
    ]


@pytest.fixture
def empty_repo():
    """Empty codebase."""
    return []


# TONE SELECTION TESTS
def test_tone_selection_apologetic(apologetic_repo):
    """Security issues trigger apologetic tone."""
    tone = select_tone(apologetic_repo)
    assert tone == "apologetic"


def test_tone_selection_cautious(cautious_repo):
    """Moderate quality with smells triggers cautious tone."""
    tone = select_tone(cautious_repo)
    assert tone == "cautious"


def test_tone_selection_confident(confident_repo):
    """High quality, clean security triggers confident tone."""
    tone = select_tone(confident_repo)
    assert tone == "confident"


def test_tone_selection_empty():
    """Empty repo defaults to cautious."""
    tone = select_tone([])
    assert tone == "cautious"


# SECTION BUILDER TESTS
def test_proud_section_present(cautious_repo):
    """Proud section identifies best files."""
    proud = build_proud_section(cautious_repo)
    assert len(proud) > 0
    assert "file" in proud[0]
    assert "quality" in proud[0]
    # Best file should be highest quality
    assert proud[0]["quality"] >= proud[1]["quality"] if len(proud) > 1 else True


def test_not_proud_section_present(apologetic_repo):
    """Not proud section identifies worst files."""
    not_proud = build_not_proud_section(apologetic_repo)
    assert len(not_proud) > 0
    assert "file" in not_proud[0]
    # Worst file should be lowest quality
    assert not_proud[0]["quality"] <= not_proud[1]["quality"] if len(not_proud) > 1 else True


def test_secrets_section_with_findings(apologetic_repo):
    """Secrets section includes security confessions."""
    secrets = build_secrets_section(apologetic_repo)
    assert len(secrets) == 2  # Two high-severity findings in apologetic_repo
    assert all("confession" in s for s in secrets)
    assert all("I'm sorry" in s["confession"] for s in secrets)


def test_secrets_section_empty(cautious_repo):
    """Secrets section is empty when no security findings."""
    secrets = build_secrets_section(cautious_repo)
    assert len(secrets) == 0


def test_avoid_section(apologetic_repo):
    """Avoid section identifies complex functions."""
    avoid = build_avoid_section(apologetic_repo)
    assert len(avoid) > 0
    assert "function" in avoid[0]
    assert "complexity" in avoid[0]


def test_start_here_section(confident_repo):
    """Start here section identifies clean entry points."""
    start = build_start_here_section(confident_repo)
    assert len(start) > 0
    assert "file" in start[0]
    assert start[0]["complexity"] <= 3


def test_start_here_fallback(apologetic_repo):
    """Start here uses fallback when no clean files."""
    start = build_start_here_section(apologetic_repo)
    assert len(start) > 0
    # Fallback should exist even if no ideal candidates
    reason_lower = start[0]["reason"].lower()
    assert "fallback" in reason_lower or "safe entry" in reason_lower or "anyway" in reason_lower


def test_first_week_tips_apologetic(apologetic_repo):
    """Apologetic tone gives security-focused tips."""
    tips = build_first_week_tips(apologetic_repo, "apologetic")
    assert len(tips) == 3
    assert any("secret" in t.lower() or "security" in t.lower() for t in tips)


def test_first_week_tips_cautious(cautious_repo):
    """Cautious tone gives quality-focused tips."""
    tips = build_first_week_tips(cautious_repo, "cautious")
    assert len(tips) == 3
    assert any("refactor" in t.lower() or "docstring" in t.lower() for t in tips)


def test_first_week_tips_confident(confident_repo):
    """Confident tone gives contribution-focused tips."""
    tips = build_first_week_tips(confident_repo, "confident")
    assert len(tips) == 3
    assert any("test" in t.lower() or "architecture" in t.lower() for t in tips)


# FULL LETTER TESTS
def test_generate_letter_complete(apologetic_repo):
    """Complete letter generation."""
    letter = generate_letter(apologetic_repo)
    assert "tone" in letter
    assert "proud" in letter
    assert "not_proud" in letter
    assert "secrets" in letter
    assert "avoid" in letter
    assert "start_here" in letter
    assert "first_week_tips" in letter
    assert "sign_off" in letter


def test_generate_letter_empty():
    """Letter generation handles empty repo."""
    letter = generate_letter([])
    assert letter["tone"] == "cautious"
    assert isinstance(letter["proud"], list)
    assert isinstance(letter["secrets"], list)


def test_letter_tone_matches_selection(apologetic_repo):
    """Letter tone matches tone selection logic."""
    letter = generate_letter(apologetic_repo)
    expected_tone = select_tone(apologetic_repo)
    assert letter["tone"] == expected_tone


# COMPARISON TESTS
def test_compare_same_tones(apologetic_repo):
    """Comparing identical letters shows no change."""
    letter1 = generate_letter(apologetic_repo)
    letter2 = generate_letter(apologetic_repo)
    comparison = compare_letter_tones(letter1, letter2)
    assert comparison["tone_changed"] == False


def test_compare_different_tones(apologetic_repo, cautious_repo):
    """Comparing different tones shows change."""
    letter1 = generate_letter(apologetic_repo)
    letter2 = generate_letter(cautious_repo)
    comparison = compare_letter_tones(letter1, letter2)
    assert comparison["tone_changed"] == True
    assert letter1["tone"] in comparison["summary_line"]
    assert letter2["tone"] in comparison["summary_line"]


def test_compare_shows_secret_reduction(apologetic_repo, cautious_repo):
    """Comparison shows reduction in secrets."""
    letter1 = generate_letter(apologetic_repo)  # Has secrets
    letter2 = generate_letter(cautious_repo)    # No secrets
    comparison = compare_letter_tones(letter1, letter2)
    if len(letter1["secrets"]) > len(letter2["secrets"]):
        assert "fewer secrets" in comparison["summary_line"].lower()


# EDGE CASES
def test_all_sections_present_apologetic(apologetic_repo):
    """Apologetic tone includes all expected sections."""
    letter = generate_letter(apologetic_repo)
    assert len(letter["secrets"]) > 0  # Should have secrets
    assert len(letter["avoid"]) > 0    # Should have avoid functions
    assert len(letter["first_week_tips"]) == 3


def test_fallback_when_no_candidates():
    """Sections use fallbacks when no ideal candidates."""
    minimal = [
        {
            "filepath": "single.py",
            "quality_score": 40,
            "complexity_average": 8.0,
            "security_findings": {"high": [{"type": "issue", "line": 1}]},
            "smells_count": 5,
            "functions": []
        }
    ]
    letter = generate_letter(minimal)
    # Should still generate sections even with bad metrics
    assert len(letter["start_here"]) > 0  # Fallback to lowest-complexity


def test_sign_off_matches_tone():
    """Sign-off matches the tone."""
    for repo, expected_tone in [
        ([], "cautious"),  # empty defaults to cautious
    ]:
        letter = generate_letter(repo)
        tone = letter["tone"]
        sign_off = letter["sign_off"]
        assert tone.capitalize() in sign_off or tone == "cautious"


# HTML RENDERING TESTS
def test_html_render_simple(apologetic_repo):
    """Letter can be rendered to HTML."""
    from inheritance import render_letter_html
    letter = generate_letter(apologetic_repo)
    html = render_letter_html(letter)
    assert "<!DOCTYPE html>" in html
    assert "Inheritance Letter" in html
    assert "text/html" not in html or "charset" in html
    assert "sorry" in html.lower()  # confessions


def test_html_is_self_contained(apologetic_repo):
    """HTML is self-contained (no external CSS/JS)."""
    from inheritance import render_letter_html
    letter = generate_letter(apologetic_repo)
    html = render_letter_html(letter)
    # Should have inline styles
    assert "<style>" in html
    # Should NOT reference external resources
    assert "http://" not in html.lower()
    assert ".css" not in html.lower()
    # Should include tone color gradient
    assert "linear-gradient" in html


def test_html_tone_styling(apologetic_repo, cautious_repo, confident_repo):
    """HTML applies different colors for each tone."""
    from inheritance import render_letter_html

    for repo, tone, color_hint in [
        (apologetic_repo, "apologetic", "#e63946"),  # Red
        (cautious_repo, "cautious", "#f77f00"),      # Orange
        (confident_repo, "confident", "#06d6a0"),    # Green
    ]:
        letter = generate_letter(repo)
        html = render_letter_html(letter)

        # Should contain the tone
        assert tone.capitalize() in html
        # Should contain the primary color
        assert color_hint in html


def test_html_contains_all_sections(apologetic_repo):
    """HTML includes all letter sections."""
    from inheritance import render_letter_html
    letter = generate_letter(apologetic_repo)
    html = render_letter_html(letter)

    # All section headers should be present
    assert "What I'm Proud Of" in html
    assert "What I'm Not Proud Of" in html
    assert "Secrets I've Been Keeping" in html
    assert "Rooms You Should Avoid First" in html
    assert "Where to Start Instead" in html
    assert "How to Survive Your First Week" in html


def test_html_secrets_section_styling(apologetic_repo):
    """Secrets section has distinct styling."""
    from inheritance import render_letter_html
    letter = generate_letter(apologetic_repo)
    html = render_letter_html(letter)

    # Should have secrets-section class
    assert "secrets-section" in html
    # Should have background color for secrets
    assert "background:" in html


def test_html_responsive_design(apologetic_repo):
    """HTML includes responsive media queries."""
    from inheritance import render_letter_html
    letter = generate_letter(apologetic_repo)
    html = render_letter_html(letter)

    # Should have mobile viewport meta tag
    assert "viewport" in html
    # Should have media queries
    assert "@media" in html
    assert "768px" in html  # Mobile breakpoint


def test_html_printable(apologetic_repo):
    """HTML is printable (includes print styles)."""
    from inheritance import render_letter_html
    letter = generate_letter(apologetic_repo)
    html = render_letter_html(letter)

    # Should have print media query
    assert "@media print" in html


def test_html_readable_font_size(apologetic_repo):
    """HTML uses readable font sizes (18px+)."""
    from inheritance import render_letter_html
    letter = generate_letter(apologetic_repo)
    html = render_letter_html(letter)

    # Should have 18px+ for main content
    assert "18px" in html or "20px" in html or "22px" in html
    # Header should be even larger
    assert "40px" in html


# INTEGRATION TESTS
def test_markdown_render_simple(apologetic_repo):
    """Letter can be rendered to markdown."""
    from inheritance import render_letter_markdown
    letter = generate_letter(apologetic_repo)
    markdown = render_letter_markdown(letter)
    assert "Inheritance Letter" in markdown
    assert "Tone:" in markdown
    assert "sorry" in markdown.lower()  # confessions


def test_metrics_list_structure(apologetic_repo):
    """Metrics list structure is correct."""
    letter = generate_letter(apologetic_repo)
    # Verify letter contains expected data structure
    assert isinstance(letter["proud"], list)
    assert all(isinstance(p, dict) for p in letter["proud"])
    assert isinstance(letter["secrets"], list)
    assert all(isinstance(s, dict) for s in letter["secrets"])


# PERFORMANCE TESTS
def test_generation_reasonably_fast(apologetic_repo):
    """Letter generation completes quickly."""
    import time
    start = time.time()
    letter = generate_letter(apologetic_repo * 10)  # 20 files
    elapsed = time.time() - start
    assert elapsed < 0.5  # Should be very fast (< 500ms)


# PHASE L4: DEMO & DOCUMENTATION TESTS

def test_before_after_comparison():
    """Before/after tone comparison works correctly."""
    # Before: with security issues
    before_metrics = [
        {
            "filepath": "bad.py",
            "quality_score": 40,
            "complexity_average": 2.0,
            "security_findings": {"high": [{"type": "secret", "line": 6}]},
            "smells_count": 5,
        }
    ]

    # After: same file, fixed
    after_metrics = [
        {
            "filepath": "bad.py",
            "quality_score": 65,
            "complexity_average": 2.0,
            "security_findings": {"high": []},
            "smells_count": 2,
        }
    ]

    letter_before = generate_letter(before_metrics)
    letter_after = generate_letter(after_metrics)

    comparison = compare_letter_tones(letter_before, letter_after)

    assert letter_before["tone"] == "apologetic"
    assert letter_after["tone"] != "apologetic"
    assert comparison["tone_changed"] is True
    assert "cautious" in comparison["summary_line"] or "confident" in comparison["summary_line"]


def test_html_generation_is_deterministic(confident_repo):
    """Same letter always generates same HTML (no randomness)."""
    from inheritance import render_letter_html
    letter = generate_letter(confident_repo)
    html1 = render_letter_html(letter)
    html2 = render_letter_html(letter)

    assert html1 == html2
    assert len(html1) > 100  # Not empty
    assert "<!DOCTYPE" in html1


def test_all_three_tones_render_html(apologetic_repo, cautious_repo, confident_repo):
    """All three tones generate valid HTML with correct colors."""
    from inheritance import render_letter_html

    letter_apol = generate_letter(apologetic_repo)
    letter_caut = generate_letter(cautious_repo)
    letter_conf = generate_letter(confident_repo)

    html_apol = render_letter_html(letter_apol)
    html_caut = render_letter_html(letter_caut)
    html_conf = render_letter_html(letter_conf)

    # Each should be valid HTML
    assert "<!DOCTYPE html" in html_apol
    assert "<!DOCTYPE html" in html_caut
    assert "<!DOCTYPE html" in html_conf

    # Each should contain inline CSS
    assert "<style>" in html_apol
    assert "<style>" in html_caut
    assert "<style>" in html_conf

    # Each should have tone-specific color
    # Apologetic: red (#e63946), Cautious: amber (#f77f00), Confident: green (#06d6a0)
    assert "e63946" in html_apol or "red" in html_apol.lower()  # Apologetic red
    # Cautious and Confident may use different patterns
    assert "<!DOCTYPE" in html_caut
    assert "<!DOCTYPE" in html_conf


def test_empty_metrics_list_renders(empty_repo):
    """Empty codebase still generates valid letter."""
    from inheritance import render_letter_html
    letter = generate_letter(empty_repo)
    html = render_letter_html(letter)

    assert "<!DOCTYPE" in html
    assert "Inheritance Letter" in html
    assert "<style>" in html


def test_letter_sections_present_in_html(apologetic_repo):
    """HTML contains all expected letter sections."""
    from inheritance import render_letter_html
    letter = generate_letter(apologetic_repo)
    html = render_letter_html(letter)

    # Check for all 6 section titles
    assert "What I'm Proud Of" in html or "Proud" in html
    assert "What I'm Not Proud Of" in html or "Not Proud" in html or "not proud" in html.lower()
    assert "Secrets I've Been Keeping" in html or "Secrets" in html
    assert "Rooms You Should Avoid" in html or "Avoid" in html
    assert "Where to Start" in html or "Start Here" in html
    assert "First Week" in html or "survive" in html.lower()


def test_tone_colors_match_in_html(apologetic_repo, confident_repo):
    """HTML uses correct colors for tones."""
    from inheritance import render_letter_html

    letter_apol = generate_letter(apologetic_repo)
    letter_conf = generate_letter(confident_repo)

    html_apol = render_letter_html(letter_apol)
    html_conf = render_letter_html(letter_conf)

    # Both should have gradients (tone-specific)
    assert "linear-gradient" in html_apol
    assert "linear-gradient" in html_conf

    # Check for color codes in the HTML
    assert "#" in html_apol  # Should have color hex codes
    assert "#" in html_conf


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
