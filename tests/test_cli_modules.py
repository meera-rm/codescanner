"""Tests for CLI modules (scanner and formatter)."""
import pytest
import json
import tempfile
import os
from pathlib import Path

# Add api to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.cli.scanner import RepositoryScanner
from api.cli.formatter import ReportFormatter


class TestRepositoryScanner:
    """Test the RepositoryScanner class."""

    def test_scanner_groups_files_by_language(self):
        """Test file grouping by language."""
        scanner = RepositoryScanner('.')
        files = [
            'src/main.py',
            'src/app.js',
            'src/schema.sql',
            'src/readme.md',
        ]
        grouped = scanner._group_by_language(files)

        assert len(grouped['python']) == 1
        assert len(grouped['javascript']) == 1
        assert len(grouped['sql']) == 1
        assert len(grouped['other']) == 1

    def test_scanner_handles_different_js_extensions(self):
        """Test that all JS extensions are grouped correctly."""
        scanner = RepositoryScanner('.')
        files = [
            'src/app.js',
            'src/app.ts',
            'src/component.jsx',
            'src/component.tsx',
        ]
        grouped = scanner._group_by_language(files)

        assert len(grouped['javascript']) == 4

    def test_scanner_summarizes_findings(self):
        """Test finding summary."""
        scanner = RepositoryScanner('.')
        scanner.findings = [
            {'severity': 'critical', 'message': 'Issue 1'},
            {'severity': 'critical', 'message': 'Issue 2'},
            {'severity': 'error', 'message': 'Issue 3'},
            {'severity': 'warning', 'message': 'Issue 4'},
            {'severity': 'warning', 'message': 'Issue 5'},
            {'severity': 'info', 'message': 'Issue 6'},
        ]
        summary = scanner._summarize()

        assert summary['critical'] == 2
        assert summary['error'] == 1
        assert summary['warning'] == 2
        assert summary['info'] == 1
        assert summary['total'] == 6

    def test_scanner_scan_returns_correct_structure(self):
        """Test that scan returns expected structure."""
        scanner = RepositoryScanner('.')
        result = scanner.scan()

        assert 'status' in result
        assert 'repository' in result
        assert 'files_scanned' in result
        assert 'files_by_language' in result
        assert 'findings' in result
        assert 'summary' in result

        assert result['status'] == 'completed'
        assert result['repository'] == '.'


