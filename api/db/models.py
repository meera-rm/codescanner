from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON, Text, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from api.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    api_keys = relationship("ApiKey", back_populates="user")
    scan_jobs = relationship("ScanJob", back_populates="user")
    webhooks = relationship("Webhook", back_populates="user")


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    name = Column(String, index=True)
    token_hash = Column(String, unique=True, index=True)
    rate_limit = Column(Integer, default=100)
    scopes = Column(JSON, default=["scan", "onboarding", "creative-suite"])
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    last_used = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="api_keys")


class ScanJob(Base):
    __tablename__ = "scan_jobs"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    directory_path = Column(String)
    language = Column(String, default="python")
    status = Column(String, default="queued")
    progress = Column(Integer, default=0)
    findings = Column(JSON, default=[])
    metrics = Column(JSON, default={})
    duration_ms = Column(Integer, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="scan_jobs")


class OnboardingProfile(Base):
    __tablename__ = "onboarding_profiles"

    id = Column(String, primary_key=True, index=True)
    directory_path = Column(String)
    tone = Column(String, default="neutral")
    profile_data = Column(JSON)
    html_content = Column(Text, nullable=True)
    markdown_content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CreativeSuiteResult(Base):
    __tablename__ = "creative_suite_results"

    id = Column(String, primary_key=True, index=True)
    directory_path = Column(String)
    personality = Column(JSON)
    letter = Column(JSON)
    caqi = Column(JSON)
    dashboard_html = Column(Text, nullable=True)
    markdown_report = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Webhook(Base):
    __tablename__ = "webhooks"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    url = Column(String)
    event_types = Column(JSON, default=["scan.completed"])
    secret = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="webhooks")


class Metrics(Base):
    __tablename__ = "metrics"

    id = Column(String, primary_key=True, index=True)
    scan_job_id = Column(String, ForeignKey("scan_jobs.id"), nullable=True)
    quality_score = Column(Float)
    complexity = Column(Float)
    security_issues = Column(Integer)
    code_smells = Column(Integer)
    documentation_coverage = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class RefactorSuggestion(Base):
    __tablename__ = "refactor_suggestions"

    id = Column(String, primary_key=True, index=True)
    scan_job_id = Column(String, ForeignKey("scan_jobs.id"))
    issue_type = Column(String)
    original_code = Column(Text)
    suggested_fix = Column(Text)
    explanation = Column(Text)
    risk_level = Column(String)
    validated = Column(Boolean, default=False)
    validation_result = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class IterationJob(Base):
    """Track Iteration Until Clean jobs."""

    __tablename__ = "iteration_jobs"

    id = Column(String, primary_key=True, index=True)  # job_id
    directory_path = Column(String, index=True)
    target_grade = Column(String, default="A")
    max_iterations = Column(Integer, default=10)
    current_iteration = Column(Integer, default=0)
    start_grade = Column(String, nullable=True)
    current_grade = Column(String, nullable=True)
    final_grade = Column(String, nullable=True)
    status = Column(String, default="processing")  # processing, completed, failed, cancelled
    history = Column(JSON, default=[])  # List of iteration steps
    metrics = Column(JSON, default={})  # Final metrics
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    iteration_history = relationship(
        "IterationHistory", back_populates="job", cascade="all, delete-orphan"
    )


class IterationHistory(Base):
    """Individual iteration steps within a job."""

    __tablename__ = "iteration_history"

    id = Column(String, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("iteration_jobs.id"), index=True)
    iteration_number = Column(Integer)
    grade_before = Column(String)
    grade_after = Column(String)
    issues_found_before = Column(Integer)
    issues_fixed = Column(Integer)
    agent_selected = Column(String)
    fix_description = Column(Text)
    validation_passed = Column(Boolean)
    changes = Column(JSON, default={})  # Detailed changes
    metrics_before = Column(JSON, nullable=True)
    metrics_after = Column(JSON, nullable=True)
    applied_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    job = relationship("IterationJob", back_populates="iteration_history")


# Path I: CAQI Enhanced - Team Analytics

class TeamScore(Base):
    """Aggregated team CAQI scores (Path I enhancement)."""

    __tablename__ = "team_scores"

    id = Column(String(36), primary_key=True, index=True)
    team_id = Column(String(255), unique=True, index=True)
    team_name = Column(String(255))

    # Dimensions (0-100 each)
    security_score = Column(Float, nullable=True)
    complexity_score = Column(Float, nullable=True)
    documentation_score = Column(Float, nullable=True)
    testing_score = Column(Float, nullable=True)
    dependencies_score = Column(Float, nullable=True)
    maintainability_score = Column(Float, nullable=True)

    # Aggregated
    overall_caqi = Column(Integer, nullable=True)  # 0-500
    personality_archetype = Column(String(50), nullable=True)
    member_count = Column(Integer, default=0)

    calculated_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    history = relationship("CAQIHistory", back_populates="team", cascade="all, delete-orphan")
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")


class CAQIHistory(Base):
    """Historical CAQI scores for trend tracking (Path I enhancement)."""

    __tablename__ = "caqi_history"

    id = Column(String(36), primary_key=True, index=True)
    team_id = Column(String(255), ForeignKey("team_scores.team_id"), index=True)

    # Dimensions
    security_score = Column(Float, nullable=True)
    complexity_score = Column(Float, nullable=True)
    documentation_score = Column(Float, nullable=True)
    testing_score = Column(Float, nullable=True)
    dependencies_score = Column(Float, nullable=True)
    maintainability_score = Column(Float, nullable=True)

    overall_caqi = Column(Integer, nullable=True)

    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    team = relationship("TeamScore", back_populates="history")


