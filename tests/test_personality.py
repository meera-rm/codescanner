"""
Tests for the personality profiler module.
"""

import pytest
import sys
from pathlib import Path

# Add scanner directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scanner"))

from personality import (
    compute_trait_scores,
    match_archetype,
    build_evidence,
    generate_relationship_tips,
    profile_codebase,
    generate_personality_markdown_section,
    generate_personality_html,
    compare_personalities,
    ARCHETYPES,
)


class TestTraitScoring:
    """Test trait score computation."""

    def test_overthinking_high_complexity(self):
        """High complexity should increase overthinking trait."""
        metrics = {
            "avg_complexity": 4.0,
            "max_complexity": 8.0,
            "security_high_count": 0,
            "smell_count": 0,
            "doc_coverage_ratio": 0.8,
            "duplication_percentage": 5.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 3.0,
            "total_logging": 10,
            "total_functions": 20,
            "error_handling_density": 50.0,
            "avg_quality_score": 70.0,
        }
        scores = compute_trait_scores(metrics)
        assert scores["overthinking"] > 60

    def test_recklessness_high_security(self):
        """High security findings should increase recklessness trait."""
        metrics = {
            "avg_complexity": 1.0,
            "max_complexity": 2.0,
            "security_high_count": 5,
            "smell_count": 0,
            "doc_coverage_ratio": 0.9,
            "duplication_percentage": 0.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 2.0,
            "total_logging": 5,
            "total_functions": 10,
            "error_handling_density": 20.0,
            "avg_quality_score": 60.0,
        }
        scores = compute_trait_scores(metrics)
        assert scores["recklessness"] >= 100  # Clamped to 100

    def test_secrecy_low_docs(self):
        """Low documentation coverage should increase secrecy trait."""
        metrics = {
            "avg_complexity": 1.0,
            "max_complexity": 2.0,
            "security_high_count": 0,
            "smell_count": 0,
            "doc_coverage_ratio": 0.2,  # Low docs
            "duplication_percentage": 0.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 2.0,
            "total_logging": 5,
            "total_functions": 10,
            "error_handling_density": 50.0,
            "avg_quality_score": 70.0,
        }
        scores = compute_trait_scores(metrics)
        assert scores["secrecy"] > 70

    def test_chaos_circular_deps(self):
        """Circular dependencies should increase chaos trait."""
        metrics = {
            "avg_complexity": 1.0,
            "max_complexity": 2.0,
            "security_high_count": 0,
            "smell_count": 0,
            "doc_coverage_ratio": 0.8,
            "duplication_percentage": 0.0,
            "circular_dep_count": 3,
            "avg_imports_per_file": 8.0,
            "total_logging": 5,
            "total_functions": 10,
            "error_handling_density": 50.0,
            "avg_quality_score": 70.0,
        }
        scores = compute_trait_scores(metrics)
        assert scores["chaos"] > 60

    def test_perfectionism_high_quality(self):
        """High quality score should increase perfectionism trait."""
        metrics = {
            "avg_complexity": 1.0,
            "max_complexity": 2.0,
            "security_high_count": 0,
            "smell_count": 0,
            "doc_coverage_ratio": 0.9,
            "duplication_percentage": 0.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 2.0,
            "total_logging": 5,
            "total_functions": 10,
            "error_handling_density": 80.0,
            "avg_quality_score": 90.0,
        }
        scores = compute_trait_scores(metrics)
        assert scores["perfectionism"] == 90.0

    def test_all_traits_zero(self):
        """Empty metrics should produce low traits."""
        metrics = {
            "avg_complexity": 0.0,
            "max_complexity": 0.0,
            "security_high_count": 0,
            "smell_count": 0,
            "doc_coverage_ratio": 1.0,
            "duplication_percentage": 0.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 0.0,
            "total_logging": 0,
            "total_functions": 1,
            "error_handling_density": 50.0,
            "avg_quality_score": 50.0,
        }
        scores = compute_trait_scores(metrics)
        assert scores["overthinking"] == 0
        assert scores["anxiety"] == 0
        assert scores["recklessness"] <= 50


