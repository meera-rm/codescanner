# Phase 1.4 Complete: Coupling Detector ✅

**Status:** Built, tested, and validated on real code  
**Time:** ~1.5 hours  
**Tests:** 15 unit tests, all passing  
**Real findings:** Low coupling (0.6 avg imports/file), no circular dependencies

---

## What Was Built

### File: `scanner/coupling.py`

**CouplingMetrics dataclass:**
- `files_analyzed` — Number of Python files scanned
- `total_imports` — Total count of custom (non-stdlib) imports
- `avg_imports_per_file` — Average imports per file
- `has_circular_deps` — Boolean flag
- `circular_deps` — List of (file1, file2) cycle pairs
- `import_graph` — Dict mapping files to their imports
- `max_imports_in_file` — Highest import count in any file
- `min_imports_in_file` — Lowest import count in any file

**CouplingDetector class:**
- `analyze_directory(path)` — Scan all .py files
- `_extract_imports()` — Parse import statements from AST
- `_filter_stdlib()` — Remove standard library imports
- `_detect_circular_deps()` — DFS-based cycle detection
- `report()` — Generate human-readable summary

---

## How It Works

### 1. Import Extraction
Handles both styles:
```python
import module_name          # Detects 'module_name'
from package import item   # Detects 'package'
```

### 2. Standard Library Filtering
Removes 100+ stdlib modules (os, sys, json, etc.) and common third-party libraries (numpy, pandas, django, etc.) to focus on custom coupling.

### 3. Circular Dependency Detection
Uses depth-first search (DFS) to detect cycles:
- Tracks visited nodes and recursion stack
- Identifies cycle edges when revisiting in-progress node
- Returns all circular dependency pairs

### 4. Coupling Classification
```
avg_imports/file < 3   → Low coupling (good)
3 ≤ avg_imports < 7    → Moderate coupling
avg_imports ≥ 7        → High coupling (refactor)
```

---

## Test Results

```bash
$ python tests/test_coupling.py

✓ Simple imports: 2 imports, avg 1.0/file
✓ From imports: 2 imports detected
✓ Stdlib filtering: 2 custom imports (stdlib filtered)
✓ No imports: handled correctly
✓ Multiple files: 6 total, avg 2.0/file
✓ Circular dependency detected
✓ No circular dependencies: clean tree
✓ Complex cycle detected: 2 edges
✓ Max/min imports: max=3, min=1
✓ Empty directory: handled correctly
✓ Syntax error: skipped gracefully
✓ Report generated
✓ Import graph structure tracked
✓ Real-world scenario: 4 files, 4 custom imports
✓ Coupling classification working

✅ All 15 tests passing
```

---

## Real-World Results

Analyzed the scanner codebase:

```
Files analyzed: 8
Total imports: 5
Avg imports/file: 0.6
Max imports in file: 3
Min imports in file: 0
Circular dependencies: 0

Result: Low coupling (good) | No circular dependencies (good)
```

**Interpretation:** Scanner has clean, loosely-coupled architecture ✓

---

## Usage Example

```python
from coupling import CouplingDetector

detector = CouplingDetector()
metrics = detector.analyze_directory("src/")

print(f"Avg coupling: {metrics.avg_imports_per_file:.1f} imports/file")
print(f"Circular deps: {len(metrics.circular_deps)}")

if metrics.has_circular_deps:
    for file1, file2 in metrics.circular_deps:
        print(f"  {file1} → {file2}")

report = detector.report(metrics)
print(report["summary"])
```

---

## Integration Ready

Coupling detector is ready to be:
- ✅ Integrated into metrics aggregator
- ✅ Wired into `--coupling` flag in scanner.py
- ✅ Used for "coupling" pollutant in CAQI

---

## All 4 Detectors Complete! ✅

| Detector | Status | Test Count | Real Coverage |
|----------|--------|-----------|---------------|
| Smells | ✅ Done | 12 tests | 4 smells found |
| Docs | ✅ Done | 13 tests | 75-100% coverage |
| Duplication | ✅ Done | 14 tests | 0% duplication |
| Coupling | ✅ Done | 15 tests | 0.6 avg imports |

**Total:** 54 tests written, all passing  
**Code quality:** All detectors validate on real codebase

---

## Next Phase: Metrics Aggregator (Phase 2)

Now that all detectors are built, Phase 2 combines them:

```python
from smells import SmellDetector
from doc_coverage import DocCoverageDetector
from duplication import DuplicationDetector
from coupling import CouplingDetector

class MetricsAggregator:
    def aggregate(directory, scanner_findings):
        # Run all 4 detectors
        smells = SmellDetector().detect(...)
        docs = DocCoverageDetector().analyze(...)
        duplication = DuplicationDetector().analyze_directory(...)
        coupling = CouplingDetector().analyze_directory(...)
        
        # Combine into unified RepoMetrics
        return RepoMetrics(
            complexity=...,  # From scanner
            security=...,    # From scanner
            smells=smells,
            docs=docs.coverage_ratio,
            duplication=duplication.duplication_percentage,
            coupling=coupling.avg_imports_per_file
        )
```

---

## Key Design Decisions

**Why filter stdlib imports?**
- Focus on actual coupling (between project modules)
- Stdlib imports are external, not architectural
- Makes metrics more meaningful

**Why use DFS for cycle detection?**
- O(V + E) complexity (efficient)
- Handles complex cycles (not just A ↔ B)
- Standard algorithm for dependency graphs

**Why separate avg/max/min imports?**
- Average shows overall coupling trend
- Max identifies hotspot files
- Min shows if some files are truly isolated

**Why ignore circular deps in metrics?**
- Added as boolean flag, not in scoring
- Circular deps are binary: either exist or don't
- CAQI formula will weight this separately

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Code size | ~120 lines (coupling.py) |
| Test coverage | 15 tests, all passing |
| Dependencies | None (pure AST) |
| Real coupling | 0.6 avg imports/file |
| Circular cycles | 0 (clean) |
| Build time | ~1.5 hours |
| Status | ✅ Production ready |

---

## Coupling Pollutant Formula (for CAQI)

```python
coupling_score = min(avg_imports * 5, 100)
if has_circular_deps:
    coupling_score += 50  # Big penalty for cycles
```

Example:
- 2 imports/file, no cycles → coupling = 10 (clean)
- 5 imports/file, no cycles → coupling = 25 (moderate)
- 10 imports/file, no cycles → coupling = 50 (high)
- Any imports, has cycles → coupling ≥ 50 (major issue)

---

## Circular Dependency Handling

Example detection:

```python
# module_a.py
import module_b

# module_b.py
import module_a  # ← Cycle!
```

Detector reports:
```
has_circular_deps: True
circular_deps: [("module_a", "module_b")]
```

---

**Status:** ✅ All 4 detectors complete!  
**Next:** Phase 2 - Metrics Aggregator (2-3 hours)  
**Then:** Phase 3 - CAQI Engine (5-7 hours)

See PLAN_OPTION_B.md for full roadmap.
