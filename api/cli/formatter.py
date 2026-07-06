"""CodePulse CLI formatter for converting reports to different formats."""
import argparse
import json
from pathlib import Path
from typing import Dict, Any, List


class ReportFormatter:
    """Convert CodePulse reports to different formats."""

    def __init__(self, report_path: str):
        with open(report_path, 'r') as f:
            self.report = json.load(f)

    def to_sarif(self) -> Dict[str, Any]:
        """Convert CodePulse report to SARIF format."""
        runs = []

        findings = self.report.get('findings', [])
        results = []

        for finding in findings:
            result = {
                'ruleId': finding.get('rule', 'unknown'),
                'message': {
                    'text': finding.get('message', 'Issue found'),
                },
                'level': self._map_level(finding.get('severity', 'warning')),
                'locations': [{
                    'physicalLocation': {
                        'artifactLocation': {
                            'uri': finding.get('file', 'unknown'),
                        },
                        'region': {
                            'startLine': finding.get('line', 1),
                            'startColumn': finding.get('column', 1),
                        },
                    },
                }],
            }

            # Add properties if available
            if finding.get('cwe'):
                result['properties'] = {
                    'cwe': finding['cwe'],
                }

            results.append(result)

        runs.append({
            'tool': {
                'driver': {
                    'name': 'CodePulse',
                    'version': '3.5.0',
                    'informationUri': 'https://codepulse.dev',
                },
            },
            'results': results,
            'properties': {
                'summary': self.report.get('summary', {}),
            },
        })

        return {
            'version': '2.1.0',
            'runs': runs,
        }

    def to_json(self) -> Dict[str, Any]:
        """Return report as-is (already JSON)."""
        return self.report

    def to_junit(self) -> str:
        """Convert CodePulse report to JUnit XML format."""
        findings = self.report.get('findings', [])
        summary = self.report.get('summary', {})

        # Group findings by file
        by_file = {}
        for finding in findings:
            file = finding.get('file', 'unknown')
            if file not in by_file:
                by_file[file] = []
            by_file[file].append(finding)

        # Build XML
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<testsuites>\n'
        xml += f'  <testsuite name="CodePulse" tests="{len(findings)}" '
        xml += f'failures="{summary.get("critical", 0) + summary.get("error", 0)}" '
        xml += f'warnings="{summary.get("warning", 0)}">\n'

        for file_path, file_findings in by_file.items():
            for finding in file_findings:
                xml += '    <testcase '
                xml += f'name="{finding.get("rule", "unknown")}" '
                xml += f'classname="{file_path}" '
                xml += f'line="{finding.get("line", 1)}">\n'

                severity = finding.get('severity', 'warning').lower()
                if severity in ['critical', 'error']:
                    xml += f'      <failure type="{severity}" message="{finding.get("message", "Issue found")}" />\n'
                elif severity == 'warning':
                    xml += f'      <skipped message="{finding.get("message", "Issue found")}" />\n'

                xml += '    </testcase>\n'

        xml += '  </testsuite>\n'
        xml += '</testsuites>\n'

        return xml

    def to_sonarqube(self) -> Dict[str, Any]:
        """Convert CodePulse report to SonarQube format."""
        findings = self.report.get('findings', [])
        issues = []

        for finding in findings:
            issue = {
                'engineId': 'codepulse',
                'ruleId': finding.get('rule', 'unknown'),
                'primaryLocation': {
                    'message': finding.get('message', 'Issue found'),
                    'filePath': finding.get('file', 'unknown'),
                    'startLine': finding.get('line', 1),
                },
                'effortMinutes': self._map_effort(finding.get('severity', 'warning')),
                'type': self._map_type(finding.get('severity', 'warning')),
                'severity': finding.get('severity', 'warning').upper(),
            }

            issues.append(issue)

        return {
            'issues': issues,
        }

    @staticmethod
    def _map_level(severity: str) -> str:
        """Map CodePulse severity to SARIF level."""
        mapping = {
            'critical': 'error',
            'error': 'error',
            'warning': 'warning',
            'info': 'note',
        }
        return mapping.get(severity.lower(), 'warning')

    @staticmethod
    def _map_type(severity: str) -> str:
        """Map CodePulse severity to SonarQube type."""
        if severity.lower() in ['critical', 'error']:
            return 'BUG'
        return 'CODE_SMELL'

    @staticmethod
    def _map_effort(severity: str) -> int:
        """Map CodePulse severity to effort minutes."""
        mapping = {
            'critical': 60,
            'error': 30,
            'warning': 15,
            'info': 5,
        }
        return mapping.get(severity.lower(), 5)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='CodePulse Report Formatter'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Input report file (JSON)'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Output file path'
    )
    parser.add_argument(
        '--format',
        default='json',
        choices=['json', 'sarif', 'junit', 'sonarqube'],
        help='Output format (default: json)'
    )

    args = parser.parse_args()

    # Read and convert report
    formatter = ReportFormatter(args.input)

    if args.format == 'sarif':
        result = formatter.to_sarif()
        output = json.dumps(result, indent=2)
    elif args.format == 'junit':
        result = formatter.to_junit()
        output = result
    elif args.format == 'sonarqube':
        result = formatter.to_sonarqube()
        output = json.dumps(result, indent=2)
    else:  # json
        result = formatter.to_json()
        output = json.dumps(result, indent=2)

    # Write output
    with open(args.output, 'w') as f:
        f.write(output)

    print(f"✅ Report formatted as {args.format}")
    print(f"   Output: {args.output}")


if __name__ == '__main__':
    main()