class TeamMember(Base):
    """Team membership mapping (Path I enhancement)."""

    __tablename__ = "team_members"

    id = Column(String(36), primary_key=True, index=True)
    team_id = Column(String(255), ForeignKey("team_scores.team_id"), index=True)
    developer_id = Column(String(255), index=True)
    added_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    team = relationship("TeamScore", back_populates="members")

    __table_args__ = (
        UniqueConstraint("team_id", "developer_id", name="unique_team_member"),
    )


class GitHubInstallation(Base):
    """GitHub App installation for a user."""

    __tablename__ = "github_installations"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    installation_id = Column(Integer, unique=True, index=True)  # GitHub app installation ID
    token = Column(String)  # Encrypted access token
    token_expires_at = Column(DateTime, nullable=True)
    repositories = relationship("GitHubRepository", back_populates="installation")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")


class GitHubRepository(Base):
    """GitHub repository connected to CodePulse."""

    __tablename__ = "github_repositories"

    id = Column(String, primary_key=True, index=True)
    installation_id = Column(String, ForeignKey("github_installations.id"), index=True)
    repo_name = Column(String, index=True)  # owner/repo
    repo_id = Column(Integer, unique=True, index=True)  # GitHub repo ID
    enabled = Column(Boolean, default=True)
    fail_on_critical = Column(Boolean, default=True)
    fail_on_error = Column(Boolean, default=False)
    pr_scans = relationship("PRScan", back_populates="repository")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    installation = relationship("GitHubInstallation", back_populates="repositories")


class PRScan(Base):
    """GitHub PR scan results."""

    __tablename__ = "pr_scans"

    id = Column(String, primary_key=True, index=True)
    repository_id = Column(String, ForeignKey("github_repositories.id"), index=True)
    pr_number = Column(Integer, index=True)
    branch = Column(String)
    commit_sha = Column(String, index=True)
    findings = Column(JSON, default=[])  # Scan results
    comment_id = Column(String, nullable=True)  # GitHub comment ID
    status = Column(String, default="pending")  # pending, success, failure
    critical_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)

    repository = relationship("GitHubRepository", back_populates="pr_scans")


# Phase 14.5: CI/CD Integration - Dashboard & Reports

class CIScanHistory(Base):
    """Track CI/CD scan execution history."""

    __tablename__ = "ci_scan_history"

    id = Column(String, primary_key=True, index=True)
    repository = Column(String, index=True)  # Repository path or name
    branch = Column(String, default="main", index=True)
    platform = Column(String, index=True)  # github, gitlab, jenkins, circleci, etc.
    event_type = Column(String)  # push, pull_request, schedule, manual
    commit_sha = Column(String, nullable=True, index=True)
    status = Column(String, index=True)  # success, failure, warning

    # Findings summary
    critical_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    info_count = Column(Integer, default=0)
    total_findings = Column(Integer, default=0)

    # File statistics
    files_scanned = Column(Integer, default=0)
    languages = Column(JSON, default={})  # {python: 50, javascript: 30, sql: 5}

    # Report formats
    report_json = Column(JSON, nullable=True)
    report_sarif = Column(JSON, nullable=True)
    report_junit = Column(Text, nullable=True)
    report_sonarqube = Column(JSON, nullable=True)

    # Performance
    duration_ms = Column(Integer, nullable=True)

    # Metadata
    webhook_id = Column(String, nullable=True, index=True)
    scan_job_id = Column(String, nullable=True, index=True)
    triggered_by = Column(String, nullable=True)  # user email or service

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CITrendMetrics(Base):
    """Aggregated CI/CD metrics for trends and analytics."""

    __tablename__ = "ci_trend_metrics"

    id = Column(String, primary_key=True, index=True)
    repository = Column(String, unique=True, index=True)

    # Current metrics
    last_scan_at = Column(DateTime, nullable=True)
    total_scans = Column(Integer, default=0)
    successful_scans = Column(Integer, default=0)
    failed_scans = Column(Integer, default=0)
    pass_rate = Column(Float, default=0.0)  # 0-100

    # Trend data (last 30 days)
    avg_critical_per_scan = Column(Float, default=0.0)
    avg_error_per_scan = Column(Float, default=0.0)
    avg_warning_per_scan = Column(Float, default=0.0)
    avg_scan_duration_ms = Column(Integer, default=0)

    # Historical data
    critical_trend = Column(JSON, default=[])  # List of {date, count}
    error_trend = Column(JSON, default=[])
    warning_trend = Column(JSON, default=[])
    pass_rate_trend = Column(JSON, default=[])

    # Platform breakdown
    platforms = Column(JSON, default={})  # {github: 5, jenkins: 3, gitlab: 2}

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AlertPreference(Base):
    """User alert notification preferences."""

    __tablename__ = "alert_preferences"

    id = Column(String, primary_key=True, index=True)
    repository = Column(String, index=True)  # Repository to alert on (or "all")

    # Thresholds
    alert_on_critical = Column(Boolean, default=True)
    alert_on_error = Column(Boolean, default=False)
    critical_threshold = Column(Integer, default=1)  # Alert if >= N critical issues
    error_threshold = Column(Integer, default=5)     # Alert if >= N errors

    # Channels
    email_enabled = Column(Boolean, default=True)
    email_address = Column(String, nullable=True)
    slack_enabled = Column(Boolean, default=False)
    slack_webhook = Column(String, nullable=True)  # Encrypted webhook URL

    # Frequency
    alert_frequency = Column(String, default='immediate')  # immediate, daily, weekly

    # Status
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