class TestReportFormatter:
    """Test the ReportFormatter class."""

    @pytest.fixture
    def sample_report(self):
        """Create a sample report for testing."""
        return {
            'status': 'completed',
            'repository': '.',
            'files_scanned': 100,
            'files_by_language': {
                'python': 50,
                'javascript': 30,
                'sql': 5,
                'other': 15,
            },
            'findings': [
                {
                    'rule': 'hardcoded_secret',
                    'message': 'Hardcoded password found',
                    'file': './config.py',
                    'line': 42,
                    'column': 10,
                    'severity': 'critical',
                    'cwe': 'CWE-798',
                },
                {
                    'rule': 'sql_injection',
                    'message': 'Potential SQL injection',
                    'file': './db/query.sql',
                    'line': 5,
                    'column': 1,
                    'severity': 'error',
                },
                {
                    'rule': 'unused_import',
                    'message': 'Unused import detected',
                    'file': './main.py',
                    'line': 3,
                    'column': 1,
                    'severity': 'warning',
                },
            ],
            'summary': {
                'critical': 1,
                'error': 1,
                'warning': 1,
                'info': 0,
                'total': 3,
            },
        }

    def test_formatter_to_sarif(self, sample_report):
        """Test SARIF format conversion."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_report, f)
            f.flush()

            formatter = ReportFormatter(f.name)
            sarif = formatter.to_sarif()

            assert sarif['version'] == '2.1.0'
            assert len(sarif['runs']) == 1
            assert sarif['runs'][0]['tool']['driver']['name'] == 'CodePulse'
            assert len(sarif['runs'][0]['results']) == 3

            # Check first result
            result = sarif['runs'][0]['results'][0]
            assert result['ruleId'] == 'hardcoded_secret'
            assert result['level'] == 'error'  # critical maps to error
            assert result['locations'][0]['physicalLocation']['artifactLocation']['uri'] == './config.py'
            assert result['locations'][0]['physicalLocation']['region']['startLine'] == 42

            os.unlink(f.name)

    def test_formatter_to_junit(self, sample_report):
        """Test JUnit XML format conversion."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_report, f)
            f.flush()

            formatter = ReportFormatter(f.name)
            junit_xml = formatter.to_junit()

            assert '<?xml version="1.0"' in junit_xml
            assert '<testsuites>' in junit_xml
            assert '<testsuite' in junit_xml
            assert 'tests="3"' in junit_xml
            assert 'failures="2"' in junit_xml
            assert 'warnings="1"' in junit_xml
            assert '<testcase' in junit_xml

            os.unlink(f.name)

    def test_formatter_to_sonarqube(self, sample_report):
        """Test SonarQube format conversion."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_report, f)
            f.flush()

            formatter = ReportFormatter(f.name)
            sonarqube = formatter.to_sonarqube()

            assert 'issues' in sonarqube
            assert len(sonarqube['issues']) == 3

            # Check first issue (critical)
            issue = sonarqube['issues'][0]
            assert issue['engineId'] == 'codepulse'
            assert issue['ruleId'] == 'hardcoded_secret'
            assert issue['type'] == 'BUG'  # critical maps to BUG
            assert issue['severity'] == 'CRITICAL'
            assert issue['effortMinutes'] == 60  # critical effort

            # Check second issue (error)
            issue = sonarqube['issues'][1]
            assert issue['severity'] == 'ERROR'
            assert issue['effortMinutes'] == 30  # error effort

            # Check third issue (warning)
            issue = sonarqube['issues'][2]
            assert issue['severity'] == 'WARNING'
            assert issue['type'] == 'CODE_SMELL'  # warning maps to CODE_SMELL
            assert issue['effortMinutes'] == 15  # warning effort

            os.unlink(f.name)

    def test_formatter_severity_mapping(self):
        """Test severity level mapping."""
        assert ReportFormatter._map_level('critical') == 'error'
        assert ReportFormatter._map_level('error') == 'error'
        assert ReportFormatter._map_level('warning') == 'warning'
        assert ReportFormatter._map_level('info') == 'note'

    def test_formatter_type_mapping(self):
        """Test SonarQube type mapping."""
        assert ReportFormatter._map_type('critical') == 'BUG'
        assert ReportFormatter._map_type('error') == 'BUG'
        assert ReportFormatter._map_type('warning') == 'CODE_SMELL'
        assert ReportFormatter._map_type('info') == 'CODE_SMELL'

    def test_formatter_effort_mapping(self):
        """Test effort minutes mapping."""
        assert ReportFormatter._map_effort('critical') == 60
        assert ReportFormatter._map_effort('error') == 30
        assert ReportFormatter._map_effort('warning') == 15
        assert ReportFormatter._map_effort('info') == 5


class TestCLIIntegration:
    """Integration tests for CLI modules."""

    def test_full_scan_and_format_pipeline(self):
        """Test scanning and formatting in sequence."""
        # Scan
        scanner = RepositoryScanner('.')
        result = scanner.scan()

        # Save report
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(result, f)
            report_path = f.name

        # Format to SARIF
        formatter = ReportFormatter(report_path)
        sarif = formatter.to_sarif()

        # Verify
        assert sarif['version'] == '2.1.0'
        assert len(sarif['runs']) > 0
        assert 'tool' in sarif['runs'][0]
        assert sarif['runs'][0]['tool']['driver']['name'] == 'CodePulse'

        os.unlink(report_path)

    def test_scanner_output_file_format(self):
        """Test that scanner produces valid JSON output."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name

        scanner = RepositoryScanner('.')
        result = scanner.scan()

        # Write to file
        with open(output_file, 'w') as f:
            json.dump(result, f)

        # Read and verify
        with open(output_file, 'r') as f:
            loaded = json.load(f)

        assert loaded == result
        assert 'summary' in loaded
        assert 'findings' in loaded

        os.unlink(output_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
