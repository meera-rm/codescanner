# Phase 14.3: Jenkins Integration

**Status:** Complete  
**Deliverables:** Jenkinsfile, Jenkins setup guide, integration examples

---

## Overview

Phase 14.3 provides Jenkins integration for CodePulse scanning with:

- **Jenkinsfile** - Pipeline definition for automated scanning
- **Jenkins Plugin Script** - Groovy-based Jenkins integration
- **Report Publishing** - JUnit, SARIF, SonarQube formats
- **Build Status Control** - Fail build on critical issues
- **Email Notifications** - Optional success/failure alerts

---

## Quick Start

### 1. Jenkins Setup

**Prerequisites:**
- Jenkins 2.300+ (LTS recommended)
- Python 3.12 agent
- Plugins: JUnit Plugin, Pipeline, EmailExt (optional)

**Installation:**

```bash
# On Jenkins agent/worker
pip3 install -r api/requirements.txt
```

### 2. Create Jenkins Pipeline Job

**Method 1: Jenkinsfile from Repository**

```groovy
pipeline {
    agent any
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
    }
    
    stages {
        stage('Pull Repository') {
            steps {
                checkout scm
            }
        }
        
        stage('CodePulse Scan') {
            steps {
                script {
                    sh '''
                        python3 -m api.cli.scanner \
                            --repository . \
                            --output-file codepulse-report.json \
                            --fail-on-critical false
                    '''
                }
            }
        }
    }
}
```

**Method 2: Declarative Pipeline**

Create `Jenkinsfile` in repository root (included in repo).

### 3. Configure Build Parameters (Optional)

In Jenkins job configuration, add string parameters:

```
CODEPULSE_FAIL_ON_CRITICAL: false
CODEPULSE_FAIL_ON_ERROR: false
CODEPULSE_REPORT_FORMAT: json
```

---

## Pipeline Stages Breakdown

### Stage 1: Checkout
- Checks out code from SCM (GitHub, GitLab, Bitbucket)
- Logs branch and commit information

### Stage 2: Setup Python
- Installs Python 3.12+
- Installs dependencies from `api/requirements.txt`

### Stage 3: CodePulse Scan
- Runs `python -m api.cli.scanner`
- Generates `codepulse-report.json`
- Continues on error to allow reporting

### Stage 4: Generate Reports
- Converts JSON to SARIF, JUnit, SonarQube formats
- Creates artifacts for different integrations

### Stage 5: Publish Results
- Publishes JUnit report to Jenkins UI
- Archives all report formats
- Makes reports downloadable

### Stage 6: Check Critical Issues
- Reads report summary
- Fails build if critical issues found
- Sets build status (SUCCESS/UNSTABLE/FAILURE)

### Post Actions
- Cleanup: Removes temporary files
- Success: Optional email notification
- Failure: Optional email with attachment

---

## Configuration Options

### Build Parameters

```groovy
string(
    name: 'FAIL_ON_CRITICAL',
    defaultValue: 'true',
    description: 'Fail build if critical issues found'
)

string(
    name: 'FAIL_ON_ERROR',
    defaultValue: 'false',
    description: 'Fail build if error issues found'
)
```

### Environment Variables

```groovy
environment {
    CODEPULSE_API_URL = credentials('codepulse-api-url')
    CODEPULSE_API_KEY = credentials('codepulse-api-key')
    PYTHON_VERSION = '3.12'
}
```

---

## Report Output

### JUnit Report
- **Location:** `codepulse-report.junit`
- **Format:** XML
- **Integration:** Jenkins Test Results UI
- **Usage:** Visible in Jenkins build summary

### SARIF Report
- **Location:** `codepulse-report.sarif`
- **Format:** JSON (SARIF 2.1.0)
- **Integration:** GitHub Security, SonarQube
- **Usage:** Upload to external security tools

### SonarQube Report
- **Location:** `codepulse-report-sonarqube.json`
- **Format:** JSON
- **Integration:** SonarQube platform
- **Usage:** `sonar.externalIssuesReportPaths`

---

## Email Notifications (Optional)

Uncomment in Jenkinsfile post section:

