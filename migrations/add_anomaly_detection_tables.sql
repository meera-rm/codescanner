-- Migration: Add Anomaly Detection Tables
-- Date: 2026-06-06
-- Purpose: Phase I+1 Advanced Analytics - anomalies, alerts, developer metrics, peer groups, benchmarks

-- 1. Anomalies Table
CREATE TABLE anomalies (
    id VARCHAR(36) PRIMARY KEY,
    team_id VARCHAR(255) NOT NULL,

    dimension VARCHAR(50) NOT NULL,
    previous_score FLOAT NOT NULL,
    current_score FLOAT NOT NULL,
    change_percent FLOAT NOT NULL,
    severity VARCHAR(20),

    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed BOOLEAN DEFAULT FALSE,
    reviewed_by VARCHAR(255),
    reviewed_at TIMESTAMP,
    notes TEXT,

    INDEX idx_anomalies_reviewed_date (team_id, reviewed, detected_at DESC),
    INDEX idx_anomalies_severity (severity),
    FOREIGN KEY (team_id) REFERENCES team_scores(team_id) ON DELETE SET NULL
);

-- 2. Alerts Table
CREATE TABLE alerts (
    id VARCHAR(36) PRIMARY KEY,
    team_id VARCHAR(255) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,

    title VARCHAR(255) NOT NULL,
    description TEXT,
    severity VARCHAR(20),

    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by VARCHAR(255),
    acknowledged_at TIMESTAMP,

    notification_sent_at TIMESTAMP,
    channels TEXT,

    INDEX idx_alerts_acknowledged_date (team_id, acknowledged, triggered_at DESC),
    INDEX idx_alerts_type_severity (alert_type, severity),
    FOREIGN KEY (team_id) REFERENCES team_scores(team_id) ON DELETE SET NULL
);

-- 3. Developer Metrics Table
CREATE TABLE developer_metrics (
    id VARCHAR(36) PRIMARY KEY,
    developer_id VARCHAR(255) NOT NULL,
    team_id VARCHAR(255) NOT NULL,

    security_contribution FLOAT DEFAULT 0,
    complexity_contribution FLOAT DEFAULT 0,
    documentation_contribution FLOAT DEFAULT 0,
    testing_contribution FLOAT DEFAULT 0,
    dependencies_contribution FLOAT DEFAULT 0,
    maintainability_contribution FLOAT DEFAULT 0,

    overall_contribution FLOAT DEFAULT 0,

    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY unique_dev_team_date (developer_id, team_id, calculated_at),
    INDEX idx_developer_metrics_date (team_id, calculated_at DESC),
    FOREIGN KEY (team_id) REFERENCES team_scores(team_id) ON DELETE CASCADE
);

-- 4. Peer Groups Table
CREATE TABLE peer_groups (
    id VARCHAR(36) PRIMARY KEY,
    peer_group_name VARCHAR(255) NOT NULL,
    description TEXT,

    team_ids TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY unique_peer_group_name (peer_group_name),
    INDEX idx_peer_group_created (created_at)
);

-- 5. Benchmarks Table
CREATE TABLE benchmarks (
    id VARCHAR(36) PRIMARY KEY,
    benchmark_type VARCHAR(50) NOT NULL,

    dimension VARCHAR(50) NOT NULL,
    percentile_10 FLOAT,
    percentile_25 FLOAT,
    percentile_50 FLOAT,
    percentile_75 FLOAT,
    percentile_90 FLOAT,

    sample_size INT,
    calculated_at TIMESTAMP,

    UNIQUE KEY unique_benchmark (benchmark_type, dimension),
    INDEX idx_benchmarks_type (benchmark_type)
);

-- Verification: List created tables
-- SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'codepulse';
