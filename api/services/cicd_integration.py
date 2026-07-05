"""
CI/CD Integration - Phase 6.2.2
Integrates CodePulse AI with CI/CD pipelines (GitHub Actions, GitLab CI, Jenkins)
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import time


class CIPlatform(str, Enum):
    """CI/CD platform types"""
    GITHUB_ACTIONS = "github_actions"
    GITLAB_CI = "gitlab_ci"
    JENKINS = "jenkins"
    CIRCLE_CI = "circle_ci"


@dataclass
class CIJobConfig:
    """CI job configuration"""
    platform: CIPlatform
    job_name: str
    api_endpoint: str
    api_key: Optional[str] = None
    timeout_seconds: int = 300
    fail_on_findings: bool = False
    min_quality_score: float = 60.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform": self.platform.value,
            "job_name": self.job_name,
            "timeout": self.timeout_seconds,
            "fail_on_findings": self.fail_on_findings,
            "min_quality_score": self.min_quality_score
        }


@dataclass
class CIPipelineRun:
    """CI pipeline run record"""
    run_id: str
    platform: CIPlatform
    job_name: str
    status: str  # success, failure, running
    quality_score: float
    findings_count: int
    duration_seconds: float
    timestamp: float = field(default_factory=time.time)
    logs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "platform": self.platform.value,
            "job_name": self.job_name,
            "status": self.status,
            "quality_score": self.quality_score,
            "findings": self.findings_count,
            "duration_seconds": self.duration_seconds
        }


class CICDIntegration:
    """Integrates CodePulse AI with CI/CD systems"""

    def __init__(self):
        self.jobs: Dict[str, CIJobConfig] = {}
        self.runs: Dict[str, CIPipelineRun] = {}
        self.workflows: Dict[str, Dict[str, Any]] = {}

    def register_job(
        self,
        platform: CIPlatform,
        job_name: str,
        api_endpoint: str,
        api_key: Optional[str] = None,
        fail_on_findings: bool = False,
        min_quality_score: float = 60.0
    ) -> CIJobConfig:
        """Register a CI job"""
        job = CIJobConfig(
            platform=platform,
            job_name=job_name,
            api_endpoint=api_endpoint,
            api_key=api_key,
            fail_on_findings=fail_on_findings,
            min_quality_score=min_quality_score
        )
        self.jobs[job_name] = job
        return job

    def get_github_actions_workflow(self) -> str:
        """Generate GitHub Actions workflow YAML"""
        workflow = """name: CodePulse AI Analysis

on:
  pull_request:
    branches: [ main, develop ]
  push:
    branches: [ main ]

jobs:
  code-analysis:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Run CodePulse AI Analysis
        uses: codepulse-ai/scanner@v1
        with:
          api-key: ${{ secrets.CODEPULSE_API_KEY }}
          min-quality-score: 60
          fail-on-findings: false
      
      - name: Upload Results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: code-analysis-results
          path: ./codepulse-report.json
      
      - name: Comment PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(fs.readFileSync('./codepulse-report.json', 'utf8'));
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: report.pr_comment
            });
"""
        self.workflows["github_actions"] = json.loads(json.dumps({"content": workflow}))
        return workflow

    def get_gitlab_ci_pipeline(self) -> str:
        """Generate GitLab CI pipeline YAML"""
        pipeline = """stages:
  - analyze
  - report

codepulse_analysis:
  stage: analyze
  image: python:3.11
  script:
    - pip install codepulse-ai
    - |
      codepulse scan \\
        --directory . \\
        --api-key $CODEPULSE_API_KEY \\
        --min-quality-score 60 \\
        --output json \\
        --report codepulse-report.json
    - |
      QUALITY_SCORE=$(jq '.quality_score' codepulse-report.json)
      if [ $QUALITY_SCORE -lt 60 ]; then
        echo "Quality score $QUALITY_SCORE below threshold"
        exit 1
      fi
  artifacts:
    reports:
      codequality: codepulse-report.json
    paths:
      - codepulse-report.json
    expire_in: 1 week
  only:
    - merge_requests
    - main
  allow_failure: true

generate_report:
  stage: report
  image: python:3.11
  script:
    - pip install codepulse-ai
    - codepulse report codepulse-report.json --format html
  artifacts:
    paths:
      - codepulse-report.html
    expire_in: 30 days
  only:
    - merge_requests
"""
        self.workflows["gitlab_ci"] = json.loads(json.dumps({"content": pipeline}))
        return pipeline

    def get_jenkins_pipeline(self) -> str:
        """Generate Jenkins Declarative Pipeline"""
        pipeline = """pipeline {
    agent any
    
    environment {
        CODEPULSE_API_KEY = credentials('codepulse-api-key')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('CodePulse Analysis') {
            steps {
                script {
                    sh '''
                        pip install codepulse-ai
                        codepulse scan \\
                            --directory . \\
                            --api-key $CODEPULSE_API_KEY \\
                            --min-quality-score 60 \\
                            --output json \\
                            --report codepulse-report.json
                    '''
                }
            }
        }
        
        stage('Quality Gate') {
            steps {
                script {
                    def report = readJSON file: 'codepulse-report.json'
                    def score = report.quality_score
                    echo "Code Quality Score: ${score}"
                    
                    if (score < 60) {
                        error("Quality score ${score} below threshold of 60")
                    }
                }
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'codepulse-report.json', allowEmptyArchive: true
            publishHTML([
                reportDir: '.',
                reportFiles: 'codepulse-report.html',
                reportName: 'CodePulse Report'
            ])
        }
        failure {
            echo 'Code analysis failed'
        }
    }
}
"""
        self.workflows["jenkins"] = json.loads(json.dumps({"content": pipeline}))
        return pipeline

    def record_pipeline_run(
        self,
        platform: CIPlatform,
        job_name: str,
        quality_score: float,
        findings_count: int,
        duration_seconds: float
    ) -> CIPipelineRun:
        """Record a pipeline run"""
        import secrets

        status = "success" if quality_score >= 60 else "failure"
        run = CIPipelineRun(
            run_id=f"run_{secrets.token_hex(8)}",
            platform=platform,
            job_name=job_name,
            status=status,
            quality_score=quality_score,
            findings_count=findings_count,
            duration_seconds=duration_seconds
        )

        self.runs[run.run_id] = run
        return run

    def get_run_history(
        self,
        platform: Optional[CIPlatform] = None,
        limit: int = 10
    ) -> List[CIPipelineRun]:
        """Get pipeline run history"""
        runs = list(self.runs.values())
        
        if platform:
            runs = [r for r in runs if r.platform == platform]
        
        runs.sort(key=lambda r: r.timestamp, reverse=True)
        return runs[:limit]

    def get_integration_status(self) -> Dict[str, Any]:
        """Get CI/CD integration status"""
        return {
            "jobs_registered": len(self.jobs),
            "platforms": [job.platform.value for job in self.jobs.values()],
            "total_runs": len(self.runs),
            "workflows_configured": list(self.workflows.keys()),
            "success_rate": self._calculate_success_rate()
        }

    def _calculate_success_rate(self) -> float:
        """Calculate success rate of all runs"""
        if not self.runs:
            return 0.0
        
        successful = sum(1 for r in self.runs.values() if r.status == "success")
        return (successful / len(self.runs)) * 100


_global_cicd_integration = CICDIntegration()

def get_cicd_integration() -> CICDIntegration:
    """Get global CI/CD integration instance"""
    return _global_cicd_integration