class TestArchetypeMatching:
    """Test archetype matching logic."""

    def test_anxious_overthinker_high_complexity(self):
        """High complexity should match Anxious Overthinker."""
        metrics = {
            "avg_complexity": 5.0,
            "max_complexity": 10.0,
            "security_high_count": 0,
            "smell_count": 2,
            "doc_coverage_ratio": 0.8,
            "duplication_percentage": 5.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 3.0,
            "total_logging": 30,
            "total_functions": 20,
            "error_handling_density": 50.0,
            "avg_quality_score": 70.0,
            "total_lines": 5000,
        }
        trait_scores = compute_trait_scores(metrics)
        archetype = match_archetype(trait_scores, metrics)
        assert archetype == ARCHETYPES["anxious_overthinker"]

    def test_reckless_optimist_high_security(self):
        """High security findings should match Reckless Optimist."""
        metrics = {
            "avg_complexity": 1.0,
            "max_complexity": 2.0,
            "security_high_count": 10,
            "smell_count": 0,
            "doc_coverage_ratio": 0.9,
            "duplication_percentage": 0.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 2.0,
            "total_logging": 5,
            "total_functions": 10,
            "error_handling_density": 10.0,
            "avg_quality_score": 50.0,
            "total_lines": 5000,
        }
        trait_scores = compute_trait_scores(metrics)
        archetype = match_archetype(trait_scores, metrics)
        assert archetype == ARCHETYPES["reckless_optimist"]

    def test_copy_paste_artist_high_duplication(self):
        """High duplication should match Copy-Paste Artist."""
        metrics = {
            "avg_complexity": 1.0,
            "max_complexity": 2.0,
            "security_high_count": 0,
            "smell_count": 0,
            "doc_coverage_ratio": 0.8,
            "duplication_percentage": 25.0,  # High duplication
            "circular_dep_count": 0,
            "avg_imports_per_file": 2.0,
            "total_logging": 5,
            "total_functions": 10,
            "error_handling_density": 50.0,
            "avg_quality_score": 70.0,
            "total_lines": 5000,
        }
        trait_scores = compute_trait_scores(metrics)
        archetype = match_archetype(trait_scores, metrics)
        assert archetype == ARCHETYPES["copy_paste_artist"]

    def test_chaotic_connector_high_coupling(self):
        """High circular dependencies should match Chaotic Connector."""
        metrics = {
            "avg_complexity": 1.0,
            "max_complexity": 2.0,
            "security_high_count": 0,
            "smell_count": 0,
            "doc_coverage_ratio": 0.8,
            "duplication_percentage": 0.0,
            "circular_dep_count": 5,
            "avg_imports_per_file": 8.0,
            "total_logging": 5,
            "total_functions": 10,
            "error_handling_density": 50.0,
            "avg_quality_score": 70.0,
            "total_lines": 5000,
        }
        trait_scores = compute_trait_scores(metrics)
        archetype = match_archetype(trait_scores, metrics)
        assert archetype == ARCHETYPES["chaotic_connector"]

    def test_cautious_perfectionist_high_quality(self):
        """High quality and docs should match Cautious Perfectionist."""
        metrics = {
            "avg_complexity": 1.0,
            "max_complexity": 2.0,
            "security_high_count": 0,
            "smell_count": 0,
            "doc_coverage_ratio": 0.95,
            "duplication_percentage": 0.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 2.0,
            "total_logging": 5,
            "total_functions": 10,
            "error_handling_density": 85.0,
            "avg_quality_score": 90.0,
            "total_lines": 5000,
        }
        trait_scores = compute_trait_scores(metrics)
        archetype = match_archetype(trait_scores, metrics)
        assert archetype == ARCHETYPES["cautious_perfectionist"]

    def test_quiet_newcomer_small_codebase(self):
        """Small codebase with neutral scores should match Quiet Newcomer."""
        metrics = {
            "avg_complexity": 0.5,
            "max_complexity": 1.0,
            "security_high_count": 0,
            "smell_count": 0,
            "doc_coverage_ratio": 0.7,
            "duplication_percentage": 0.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 1.0,
            "total_logging": 1,
            "total_functions": 2,
            "error_handling_density": 70.0,
            "avg_quality_score": 35.0,  # Low enough to trigger fallback
            "total_lines": 200,  # Small codebase
        }
        trait_scores = compute_trait_scores(metrics)
        # With these metrics, all traits should be < 40
        archetype = match_archetype(trait_scores, metrics)
        assert archetype == ARCHETYPES["quiet_newcomer"]


