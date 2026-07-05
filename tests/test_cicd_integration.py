"""
Tests for CI/CD Integration - Phase 6.2.2
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.cicd_integration import (
    CICDIntegration,
    CIPlatform,
    CIJobConfig
)


class TestCICDIntegration:
    """Test CI/CD integration"""

    def test_register_job(self):
        """Test registering CI job"""
        integration = CICDIntegration()

        job = integration.register_job(
            platform=CIPlatform.GITHUB_ACTIONS,
            job_name="code-analysis",
            api_endpoint="https://api.github.com",
            api_key="test_key",
            fail_on_findings=True,
            min_quality_score=70.0
        )

        assert job.job_name == "code-analysis"
        assert job.platform == CIPlatform.GITHUB_ACTIONS
        assert job.min_quality_score == 70.0

    def test_github_actions_workflow(self):
        """Test GitHub Actions workflow generation"""
        integration = CICDIntegration()

        workflow = integration.get_github_actions_workflow()

        assert "name: CodePulse AI Analysis" in workflow
        assert "pull_request" in workflow
        assert "CODEPULSE_API_KEY" in workflow

    def test_gitlab_ci_pipeline(self):
        """Test GitLab CI pipeline generation"""
        integration = CICDIntegration()

        pipeline = integration.get_gitlab_ci_pipeline()

        assert "stages:" in pipeline
        assert "codepulse_analysis:" in pipeline
        assert "quality_score" in pipeline

    def test_jenkins_pipeline(self):
        """Test Jenkins pipeline generation"""
        integration = CICDIntegration()

        pipeline = integration.get_jenkins_pipeline()

        assert "pipeline {" in pipeline
        assert "stages {" in pipeline
        assert "CodePulse Analysis" in pipeline
        assert "Quality Gate" in pipeline

    def test_record_pipeline_run(self):
        """Test recording pipeline run"""
        integration = CICDIntegration()

        run = integration.record_pipeline_run(
            platform=CIPlatform.GITHUB_ACTIONS,
            job_name="analysis",
            quality_score=85.0,
            findings_count=3,
            duration_seconds=45.2
        )

        assert run.run_id.startswith("run_")
        assert run.status == "success"
        assert run.quality_score == 85.0

    def test_run_failure_status(self):
        """Test run marked as failure when score below threshold"""
        integration = CICDIntegration()

        run = integration.record_pipeline_run(
            platform=CIPlatform.GITLAB_CI,
            job_name="analysis",
            quality_score=45.0,
            findings_count=10,
            duration_seconds=30.0
        )

        assert run.status == "failure"

    def test_run_history(self):
        """Test getting run history"""
        integration = CICDIntegration()

        # Record multiple runs
        for i in range(5):
            integration.record_pipeline_run(
                platform=CIPlatform.GITHUB_ACTIONS,
                job_name="analysis",
                quality_score=80.0 + (i * 2),
                findings_count=i,
                duration_seconds=30.0
            )

        history = integration.get_run_history(limit=3)

        assert len(history) == 3
        assert all(r.platform == CIPlatform.GITHUB_ACTIONS for r in history)

    def test_run_history_by_platform(self):
        """Test filtering run history by platform"""
        integration = CICDIntegration()

        # Record runs on different platforms
        integration.record_pipeline_run(
            platform=CIPlatform.GITHUB_ACTIONS,
            job_name="gh",
            quality_score=80.0,
            findings_count=2,
            duration_seconds=30.0
        )

        integration.record_pipeline_run(
            platform=CIPlatform.JENKINS,
            job_name="jenkins",
            quality_score=75.0,
            findings_count=5,
            duration_seconds=45.0
        )

        gh_runs = integration.get_run_history(platform=CIPlatform.GITHUB_ACTIONS)
        jenkins_runs = integration.get_run_history(platform=CIPlatform.JENKINS)

        assert len(gh_runs) == 1
        assert len(jenkins_runs) == 1
        assert gh_runs[0].job_name == "gh"

    def test_integration_status(self):
        """Test integration status"""
        integration = CICDIntegration()

        integration.register_job(
            platform=CIPlatform.GITHUB_ACTIONS,
            job_name="gh",
            api_endpoint="https://api.github.com"
        )

        integration.register_job(
            platform=CIPlatform.JENKINS,
            job_name="jenkins",
            api_endpoint="http://jenkins.local"
        )

        status = integration.get_integration_status()

        assert status["jobs_registered"] == 2
        assert "github_actions" in status["platforms"]
        assert "jenkins" in status["platforms"]

    def test_success_rate(self):
        """Test success rate calculation"""
        integration = CICDIntegration()

        # Record 3 successful and 2 failed runs
        for i in range(3):
            integration.record_pipeline_run(
                platform=CIPlatform.GITHUB_ACTIONS,
                job_name="analysis",
                quality_score=80.0,
                findings_count=0,
                duration_seconds=30.0
            )

        for i in range(2):
            integration.record_pipeline_run(
                platform=CIPlatform.GITHUB_ACTIONS,
                job_name="analysis",
                quality_score=50.0,
                findings_count=10,
                duration_seconds=30.0
            )

        status = integration.get_integration_status()
        assert status["success_rate"] == pytest.approx(60.0)

    def test_job_config_to_dict(self):
        """Test job config serialization"""
        job = CIJobConfig(
            platform=CIPlatform.GITLAB_CI,
            job_name="test",
            api_endpoint="http://gitlab.local",
            fail_on_findings=True,
            min_quality_score=75.0
        )

        job_dict = job.to_dict()

        assert job_dict["job_name"] == "test"
        assert job_dict["fail_on_findings"] is True

    def test_pipeline_run_to_dict(self):
        """Test pipeline run serialization"""
        integration = CICDIntegration()

        run = integration.record_pipeline_run(
            platform=CIPlatform.JENKINS,
            job_name="analysis",
            quality_score=85.0,
            findings_count=2,
            duration_seconds=40.0
        )

        run_dict = run.to_dict()

        assert run_dict["platform"] == "jenkins"
        assert run_dict["quality_score"] == 85.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
