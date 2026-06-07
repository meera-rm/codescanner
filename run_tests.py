#!/usr/bin/env python3
"""
Comprehensive test runner with coverage reporting.

Usage:
    python run_tests.py                 # Run all tests
    python run_tests.py --unit          # Run unit tests only
    python run_tests.py --integration   # Run integration tests only
    python run_tests.py --coverage      # Run with coverage report
    python run_tests.py --fast          # Run tests in parallel
"""

import subprocess
import sys
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and print results."""
    print(f"\n{'=' * 70}")
    print(f"📋 {description}")
    print(f"{'=' * 70}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Run test suite")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage report")
    parser.add_argument("--fast", action="store_true", help="Run tests in parallel")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--markers", "-m", type=str, help="Run tests matching marker")

    args = parser.parse_args()

    # Build pytest command
    cmd = "pytest"

    if args.fast:
        cmd += " -n auto"  # Parallel execution
    elif args.verbose:
        cmd += " -vv"
    else:
        cmd += " -v"

    # Add coverage
    if args.coverage:
        cmd += " --cov=scanner --cov-report=html --cov-report=term"

    # Add marker filtering
    if args.unit:
        cmd += " -m unit"
    elif args.integration:
        cmd += " -m integration"
    elif args.markers:
        cmd += f" -m {args.markers}"

    print("\n" + "=" * 70)
    print("🧪 CODE SCANNER TEST SUITE")
    print("=" * 70)

    # Display what's being tested
    tests_dir = Path("tests")
    test_files = list(tests_dir.glob("test_*.py"))

    print(f"\n📁 Test Files Found: {len(test_files)}")
    for test_file in sorted(test_files):
        print(f"   • {test_file.name}")

    # Run tests
    success = run_command(cmd, "Running Tests")

    if success:
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)

        if args.coverage:
            print("\n📊 Coverage Report: htmlcov/index.html")
            print("   Open in browser to view detailed coverage")

        return 0
    else:
        print("\n" + "=" * 70)
        print("❌ SOME TESTS FAILED")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