class TestEvidenceBuilding:
    """Test evidence extraction."""

    def test_anxious_overthinker_evidence(self):
        """Anxious Overthinker should cite complexity and logging."""
        metrics = {
            "avg_complexity": 4.0,
            "total_logging": 50,
            "smell_count": 3,
            "doc_coverage_ratio": 0.8,
            "duplication_percentage": 0.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 2.0,
            "total_functions": 20,
            "security_high_count": 0,
            "error_handling_density": 50.0,
            "avg_quality_score": 70.0,
        }
        trait_scores = compute_trait_scores(metrics)
        archetype = match_archetype(trait_scores, metrics)
        evidence = build_evidence(metrics, archetype)

        # Should have complexity and logging evidence
        assert any("complexity" in e.get("metric", "").lower() for e in evidence)
        assert any("logging" in e.get("metric", "").lower() for e in evidence)

    def test_reckless_optimist_evidence(self):
        """Reckless Optimist should cite security issues."""
        metrics = {
            "avg_complexity": 1.0,
            "max_complexity": 2.0,
            "security_high_count": 8,
            "smell_count": 0,
            "doc_coverage_ratio": 0.9,
            "duplication_percentage": 0.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 2.0,
            "total_logging": 5,
            "total_functions": 10,
            "error_handling_density": 15.0,
            "avg_quality_score": 50.0,
        }
        trait_scores = compute_trait_scores(metrics)
        archetype = match_archetype(trait_scores, metrics)
        evidence = build_evidence(metrics, archetype)

        # Should have security evidence
        assert any("security" in e.get("metric", "").lower() for e in evidence)


class TestRelationshipTips:
    """Test tip generation."""

    def test_anxious_overthinker_tips(self):
        """Anxious Overthinker should get complexity-related tips."""
        tips = generate_relationship_tips(
            ARCHETYPES["anxious_overthinker"],
            []
        )
        assert len(tips) == 3
        assert any("simpler" in t.lower() or "complex" in t.lower() for t in tips)

    def test_reckless_optimist_tips(self):
        """Reckless Optimist should get security-related tips."""
        tips = generate_relationship_tips(
            ARCHETYPES["reckless_optimist"],
            []
        )
        assert len(tips) == 3
        assert any("security" in t.lower() for t in tips)

    def test_all_archetypes_have_tips(self):
        """All archetypes should generate 3 tips."""
        for archetype in ARCHETYPES.values():
            tips = generate_relationship_tips(archetype, [])
            assert len(tips) == 3
            assert all(isinstance(t, str) for t in tips)


class TestFullProfile:
    """Test complete profile generation."""

    def test_profile_includes_all_fields(self):
        """Profile should include all required fields."""
        metrics = {
            "avg_complexity": 2.0,
            "max_complexity": 4.0,
            "security_high_count": 1,
            "smell_count": 2,
            "doc_coverage_ratio": 0.7,
            "duplication_percentage": 5.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 3.0,
            "total_logging": 15,
            "total_functions": 15,
            "error_handling_density": 50.0,
            "avg_quality_score": 70.0,
            "total_lines": 2000,
        }
        profile = profile_codebase(metrics)

        assert "archetype" in profile
        assert "emoji" in profile
        assert "tagline" in profile
        assert "trait_scores" in profile
        assert "dominant_traits" in profile
        assert "evidence" in profile
        assert "strengths" in profile
        assert "blind_spots" in profile
        assert "relationship_tips" in profile

    def test_profile_dominant_traits(self):
        """Dominant traits should be those >= 70."""
        metrics = {
            "avg_complexity": 4.0,
            "max_complexity": 8.0,
            "security_high_count": 0,
            "smell_count": 5,
            "doc_coverage_ratio": 0.8,
            "duplication_percentage": 0.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 2.0,
            "total_logging": 50,
            "total_functions": 20,
            "error_handling_density": 50.0,
            "avg_quality_score": 70.0,
            "total_lines": 5000,
        }
        profile = profile_codebase(metrics)

        # Dominant traits should only include scores >= 70
        for trait in profile["dominant_traits"]:
            assert profile["trait_scores"][trait] >= 70

    def test_profile_has_strengths_and_blinds(self):
        """Profile should always have strengths and blind spots."""
        metrics = {
            "avg_complexity": 0.5,
            "max_complexity": 1.0,
            "security_high_count": 0,
            "smell_count": 0,
            "doc_coverage_ratio": 0.5,
            "duplication_percentage": 0.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 1.0,
            "total_logging": 0,
            "total_functions": 5,
            "error_handling_density": 20.0,
            "avg_quality_score": 50.0,
            "total_lines": 200,
        }
        profile = profile_codebase(metrics)

        assert len(profile["strengths"]) >= 1
        assert len(profile["blind_spots"]) >= 1
        assert len(profile["relationship_tips"]) == 3


