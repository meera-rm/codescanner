pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.12'
        WORKSPACE_DIR = "${WORKSPACE}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    echo "✅ Code checked out from ${GIT_BRANCH}"
                }
            }
        }

        stage('Setup Python') {
            steps {
                script {
                    sh '''
                        python3 --version
                        pip3 install --upgrade pip
                        if [ -f api/requirements.txt ]; then
                            pip3 install -r api/requirements.txt
                        fi
                    '''
                }
            }
        }

        stage('CodePulse Scan') {
            steps {
                script {
                    try {
                        sh '''
                            echo "🔍 Starting CodePulse scan..."
                            python3 -m api.cli.scanner \
                                --repository . \
                                --output-file codepulse-report.json \
                                --fail-on-critical false
                            echo "✅ Scan completed"
                        '''
                    } catch (Exception e) {
                        echo "⚠️  Scan failed: ${e.message}"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }

        stage('Generate Reports') {
            steps {
                script {
                    try {
                        sh '''
                            echo "📋 Generating report formats..."

                            # Generate SARIF report
                            python3 -m api.cli.formatter \
                                --input codepulse-report.json \
                                --output codepulse-report.sarif \
                                --format sarif

                            # Generate JUnit report
                            python3 -m api.cli.formatter \
                                --input codepulse-report.json \
                                --output codepulse-report.junit \
                                --format junit

                            # Generate SonarQube report
                            python3 -m api.cli.formatter \
                                --input codepulse-report.json \
                                --output codepulse-report-sonarqube.json \
                                --format sonarqube

                            echo "✅ Reports generated successfully"
                        '''
                    } catch (Exception e) {
                        echo "⚠️  Report generation failed: ${e.message}"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }

        stage('Publish Results') {
            steps {
                script {
                    // Publish JUnit test results
                    junit testResults: 'codepulse-report.junit',
                          allowEmptyResults: true,
                          skipPublishingChecks: true

                    // Archive reports
                    archiveArtifacts artifacts: 'codepulse-report*.json,codepulse-report*.sarif,codepulse-report*.junit',
                                     allowEmptyArchive: true,
                                     fingerprint: true

                    echo "✅ Results published"
                }
            }
        }

        stage('Check Critical Issues') {
            steps {
                script {
                    def report = readJSON file: 'codepulse-report.json'
                    def summary = report.summary ?: [:]
                    def critical = summary.critical ?: 0
                    def errors = summary.error ?: 0
                    def warnings = summary.warning ?: 0
                    def total = summary.total ?: 0

                    echo """
                    📊 CodePulse Scan Summary
                       Critical: ${critical}
                       Error: ${errors}
                       Warning: ${warnings}
                       Total: ${total}
                    """

                    if (critical > 0) {
                        echo "❌ Critical issues found - failing build"
                        currentBuild.result = 'FAILURE'
                        error("Critical issues detected in code scan")
                    } else if (errors > 0) {
                        echo "⚠️  Error issues found - review required"
                        currentBuild.result = 'UNSTABLE'
                    } else {
                        echo "✅ No critical or error issues found"
                        currentBuild.result = 'SUCCESS'
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                echo "🔄 Cleaning up workspace..."
                cleanWs deleteDirs: true,
                        patterns: [[pattern: '**/codepulse-*.tmp', type: 'INCLUDE']]
            }
        }

        success {
            script {
                echo "✅ Pipeline completed successfully"
                // Optional: Send success notification
                // emailext(
                //     subject: "Build Success: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                //     body: "CodePulse scan completed successfully with no critical issues.",
                //     to: "${env.CHANGE_AUTHOR_EMAIL}"
                // )
            }
        }

        unstable {
            script {
                echo "⚠️  Pipeline completed with warnings"
                // Optional: Send warning notification
            }
        }

        failure {
            script {
                echo "❌ Pipeline failed"
                // Optional: Send failure notification
                // emailext(
                //     subject: "Build Failure: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                //     body: "CodePulse scan found critical issues. Please review the report.",
                //     to: "${env.CHANGE_AUTHOR_EMAIL}",
                //     attachmentsPattern: 'codepulse-report*.json'
                // )
            }
        }
    }
}
