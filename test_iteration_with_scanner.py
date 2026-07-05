#!/usr/bin/env python
"""
Quick test: Run iteration with real scanner on examples/ directory.
This verifies the scanner integration works end-to-end.
"""

import asyncio
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "scanner"))

from api.services.iteration_clean_service import IterationCleanService
from api.services.scanner_service import ScannerService


async def test_iteration_with_real_scanner():
    """Test iteration with real scanner on examples/ directory."""
    print("\n" + "="*80)
    print("PHASE 3.5: ITERATION UNTIL CLEAN - REAL SCANNER TEST")
    print("="*80)

    # Initialize service with real scanner
    scanner = ScannerService()
    service = IterationCleanService(scanner_service=scanner)

    # Use api/routes directory (has real code with issues)
    codebase_path = "/Users/meera/Documents/codescanner/api/routes"

    print(f"\n📁 Scanning: {codebase_path}")
    print("-" * 80)

    # Step 1: Initial scan
    print("\n1️⃣  INITIAL SCAN")
    initial_scan = await service._scan_codebase(codebase_path)
    initial_grade = initial_scan.get("grade", "unknown")
    initial_issues = len(initial_scan.get("issues", []))
    initial_score = initial_scan.get("metrics", {}).get("quality_score", 0)

    print(f"   Grade: {initial_grade}")
    print(f"   Quality Score: {initial_score:.1f}/100")
    print(f"   Issues Found: {initial_issues}")
    print(f"   Severity Breakdown: {initial_scan.get('metrics', {}).get('findings_by_severity', {})}")

    if initial_issues == 0:
        print("\n   ✅ No issues found! Code is already clean.")
        print("      Skipping iteration (nothing to fix).")
        return

    # Step 2: Get suggestions from agents
    print("\n2️⃣  AGENT SUGGESTIONS (parallel)")
    issues = initial_scan.get("issues", [])
    suggestions = await service._get_suggestions(codebase_path, issues)

    for i, sugg in enumerate(suggestions, 1):
        print(f"   Agent {i}: {sugg.agent}")
        print(f"      Strategy: {sugg.description}")
        print(f"      Complexity Reduction: {sugg.complexity_reduction}%")
        print(f"      Risk Level: {sugg.risk_level}")

    if not suggestions:
        print("   ⚠️  No suggestions available")
        return

    # Step 3: Evaluate and pick best
    print("\n3️⃣  EVALUATION")
    best = service.evaluator.pick_best(suggestions)
    print(f"   Selected: {best.agent}")
    print(f"   Strategy: {best.description}")
    print(f"   Estimated Improvement: {best.complexity_reduction}%")

    # Step 4: Validate
    print("\n4️⃣  VALIDATION")
    validation = await service.validator.validate(best)
    print(f"   Approved: {validation.approved}")
    for check in validation.checks:
        status = "✅" if check.passed else "❌"
        print(f"   {status} {check.check_name}")

    # Step 5: Apply fix (simulated)
    print("\n5️⃣  APPLY FIX (simulated in Phase 3.5)")
    fix_result = await service._apply_fix(codebase_path, best)
    print(f"   Applied: {fix_result.get('applied', False)}")
    print(f"   Files Modified: {fix_result.get('files_modified', 0)}")
    print(f"   Summary: {fix_result.get('changes_summary', 'N/A')}")

    # Step 6: Rescan
    print("\n6️⃣  RESCAN")
    rescan = await service._scan_codebase(codebase_path)
    new_grade = rescan.get("grade", "unknown")
    new_issues = len(rescan.get("issues", []))
    new_score = rescan.get("metrics", {}).get("quality_score", 0)

    print(f"   Grade: {new_grade}")
    print(f"   Quality Score: {new_score:.1f}/100")
    print(f"   Issues Found: {new_issues}")
    print(f"   Issues Fixed: {initial_issues - new_issues}")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Start:  {initial_grade} ({initial_score:.1f}/100) - {initial_issues} issues")
    print(f"End:    {new_grade} ({new_score:.1f}/100) - {new_issues} issues")
    print(f"Change: {initial_grade} → {new_grade} ({new_score - initial_score:+.1f} points)")
    print(f"Fixed:  {initial_issues - new_issues} issues")
    print("\n✅ Single iteration complete (would repeat until target grade)")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(test_iteration_with_real_scanner())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