class TestMarkdownGeneration:
    """Test Markdown personality section generation."""

    def test_markdown_includes_archetype(self):
        """Markdown should include archetype name and emoji."""
        metrics = {
            "avg_complexity": 3.0,
            "max_complexity": 6.0,
            "security_high_count": 0,
            "smell_count": 1,
            "doc_coverage_ratio": 0.8,
            "duplication_percentage": 0.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 2.0,
            "total_logging": 20,
            "total_functions": 15,
            "error_handling_density": 50.0,
            "avg_quality_score": 70.0,
            "total_lines": 2000,
        }
        profile = profile_codebase(metrics)
        markdown = generate_personality_markdown_section(profile)

        assert "Codebase Personality" in markdown
        assert profile["archetype"] in markdown
        assert profile["emoji"] in markdown
        assert profile["tagline"] in markdown

    def test_markdown_includes_traits(self):
        """Markdown should include all trait scores in table."""
        metrics = {
            "avg_complexity": 2.0,
            "max_complexity": 4.0,
            "security_high_count": 0,
            "smell_count": 0,
            "doc_coverage_ratio": 0.7,
            "duplication_percentage": 0.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 2.0,
            "total_logging": 10,
            "total_functions": 10,
            "error_handling_density": 50.0,
            "avg_quality_score": 70.0,
            "total_lines": 1500,
        }
        profile = profile_codebase(metrics)
        markdown = generate_personality_markdown_section(profile)

        assert "Trait Profile" in markdown
        assert "Overthinking" in markdown or "overthinking" in markdown.lower()
        assert "|" in markdown  # Table format

    def test_markdown_includes_evidence(self):
        """Markdown should include evidence section."""
        metrics = {
            "avg_complexity": 4.0,
            "max_complexity": 8.0,
            "security_high_count": 0,
            "smell_count": 2,
            "doc_coverage_ratio": 0.8,
            "duplication_percentage": 0.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 2.0,
            "total_logging": 30,
            "total_functions": 20,
            "error_handling_density": 50.0,
            "avg_quality_score": 70.0,
            "total_lines": 2000,
        }
        profile = profile_codebase(metrics)
        markdown = generate_personality_markdown_section(profile)

        assert "Evidence" in markdown
        assert "Strengths" in markdown
        assert "Blind Spots" in markdown
        assert "Relationship Tips" in markdown


class TestHTMLGeneration:
    """Test HTML personality card generation."""

    def test_html_is_valid(self):
        """Generated HTML should be valid."""
        metrics = {
            "avg_complexity": 2.0,
            "max_complexity": 4.0,
            "security_high_count": 0,
            "smell_count": 0,
            "doc_coverage_ratio": 0.7,
            "duplication_percentage": 0.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 2.0,
            "total_logging": 10,
            "total_functions": 10,
            "error_handling_density": 50.0,
            "avg_quality_score": 70.0,
            "total_lines": 1500,
        }
        profile = profile_codebase(metrics)
        html = generate_personality_html(profile)

        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "</html>" in html
        assert "<style>" in html
        assert "</style>" in html

    def test_html_contains_archetype(self):
        """HTML should prominently display archetype."""
        metrics = {
            "avg_complexity": 3.0,
            "max_complexity": 6.0,
            "security_high_count": 0,
            "smell_count": 1,
            "doc_coverage_ratio": 0.8,
            "duplication_percentage": 0.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 2.0,
            "total_logging": 20,
            "total_functions": 15,
            "error_handling_density": 50.0,
            "avg_quality_score": 70.0,
            "total_lines": 2000,
        }
        profile = profile_codebase(metrics)
        html = generate_personality_html(profile)

        assert profile["archetype"] in html
        assert profile["emoji"] in html
        assert profile["tagline"] in html

    def test_html_contains_traits(self):
        """HTML should display trait scores with bars."""
        metrics = {
            "avg_complexity": 2.0,
            "max_complexity": 4.0,
            "security_high_count": 0,
            "smell_count": 0,
            "doc_coverage_ratio": 0.7,
            "duplication_percentage": 0.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 2.0,
            "total_logging": 10,
            "total_functions": 10,
            "error_handling_density": 50.0,
            "avg_quality_score": 70.0,
            "total_lines": 1500,
        }
        profile = profile_codebase(metrics)
        html = generate_personality_html(profile)

        assert "Trait Profile" in html
        assert "trait-bar" in html  # CSS class for trait bars
        assert "trait-label" in html

    def test_html_is_self_contained(self):
        """HTML should be self-contained with inline CSS."""
        metrics = {
            "avg_complexity": 1.0,
            "max_complexity": 2.0,
            "security_high_count": 0,
            "smell_count": 0,
            "doc_coverage_ratio": 0.8,
            "duplication_percentage": 0.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 1.0,
            "total_logging": 5,
            "total_functions": 5,
            "error_handling_density": 60.0,
            "avg_quality_score": 75.0,
            "total_lines": 500,
        }
        profile = profile_codebase(metrics)
        html = generate_personality_html(profile)

        # Should not reference external stylesheets
        assert "href=" not in html or ".css" not in html
        # Should have inline styles
        assert "<style>" in html
        assert "background:" in html

    def test_html_includes_all_sections(self):
        """HTML should include all personality sections."""
        metrics = {
            "avg_complexity": 2.0,
            "max_complexity": 4.0,
            "security_high_count": 1,
            "smell_count": 1,
            "doc_coverage_ratio": 0.7,
            "duplication_percentage": 2.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 3.0,
            "total_logging": 10,
            "total_functions": 10,
            "error_handling_density": 50.0,
            "avg_quality_score": 70.0,
            "total_lines": 1500,
        }
        profile = profile_codebase(metrics)
        html = generate_personality_html(profile)

        assert "Trait Profile" in html
        assert "Evidence" in html
        assert "Strengths" in html
        assert "Blind Spots" in html
        assert "Relationship Tips" in html


