import os
import re
from typing import Dict, Optional, Any


class RefactoringService:
    """Service for generating and validating code fixes."""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.claude_available = self.api_key is not None

    def generate_fix(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a fix suggestion for a code issue."""
        if not self.claude_available:
            return self._generate_fix_heuristic(issue)

        try:
            from anthropic import Anthropic

            client = Anthropic()

            issue_type = issue.get("type", "")
            code_snippet = issue.get("code_snippet", "")
            severity = issue.get("severity", "medium")
            message = issue.get("message", "")

            prompt = f"""You are a code refactoring expert. Fix this code issue:

Type: {issue_type}
Severity: {severity}
Message: {message}

Code:
```
{code_snippet}
```

Provide:
1. The fixed code (in a code block)
2. A brief explanation (1-2 sentences)
3. A risk assessment (low/medium/high)

Format your response as:
FIXED_CODE:
```
<code>
```
EXPLANATION: <explanation>
RISK: <risk>
"""

            response = client.messages.create(
                model="claude-opus-4-8",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text

            return self._parse_claude_response(content, issue)

        except Exception as e:
            return {
                "original_code": issue.get("code_snippet", ""),
                "suggested_fix": None,
                "explanation": f"Could not generate fix: {str(e)}",
                "risk_level": "unknown",
                "error": str(e),
            }

    def _generate_fix_heuristic(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a fix using heuristic rules (when Claude API not available)."""
        issue_type = issue.get("type", "")
        code = issue.get("code_snippet", "")

        if "hardcoded_secret" in issue_type:
            suggested = re.sub(r'"[a-zA-Z0-9\-]{32,}"', '"<SECRET>"', code)
            return {
                "original_code": code,
                "suggested_fix": suggested,
                "explanation": "Replace hardcoded secret with environment variable",
                "risk_level": "low",
            }

        if "unused_import" in issue_type:
            lines = code.split("\n")
            suggested = "\n".join([l for l in lines if l.strip()])
            return {
                "original_code": code,
                "suggested_fix": suggested,
                "explanation": "Remove unused import",
                "risk_level": "low",
            }

        return {
            "original_code": code,
            "suggested_fix": None,
            "explanation": "No automated fix available",
            "risk_level": "unknown",
        }

    def _parse_claude_response(self, content: str, issue: Dict) -> Dict:
        """Parse Claude's response to extract fix, explanation, and risk."""
        fixed_code = None
        explanation = "No fix generated"
        risk_level = "unknown"

        if "FIXED_CODE:" in content:
            code_section = content.split("FIXED_CODE:")[1]
            if "```" in code_section:
                parts = code_section.split("```")
                if len(parts) > 1:
                    fixed_code = parts[1].strip()

        if "EXPLANATION:" in content:
            exp_section = content.split("EXPLANATION:")[1]
            if "RISK:" in exp_section:
                explanation = exp_section.split("RISK:")[0].strip()
            else:
                explanation = exp_section.strip()[:200]

        if "RISK:" in content:
            risk_section = content.split("RISK:")[-1].strip()
            risk_word = risk_section.split()[0].lower() if risk_section else "unknown"
            if risk_word in ["low", "medium", "high"]:
                risk_level = risk_word

        return {
            "original_code": issue.get("code_snippet", ""),
            "suggested_fix": fixed_code,
            "explanation": explanation,
            "risk_level": risk_level,
        }

    def validate_fix(self, original_code: str, fixed_code: str) -> Dict[str, Any]:
        """Validate that a fix is syntactically correct."""
        import ast

        validation_result = {
            "syntax_valid": False,
            "can_compile": False,
            "warnings": [],
            "errors": [],
        }

        try:
            ast.parse(fixed_code)
            validation_result["syntax_valid"] = True
            validation_result["can_compile"] = True
        except SyntaxError as e:
            validation_result["errors"].append(f"Syntax error: {str(e)}")
        except Exception as e:
            validation_result["errors"].append(f"Parse error: {str(e)}")

        if len(fixed_code) > len(original_code) * 2:
            validation_result["warnings"].append("Fixed code is much longer than original")

        if not fixed_code.strip():
            validation_result["errors"].append("Fixed code is empty")

        return validation_result

    def estimate_risk(self, fix: Dict[str, Any]) -> str:
        """Estimate risk level of applying a fix."""
        risk_level = fix.get("risk_level", "unknown").lower()

        if risk_level in ["low", "minimal"]:
            return "low"
        elif risk_level in ["medium", "moderate"]:
            return "medium"
        elif risk_level in ["high", "critical"]:
            return "high"
        else:
            return "unknown"

    def explain_fix(self, fix: Dict[str, Any]) -> str:
        """Generate human-readable explanation of fix."""
        explanation = fix.get("explanation", "No explanation available")
        risk = fix.get("risk_level", "unknown")

        return f"{explanation}\n\nRisk Level: {risk}"
