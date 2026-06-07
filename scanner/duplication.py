import ast
import hashlib
import re
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from pathlib import Path


@dataclass
class DuplicateBlock:
    """Represents a duplicate code block found in two locations."""
    file1: str
    line1: int
    file2: str
    line2: int
    block_size: int  # Number of lines in the duplicate
    similarity: float  # 0.0 to 1.0
    block_type: str  # "exact" or "near"


@dataclass
class DuplicationMetrics:
    """Statistics about code duplication in a file or repo."""
    total_lines: int
    duplicate_lines: int
    duplication_percentage: float  # 0-100
    duplicate_blocks: List[DuplicateBlock]
    files_analyzed: int


class DuplicationDetector:
    """Detects duplicate code blocks across Python files."""

    def __init__(self, min_block_size: int = 3):
        """
        Initialize detector.

        Args:
            min_block_size: Minimum lines to consider as a block (default: 3)
        """
        self.min_block_size = min_block_size
        self.code_blocks: Dict[str, List[Tuple[int, str]]] = {}  # file -> [(line, code)]
        self.normalized_blocks: Dict[str, List[Tuple[int, str]]] = {}  # file -> [(line, normalized)]
        self.block_hashes: Dict[str, List[Tuple[int, str]]] = {}  # file -> [(line, hash)]

    def analyze_directory(self, directory: str) -> DuplicationMetrics:
        """Analyze duplication across all Python files in a directory."""
        py_files = list(Path(directory).rglob("*.py"))

        # Skip test/fixture directories
        skip_patterns = ["test", "tests", "fixtures", "__pycache__", ".venv"]
        py_files = [
            f for f in py_files
            if not any(pattern in str(f) for pattern in skip_patterns)
        ]

        total_lines = 0
        all_duplicates = []

        # First pass: extract blocks from all files
        for py_file in py_files:
            blocks = self._extract_blocks(str(py_file))
            if blocks:
                total_lines += sum(len(code.split("\n")) for _, code in blocks)

        # Second pass: find duplicates
        for i, file1 in enumerate(py_files):
            blocks1 = self._extract_blocks(str(file1))
            if not blocks1:
                continue

            for file2 in py_files[i + 1 :]:  # Only compare forward
                blocks2 = self._extract_blocks(str(file2))
                if not blocks2:
                    continue

                duplicates = self._find_duplicates(
                    str(file1), blocks1, str(file2), blocks2
                )
                all_duplicates.extend(duplicates)

        # Calculate duplicate lines
        duplicate_lines = self._count_duplicate_lines(all_duplicates)

        duplication_percentage = (
            (duplicate_lines / total_lines * 100) if total_lines > 0 else 0.0
        )

        return DuplicationMetrics(
            total_lines=total_lines,
            duplicate_lines=duplicate_lines,
            duplication_percentage=duplication_percentage,
            duplicate_blocks=all_duplicates,
            files_analyzed=len(py_files),
        )

    def _extract_blocks(self, filepath: str) -> List[Tuple[int, str]]:
        """Extract code blocks (functions, classes, and sequences) from a file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()
        except (UnicodeDecodeError, IOError):
            return []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []

        blocks = []
        lines = code.split("\n")

        # Extract functions and classes
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                start = node.lineno - 1
                end = node.end_lineno or node.lineno
                block_code = "\n".join(lines[start:end])
                if len(block_code.split("\n")) >= self.min_block_size:
                    blocks.append((node.lineno, block_code))

        # Also extract line sequences (for non-function duplicates)
        # Look for sequences of >= min_block_size lines
        i = 0
        while i < len(lines):
            # Skip empty/comment lines
            if lines[i].strip() == "" or lines[i].strip().startswith("#"):
                i += 1
                continue

            # Try to find a block of min_block_size lines
            block_lines = []
            j = i
            while j < len(lines) and len(block_lines) < 10:  # Max 10 lines per sequence
                if lines[j].strip() and not lines[j].strip().startswith("#"):
                    block_lines.append(lines[j])
                j += 1

            if len(block_lines) >= self.min_block_size:
                block_code = "\n".join(block_lines)
                blocks.append((i + 1, block_code))
                i = j
            else:
                i += 1

        return blocks

    def _find_duplicates(
        self,
        file1: str,
        blocks1: List[Tuple[int, str]],
        file2: str,
        blocks2: List[Tuple[int, str]],
    ) -> List[DuplicateBlock]:
        """Find duplicate blocks between two files."""
        duplicates = []

        for line1, code1 in blocks1:
            for line2, code2 in blocks2:
                if len(code1.split("\n")) != len(code2.split("\n")):
                    continue  # Different sizes

                # Check for exact match
                if code1 == code2:
                    block_size = len(code1.split("\n"))
                    duplicates.append(
                        DuplicateBlock(
                            file1=file1,
                            line1=line1,
                            file2=file2,
                            line2=line2,
                            block_size=block_size,
                            similarity=1.0,
                            block_type="exact",
                        )
                    )
                else:
                    # Check for near match
                    similarity = self._calculate_similarity(code1, code2)
                    if similarity > 0.85:  # >85% similar
                        block_size = len(code1.split("\n"))
                        duplicates.append(
                            DuplicateBlock(
                                file1=file1,
                                line1=line1,
                                file2=file2,
                                line2=line2,
                                block_size=block_size,
                                similarity=similarity,
                                block_type="near",
                            )
                        )

        return duplicates

    def _calculate_similarity(self, code1: str, code2: str) -> float:
        """Calculate similarity between two code blocks (0-1)."""
        norm1 = self._normalize_code(code1)
        norm2 = self._normalize_code(code2)

        if norm1 == norm2:
            return 1.0

        # Levenshtein-based similarity
        distance = self._levenshtein_distance(norm1, norm2)
        max_len = max(len(norm1), len(norm2))

        if max_len == 0:
            return 1.0

        similarity = 1.0 - (distance / max_len)
        return max(0.0, similarity)

    def _normalize_code(self, code: str) -> str:
        """Normalize code for comparison (remove comments, extra whitespace)."""
        lines = code.split("\n")
        normalized = []

        for line in lines:
            # Remove comments
            line = re.sub(r"#.*$", "", line)
            # Strip whitespace
            line = line.strip()
            # Skip empty lines
            if line:
                normalized.append(line)

        return "\n".join(normalized)

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def _count_duplicate_lines(self, duplicates: List[DuplicateBlock]) -> int:
        """Count total duplicate lines from a list of duplicate blocks."""
        if not duplicates:
            return 0

        # Track which line ranges are duplicated
        duplicate_ranges = []
        for dup in duplicates:
            end_line = dup.line1 + dup.block_size - 1
            duplicate_ranges.append((dup.file1, dup.line1, end_line))
            duplicate_ranges.append((dup.file2, dup.line2, end_line))

        # Count unique duplicate line ranges
        seen = set()
        count = 0
        for file, start, end in duplicate_ranges:
            key = (file, start, end)
            if key not in seen:
                seen.add(key)
                count += (end - start + 1)

        return count

    def report(self, metrics: DuplicationMetrics) -> dict:
        """Generate a report of duplication findings."""
        return {
            "total_lines": metrics.total_lines,
            "duplicate_lines": metrics.duplicate_lines,
            "duplication_percentage": metrics.duplication_percentage,
            "files_analyzed": metrics.files_analyzed,
            "duplicate_count": len(metrics.duplicate_blocks),
            "summary": f"{metrics.duplication_percentage:.1f}% of code is duplicated ({metrics.duplicate_lines}/{metrics.total_lines} lines)",
            "top_duplicates": sorted(
                metrics.duplicate_blocks,
                key=lambda x: x.block_size,
                reverse=True,
            )[:5],
        }
