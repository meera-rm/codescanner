"""Service for sending email and Slack notifications."""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from api.db.models import AlertPreference, CIScanHistory
import requests
import json


class AlertService:
    """Send email and Slack alerts for scan results."""

    # Email configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', 'noreply@codepulse.dev')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')

    @staticmethod
    def check_alert_threshold(
        scan: CIScanHistory,
        preference: AlertPreference,
    ) -> bool:
        """Check if scan triggers alert based on thresholds."""
        if not preference.is_active:
            return False

        if preference.alert_on_critical and scan.critical_count >= preference.critical_threshold:
            return True

        if preference.alert_on_error and scan.error_count >= preference.error_threshold:
            return True

        return False

    @staticmethod
    def send_email_alert(
        email: str,
        scan: CIScanHistory,
    ) -> bool:
        """Send email alert for scan results."""
        if not email or not AlertService.SMTP_PASSWORD:
            return False

        try:
            subject = f"🚨 CodePulse Alert: {scan.repository} - {scan.status.upper()}"

            # Build HTML email
            html_body = f"""
            <html>
              <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <h2 style="color: #d32f2f;">CodePulse Scan Alert</h2>

                <p><strong>Repository:</strong> {scan.repository}</p>
                <p><strong>Branch:</strong> {scan.branch}</p>
                <p><strong>Platform:</strong> {scan.platform}</p>
                <p><strong>Status:</strong> <span style="color: {'#d32f2f' if scan.status == 'failure' else '#4caf50'};">{scan.status.upper()}</span></p>

                <h3>Issues Found:</h3>
                <ul style="font-size: 14px;">
                  <li style="color: #d32f2f;"><strong>Critical:</strong> {scan.critical_count}</li>
                  <li style="color: #f57c00;"><strong>Errors:</strong> {scan.error_count}</li>
                  <li style="color: #fbc02d;"><strong>Warnings:</strong> {scan.warning_count}</li>
                </ul>

                <p><strong>Files Scanned:</strong> {scan.files_scanned}</p>
                <p><strong>Scan Time:</strong> {scan.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>

                <hr>
                <p style="font-size: 12px; color: #666;">
                  View full report: <a href="http://localhost:3000/dashboard">Dashboard</a>
                </p>
              </body>
            </html>
            """

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = AlertService.SMTP_USERNAME
            msg['To'] = email

            msg.attach(MIMEText(html_body, 'html'))

            # Send email
            with smtplib.SMTP(AlertService.SMTP_SERVER, AlertService.SMTP_PORT) as server:
                server.starttls()
                server.login(AlertService.SMTP_USERNAME, AlertService.SMTP_PASSWORD)
                server.sendmail(AlertService.SMTP_USERNAME, email, msg.as_string())

            return True

        except Exception as e:
            print(f"Failed to send email alert: {e}")
            return False

    @staticmethod
    def send_slack_alert(
        webhook_url: str,
        scan: CIScanHistory,
    ) -> bool:
        """Send Slack alert for scan results."""
        if not webhook_url:
            return False

        try:
            # Determine color based on status
            color = '#d32f2f' if scan.critical_count > 0 else ('#f57c00' if scan.error_count > 0 else '#4caf50')
            status_emoji = '🚨' if scan.status == 'failure' else '✅'

            payload = {
                'attachments': [
                    {
                        'color': color,
                        'title': f'{status_emoji} CodePulse Scan Alert',
                        'fields': [
                            {
                                'title': 'Repository',
                                'value': scan.repository,
                                'short': True,
                            },
                            {
                                'title': 'Branch',
                                'value': scan.branch,
                                'short': True,
                            },
                            {
                                'title': 'Platform',
                                'value': scan.platform,
                                'short': True,
                            },
                            {
                                'title': 'Status',
                                'value': scan.status.upper(),
                                'short': True,
                            },
                            {
                                'title': 'Critical Issues',
                                'value': str(scan.critical_count),
                                'short': True,
                            },
                            {
                                'title': 'Errors',
                                'value': str(scan.error_count),
                                'short': True,
                            },
                            {
                                'title': 'Warnings',
                                'value': str(scan.warning_count),
                                'short': True,
                            },
                            {
                                'title': 'Files Scanned',
                                'value': str(scan.files_scanned),
                                'short': True,
                            },
                        ],
                        'footer': 'CodePulse CI/CD Dashboard',
                        'ts': int(datetime.utcnow().timestamp()),
                    }
                ]
            }

            response = requests.post(webhook_url, json=payload, timeout=10)
            return response.status_code == 200

        except Exception as e:
            print(f"Failed to send Slack alert: {e}")
            return False

    @staticmethod
    def process_alerts(
        db: Session,
        scan: CIScanHistory,
    ) -> dict:
        """Process all alerts for a completed scan."""
        results = {
            'email_sent': False,
            'slack_sent': False,
            'error': None,
        }

        try:
            # Get alert preferences for this repository
            preferences = db.query(AlertPreference).filter(
                (AlertPreference.repository == scan.repository) |
                (AlertPreference.repository == 'all')
            ).all()

            for pref in preferences:
                # Check if threshold exceeded
                if not AlertService.check_alert_threshold(scan, pref):
                    continue

                # Send email
                if pref.email_enabled and pref.email_address:
                    if AlertService.send_email_alert(pref.email_address, scan):
                        results['email_sent'] = True

                # Send Slack
                if pref.slack_enabled and pref.slack_webhook:
                    if AlertService.send_slack_alert(pref.slack_webhook, scan):
                        results['slack_sent'] = True

        except Exception as e:
            results['error'] = str(e)
            print(f"Error processing alerts: {e}")

        return results