class TestPersonalityComparison:
    """Test personality comparison (before/after)."""

    def test_compare_same_profiles_no_change(self):
        """Comparing identical profiles should show no change."""
        metrics = {
            "avg_complexity": 1.0,
            "max_complexity": 2.0,
            "security_high_count": 0,
            "smell_count": 0,
            "doc_coverage_ratio": 0.8,
            "duplication_percentage": 0.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 2.0,
            "total_logging": 5,
            "total_functions": 10,
            "error_handling_density": 70.0,
            "avg_quality_score": 75.0,
            "total_lines": 1500,
        }
        profile = profile_codebase(metrics)
        comparison = compare_personalities(profile, profile)

        assert comparison["archetype_changed"] is False
        assert len(comparison["trait_deltas"]) == 0

    def test_compare_security_fix(self):
        """Comparing before/after security fix should show recklessness change."""
        # Before: High security issues (Reckless Optimist)
        before_metrics = {
            "avg_complexity": 1.0,
            "max_complexity": 2.0,
            "security_high_count": 10,
            "smell_count": 0,
            "doc_coverage_ratio": 0.9,
            "duplication_percentage": 0.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 2.0,
            "total_logging": 5,
            "total_functions": 10,
            "error_handling_density": 20.0,
            "avg_quality_score": 50.0,
            "total_lines": 1500,
        }
        before = profile_codebase(before_metrics)

        # After: No security issues (Cautious Perfectionist)
        after_metrics = {
            "avg_complexity": 1.0,
            "max_complexity": 2.0,
            "security_high_count": 0,
            "smell_count": 0,
            "doc_coverage_ratio": 0.95,
            "duplication_percentage": 0.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 2.0,
            "total_logging": 5,
            "total_functions": 10,
            "error_handling_density": 80.0,
            "avg_quality_score": 90.0,
            "total_lines": 1500,
        }
        after = profile_codebase(after_metrics)

        comparison = compare_personalities(before, after)

        assert comparison["archetype_changed"] is True
        assert "recklessness" in comparison["trait_deltas"]
        assert comparison["trait_deltas"]["recklessness"]["delta"] < 0  # Decreased

    def test_compare_includes_summary(self):
        """Comparison should include summary line."""
        before_metrics = {
            "avg_complexity": 3.0,
            "max_complexity": 6.0,
            "security_high_count": 2,
            "smell_count": 1,
            "doc_coverage_ratio": 0.8,
            "duplication_percentage": 0.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 2.0,
            "total_logging": 20,
            "total_functions": 15,
            "error_handling_density": 50.0,
            "avg_quality_score": 70.0,
            "total_lines": 2000,
        }
        before = profile_codebase(before_metrics)

        after_metrics = {
            "avg_complexity": 1.5,
            "max_complexity": 3.0,
            "security_high_count": 1,
            "smell_count": 0,
            "doc_coverage_ratio": 0.85,
            "duplication_percentage": 0.0,
            "circular_dep_count": 0,
            "avg_imports_per_file": 2.0,
            "total_logging": 15,
            "total_functions": 15,
            "error_handling_density": 60.0,
            "avg_quality_score": 80.0,
            "total_lines": 2000,
        }
        after = profile_codebase(after_metrics)

        comparison = compare_personalities(before, after)

        assert "summary_line" in comparison
        assert len(comparison["summary_line"]) > 0
        assert "changed" in comparison["summary_line"].lower() or "no changes" in comparison["summary_line"].lower()
