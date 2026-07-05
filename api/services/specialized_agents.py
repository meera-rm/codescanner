"""
Specialized Agents - Phase 5.1
Security Auditor, Performance Optimizer, Documentation Generator
"""

from typing import Dict, Any, List
import ast
import re
import asyncio


# ============================================================================
# SECURITY AUDITOR AGENT
# ============================================================================

class SecurityAuditor:
    """Analyzes code for security vulnerabilities"""

    SECURITY_PATTERNS = {
        "sql_injection": [
            r"execute\s*\(\s*['\"].*\{.*\}.*['\"]",
            r"cursor\.execute\s*\(\s*f['\"]",
        ],
        "hardcoded_secrets": [
            r"(api_key|password|secret|token)\s*=\s*['\"].*['\"]",
            r"ghp_[a-zA-Z0-9]{36}",  # GitHub token
            r"AKIA[0-9A-Z]{16}",     # AWS key
        ],
        "path_traversal": [
            r"open\s*\(\s*['\"].*\.\./",
            r"os\.path\.join\s*\(\s*user_input",
        ],
        "eval_usage": [
            r"eval\s*\(",
            r"exec\s*\(",
            r"__import__\s*\(",
        ],
        "command_injection": [
            r"os\.system\s*\(\s*f['\"]",
            r"subprocess\.call\s*\(\s*f['\"]",
        ],
    }

    @staticmethod
    async def analyze(code: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code for security issues"""
        issues = []
        confidence_scores = {}

        for category, patterns in SecurityAuditor.SECURITY_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, code, re.IGNORECASE)
                for match in matches:
                    line_num = code[:match.start()].count('\n') + 1
                    issues.append({
                        "type": category,
                        "line": line_num,
                        "match": match.group(0)[:50],
                        "severity": SecurityAuditor._classify_severity(category)
                    })

            if issues:
                confidence_scores[category] = min(
                    0.95,
                    0.7 + (len([i for i in issues if i["type"] == category]) * 0.1)
                )

        # Check for proper input validation
        validation_patterns = [
            r"isinstance\s*\(",
            r"if\s+.*\.isdigit\s*\(",
            r"if\s+.*\.isalpha\s*\(",
        ]

        validation_found = sum(
            len(list(re.finditer(p, code))) for p in validation_patterns
        )

        recommendations = []
        if len(issues) > 0:
            recommendations.append("Review and remediate security vulnerabilities")
        if validation_found == 0:
            recommendations.append("Add input validation and sanitization")

        return {
            "vulnerabilities_found": len(issues),
            "critical_count": len([i for i in issues if i["severity"] == "critical"]),
            "high_count": len([i for i in issues if i["severity"] == "high"]),
            "medium_count": len([i for i in issues if i["severity"] == "medium"]),
            "issues": issues[:10],  # Top 10
            "confidence": sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0.5,
            "recommendations": recommendations,
            "validation_score": min(100, validation_found * 10)
        }

    @staticmethod
    def _classify_severity(category: str) -> str:
        """Classify vulnerability severity"""
        critical = {"sql_injection", "hardcoded_secrets", "eval_usage"}
        high = {"command_injection", "path_traversal"}

        if category in critical:
            return "critical"
        elif category in high:
            return "high"
        else:
            return "medium"


# ============================================================================
# PERFORMANCE OPTIMIZER AGENT
# ============================================================================

class PerformanceOptimizer:
    """Identifies performance optimization opportunities"""

    @staticmethod
    async def analyze(code: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code for performance improvements"""
        issues = []

        # Check for common anti-patterns
        patterns = {
            "nested_loops": r"for\s+.*:\s*.*for\s+",
            "string_concatenation": r"['\"].*['\"],?\s*\+\s*['\"]",
            "repeated_calculations": r"=\s*\w+\s*\*\s*\d+.*\n.*\w+\s*\*\s*\d+",
            "inefficient_sort": r"sorted\s*\(.*key\s*=\s*lambda",
            "list_comprehension_missing": r"for\s+\w+\s+in\s+.*:\s+if\s+",
        }

        for category, pattern in patterns.items():
            matches = list(re.finditer(pattern, code, re.MULTILINE))
            if matches:
                issues.append({
                    "type": category,
                    "count": len(matches),
                    "recommendation": PerformanceOptimizer._recommend(category)
                })

        # Complexity analysis
        try:
            tree = ast.parse(code)
            max_nesting = PerformanceOptimizer._max_nesting_depth(tree)
        except:
            max_nesting = 0

        recommendations = []
        optimization_score = 100

        if max_nesting > 4:
            recommendations.append(f"Reduce nesting depth (currently {max_nesting})")
            optimization_score -= 20

        for issue in issues:
            if issue["type"] == "nested_loops":
                recommendations.append("Consider vectorization or algorithm optimization")
                optimization_score -= 15

        return {
            "issues_found": len(issues),
            "max_nesting_depth": max_nesting,
            "potential_optimizations": issues,
            "optimization_score": max(0, optimization_score),
            "recommendations": recommendations[:5],
            "confidence": 0.8
        }

    @staticmethod
    def _recommend(category: str) -> str:
        """Get recommendation for issue"""
        recommendations = {
            "nested_loops": "Use vectorization or optimize algorithm",
            "string_concatenation": "Use list join or f-strings",
            "repeated_calculations": "Cache calculation results",
            "inefficient_sort": "Optimize sorting key",
            "list_comprehension_missing": "Use list comprehension instead"
        }
        return recommendations.get(category, "Optimize this pattern")

    @staticmethod
    def _max_nesting_depth(node: ast.AST, depth: int = 0) -> int:
        """Calculate max nesting depth"""
        if isinstance(node, (ast.For, ast.While, ast.If)):
            max_depth = depth + 1
            for child in ast.iter_child_nodes(node):
                max_depth = max(
                    max_depth,
                    PerformanceOptimizer._max_nesting_depth(child, depth + 1)
                )
            return max_depth

        max_depth = depth
        for child in ast.iter_child_nodes(node):
            max_depth = max(
                max_depth,
                PerformanceOptimizer._max_nesting_depth(child, depth)
            )
        return max_depth


# ============================================================================
# DOCUMENTATION GENERATOR AGENT
# ============================================================================

class DocumentationGenerator:
    """Generates and improves documentation"""

    @staticmethod
    async def analyze(code: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code documentation"""
        try:
            tree = ast.parse(code)
        except:
            return {
                "syntax_valid": False,
                "documentation_score": 0,
                "recommendations": ["Code has syntax errors, cannot analyze"]
            }

        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        functions_with_docs = sum(
            1 for f in functions if ast.get_docstring(f)
        )
        classes_with_docs = sum(
            1 for c in classes if ast.get_docstring(c)
        )

        doc_coverage = 0
        if functions or classes:
            doc_coverage = (
                (functions_with_docs + classes_with_docs) /
                (len(functions) + len(classes)) * 100
            )

        recommendations = []

        if doc_coverage < 50:
            recommendations.append("Add docstrings to undocumented functions/classes")
        if doc_coverage < 80:
            recommendations.append("Improve docstring coverage")

        # Check for type hints
        functions_with_types = sum(
            1 for f in functions
            if f.returns or any(arg.annotation for arg in f.args.args)
        )

        return {
            "total_functions": len(functions),
            "documented_functions": functions_with_docs,
            "total_classes": len(classes),
            "documented_classes": classes_with_docs,
            "documentation_coverage": f"{doc_coverage:.1f}%",
            "type_hint_coverage": f"{functions_with_types / len(functions) * 100 if functions else 0:.1f}%",
            "recommendations": recommendations,
            "confidence": 0.9,
            "score": min(100, doc_coverage + (functions_with_types / len(functions) * 20 if functions else 0))
        }
