import ast
from dataclasses import dataclass
from typing import List, Dict, Set, Tuple, Optional
from pathlib import Path


@dataclass
class CouplingMetrics:
    """Statistics about module coupling (imports and dependencies)."""
    files_analyzed: int
    total_imports: int
    avg_imports_per_file: float
    has_circular_deps: bool
    circular_deps: List[Tuple[str, str]]  # List of (file1, file2) pairs that form cycles
    import_graph: Dict[str, Set[str]]  # file -> set of imported files
    max_imports_in_file: int
    min_imports_in_file: int


class CouplingDetector:
    """Analyzes module coupling through imports and detects circular dependencies."""

    def __init__(self):
        self.import_graph: Dict[str, Set[str]] = {}  # file -> imported modules
        self.file_to_path: Dict[str, str] = {}  # module name -> file path

    def analyze_directory(self, directory: str) -> CouplingMetrics:
        """Analyze coupling across all Python files in a directory."""
        self.import_graph = {}
        self.file_to_path = {}

        py_files = list(Path(directory).rglob("*.py"))

        # Skip test/fixture directories
        skip_patterns = ["test", "tests", "fixtures", "__pycache__", ".venv"]
        py_files = [
            f for f in py_files
            if not any(pattern in str(f) for pattern in skip_patterns)
        ]

        # Extract imports from all files
        for py_file in py_files:
            relative_path = str(py_file.relative_to(directory))
            module_name = relative_path.replace("/", ".").replace("\\", ".").replace(".py", "")
            self.file_to_path[module_name] = str(py_file)
            self.import_graph[module_name] = self._extract_imports(str(py_file))

        # Detect circular dependencies
        circular_deps = self._detect_circular_deps()

        # Calculate metrics
        total_imports = sum(len(imports) for imports in self.import_graph.values())
        file_import_counts = [len(imports) for imports in self.import_graph.values()]

        avg_imports = (
            total_imports / len(py_files) if py_files else 0
        )
        max_imports = max(file_import_counts) if file_import_counts else 0
        min_imports = min(file_import_counts) if file_import_counts else 0

        return CouplingMetrics(
            files_analyzed=len(py_files),
            total_imports=total_imports,
            avg_imports_per_file=avg_imports,
            has_circular_deps=len(circular_deps) > 0,
            circular_deps=circular_deps,
            import_graph=self.import_graph,
            max_imports_in_file=max_imports,
            min_imports_in_file=min_imports,
        )

    def _extract_imports(self, filepath: str) -> Set[str]:
        """Extract all imported module names from a file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()
        except (UnicodeDecodeError, IOError):
            return set()

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return set()

        imports = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                # import X, import X.Y.Z
                for alias in node.names:
                    module = alias.name.split(".")[0]
                    imports.add(module)

            elif isinstance(node, ast.ImportFrom):
                # from X import Y, from X.Y import Z
                if node.module:
                    module = node.module.split(".")[0]
                    imports.add(module)

        # Filter out standard library and built-in imports
        imports = self._filter_stdlib(imports)
        return imports

    def _filter_stdlib(self, imports: Set[str]) -> Set[str]:
        """Remove standard library and common third-party imports."""
        # Standard library modules
        stdlib = {
            "os", "sys", "re", "json", "csv", "pathlib", "logging",
            "abc", "ast", "asyncio", "collections", "dataclasses",
            "datetime", "functools", "itertools", "typing", "unittest",
            "pytest", "tempfile", "shutil", "subprocess", "threading",
            "urllib", "requests", "numpy", "pandas", "django", "flask",
            "sqlalchemy", "boto3", "click", "argparse", "hashlib",
            "hmac", "struct", "string", "io", "pickle", "base64",
            "codecs", "copy", "enum", "glob", "gzip", "hashlib",
            "heapq", "html", "http", "imaplib", "imghdr", "inspect",
            "ipaddress", "mmap", "numbers", "operator", "pdb", "pkgutil",
            "platform", "pprint", "queue", "random", "secrets", "select",
            "shelve", "signal", "site", "socket", "sqlite3", "ssl",
            "stat", "statistics", "textwrap", "time", "timeit", "trace",
            "traceback", "tracemalloc", "types", "uuid", "warnings", "weakref",
            "wsgiref", "xml", "zipfile", "zlib"
        }
        return imports - stdlib

    def _detect_circular_deps(self) -> List[Tuple[str, str]]:
        """Detect circular dependencies using DFS."""
        visited = set()
        rec_stack = set()
        circular_deps = []

        def has_cycle(node: str, path: List[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.import_graph.get(node, set()):
                # Only check if neighbor is in our analyzed files
                if neighbor not in self.import_graph:
                    continue

                if neighbor not in visited:
                    if has_cycle(neighbor, path):
                        return True
                elif neighbor in rec_stack:
                    # Found cycle
                    idx = path.index(neighbor)
                    for i in range(idx, len(path) - 1):
                        circular_deps.append((path[i], path[i + 1]))
                    return True

            rec_stack.remove(node)
            path.pop()
            return False

        for node in self.import_graph:
            if node not in visited:
                has_cycle(node, [])

        return circular_deps

    def report(self, metrics: CouplingMetrics) -> dict:
        """Generate a human-readable report."""
        return {
            "files_analyzed": metrics.files_analyzed,
            "total_imports": metrics.total_imports,
            "avg_imports_per_file": metrics.avg_imports_per_file,
            "max_imports": metrics.max_imports_in_file,
            "min_imports": metrics.min_imports_in_file,
            "has_circular_deps": metrics.has_circular_deps,
            "circular_deps_count": len(metrics.circular_deps),
            "circular_deps": metrics.circular_deps,
            "summary": self._generate_summary(metrics),
        }

    def _generate_summary(self, metrics: CouplingMetrics) -> str:
        """Generate summary string."""
        parts = []

        avg = metrics.avg_imports_per_file
        if avg < 3:
            parts.append("Low coupling (good)")
        elif avg < 7:
            parts.append("Moderate coupling")
        else:
            parts.append("High coupling (consider refactoring)")

        if metrics.has_circular_deps:
            parts.append(f"Found {len(metrics.circular_deps)} circular dependencies")
        else:
            parts.append("No circular dependencies (good)")

        return " | ".join(parts)