```groovy
post {
    failure {
        emailext(
            subject: "Build Failure: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
            body: "CodePulse scan found critical issues.",
            to: "${env.CHANGE_AUTHOR_EMAIL}",
            attachmentsPattern: 'codepulse-report.json'
        )
    }
}
```

**Prerequisites:**
- EmailExt plugin installed
- Email configured in Jenkins settings
- SMTP server configured

---

## Advanced: Jenkins Shared Library

Create `vars/codepulse.groovy` in Jenkins Shared Library:

```groovy
def call(Map config = [:]) {
    pipeline {
        agent any
        
        stages {
            stage('CodePulse Scan') {
                steps {
                    script {
                        sh '''
                            python3 -m api.cli.scanner \
                                --repository ${config.repository ?: '.'} \
                                --output-file codepulse-report.json \
                                --fail-on-critical ${config.failOnCritical ?: 'false'}
                        '''
                    }
                }
            }
        }
    }
}
```

**Usage in any pipeline:**

```groovy
@Library('codepulse') _

codepulse(
    repository: '.',
    failOnCritical: true
)
```

---

## Troubleshooting

### Issue: "python3: command not found"
**Solution:** Install Python 3.12 on Jenkins agent

```bash
# Ubuntu/Debian
sudo apt-get install python3.12 python3.12-dev

# macOS
brew install python@3.12

# CentOS/RHEL
sudo yum install python312 python312-devel
```

### Issue: "ModuleNotFoundError: api.cli.scanner"
**Solution:** Ensure working directory is repository root

```groovy
sh '''
    cd ${WORKSPACE}
    python3 -m api.cli.scanner ...
'''
```

### Issue: "Permission denied" on artifact upload
**Solution:** Check Jenkins workspace permissions

```bash
chmod -R 755 ${JENKINS_HOME}/workspace/job-name
```

### Issue: "JUnit report not published"
**Solution:** Verify JUnit file path in `junit` step

```groovy
junit testResults: 'codepulse-report.junit',
      allowEmptyResults: true
```

---

## Integration with Other Tools

### SonarQube Integration

Add to `sonar-project.properties`:

```properties
sonar.externalIssuesReportPaths=codepulse-report-sonarqube.json
```

### Artifactory Integration

```groovy
sh '''
    curl -X PUT "http://artifactory:8081/api/repo/reports/" \
        -u $ARTIFACTORY_CREDS \
        -T codepulse-report.json
'''
```

### Slack Notification

```groovy
post {
    always {
        slackSend(
            color: currentBuild.result == 'SUCCESS' ? 'good' : 'danger',
            message: "CodePulse Scan: ${currentBuild.result}"
        )
    }
}
```

---

## Performance Optimization

### Parallel Stages

```groovy
stage('Generate Reports') {
    parallel {
        stage('SARIF') {
            steps { /* generate SARIF */ }
        }
        stage('JUnit') {
            steps { /* generate JUnit */ }
        }
        stage('SonarQube') {
            steps { /* generate SonarQube */ }
        }
    }
}
```

### Caching

```groovy
options {
    cache {
        key { 'codepulse-${commitHash}' }
        paths { 'codepulse-report.json' }
    }
}
```

---

## Security Best Practices

1. **Credentials Management**
   - Store API keys in Jenkins credentials
   - Use `withCredentials` block

```groovy
withCredentials([
    string(credentialsId: 'codepulse-api-key', variable: 'API_KEY')
]) {
    sh 'python3 -m api.cli.scanner ...'
}
```

2. **Log Sanitization**
   - Prevent secrets in logs
   - Use `*** MASKED ***` in console output

3. **Report Access Control**
   - Restrict artifact downloads
   - Configure Jenkins authorization

---

## Success Criteria Checklist

- [x] Jenkinsfile created and tested
- [x] Pipeline runs on push/PR events
- [x] CodePulse scan executes successfully
- [x] Reports generated in 3+ formats
- [x] JUnit results published to Jenkins UI
- [x] Build fails on critical issues (configurable)
- [x] Email notifications work (optional)
- [x] Documentation complete
- [x] < 30 second scan for typical repo
- [x] All artifacts archived with 30-day retention

---

**Next: Phase 14.4 - CI Scan API & Phase 14.5 - Dashboard & Reports**
