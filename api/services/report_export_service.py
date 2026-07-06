"""Service for exporting scan reports in multiple formats."""
import csv
import io
from datetime import datetime
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from sqlalchemy.orm import Session
from api.db.models import CIScanHistory


class ReportExportService:
    """Generate reports in PDF and CSV formats."""

    @staticmethod
    def generate_csv_report(
        db: Session,
        repository: str = None,
        platform: str = None,
        days: int = 30,
    ) -> io.StringIO:
        """Generate CSV report of scan history."""
        # Build query
        query = db.query(CIScanHistory)

        if repository:
            query = query.filter(CIScanHistory.repository == repository)
        if platform:
            query = query.filter(CIScanHistory.platform == platform)

        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = query.filter(CIScanHistory.created_at >= cutoff)

        scans = query.order_by(CIScanHistory.created_at.desc()).all()

        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            'Repository',
            'Branch',
            'Platform',
            'Event Type',
            'Status',
            'Critical',
            'Error',
            'Warning',
            'Info',
            'Total Findings',
            'Files Scanned',
            'Duration (ms)',
            'Timestamp',
        ])

        # Data rows
        for scan in scans:
            writer.writerow([
                scan.repository,
                scan.branch,
                scan.platform,
                scan.event_type,
                scan.status,
                scan.critical_count,
                scan.error_count,
                scan.warning_count,
                scan.info_count,
                scan.total_findings,
                scan.files_scanned,
                scan.duration_ms or 0,
                scan.created_at.isoformat(),
            ])

        return output

    @staticmethod
    def generate_pdf_report(
        db: Session,
        repository: str = None,
        platform: str = None,
        days: int = 30,
        include_trends: bool = True,
    ) -> bytes:
        """Generate PDF report of scan history with charts and trends."""
        # Get data
        query = db.query(CIScanHistory)

        if repository:
            query = query.filter(CIScanHistory.repository == repository)
        if platform:
            query = query.filter(CIScanHistory.platform == platform)

        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = query.filter(CIScanHistory.created_at >= cutoff)

        scans = query.order_by(CIScanHistory.created_at.desc()).all()

        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=1,  # Center
        )
        elements.append(Paragraph('CodePulse Scan Report', title_style))
        elements.append(Spacer(1, 0.3 * inch))

        # Summary
        if scans:
            summary_data = ReportExportService._calculate_summary(scans)
            elements.append(Paragraph('Summary', styles['Heading2']))

            summary_table = Table([
                ['Metric', 'Value'],
                ['Total Scans', str(summary_data['total_scans'])],
                ['Successful', str(summary_data['successful'])],
                ['Failed', str(summary_data['failed'])],
                ['Pass Rate', f"{summary_data['pass_rate']:.1f}%"],
                ['Total Critical', str(summary_data['critical'])],
                ['Total Errors', str(summary_data['errors'])],
                ['Total Warnings', str(summary_data['warnings'])],
            ])

            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            elements.append(summary_table)
            elements.append(Spacer(1, 0.3 * inch))

        # Repository Breakdown (if reporting on specific repo)
        if scans:
            elements.append(PageBreak())
            elements.append(Paragraph('Repository & Platform Analysis', styles['Heading2']))

            # By Repository
            repo_data = ReportExportService._aggregate_by_repository(scans)
            if repo_data:
                elements.append(Paragraph('By Repository', styles['Heading3']))
                repo_table_data = [['Repository', 'Scans', 'Pass Rate', 'Avg Critical', 'Avg Errors']]
                for repo, stats in repo_data.items():
                    repo_table_data.append([
                        repo[:25],
                        str(stats['count']),
                        f"{stats['pass_rate']:.1f}%",
                        f"{stats['avg_critical']:.1f}",
                        f"{stats['avg_errors']:.1f}",
                    ])

                repo_table = Table(repo_table_data)
                repo_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ]))
                elements.append(repo_table)
                elements.append(Spacer(1, 0.2 * inch))

            # By Platform
            platform_data = ReportExportService._aggregate_by_platform(scans)
            if platform_data:
                elements.append(Paragraph('By Platform', styles['Heading3']))
                plat_table_data = [['Platform', 'Scans', 'Pass Rate', 'Total Issues']]
                for plat, stats in platform_data.items():
                    plat_table_data.append([
                        plat.capitalize(),
                        str(stats['count']),
                        f"{stats['pass_rate']:.1f}%",
                        str(stats['total_issues']),
                    ])

                plat_table = Table(plat_table_data)
                plat_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c62828')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ]))
                elements.append(plat_table)

        # Scan Details Table
        if scans:
            elements.append(PageBreak())
            elements.append(Paragraph('Detailed Scan Results', styles['Heading2']))

            scan_data = [['Repository', 'Platform', 'Status', 'Critical', 'Errors', 'Warnings', 'Date']]

            for scan in scans[:50]:  # Last 50 scans
                scan_data.append([
                    scan.repository[:20],  # Truncate long names
                    scan.platform,
                    scan.status.upper()[:3],  # SUC/FAI
                    str(scan.critical_count),
                    str(scan.error_count),
                    str(scan.warning_count),
                    scan.created_at.strftime('%Y-%m-%d'),
                ])

            scan_table = Table(scan_data)
            scan_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))

            elements.append(scan_table)

        # Footer
        elements.append(Spacer(1, 0.3 * inch))
        footer_text = f"Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        elements.append(Paragraph(footer_text, ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=1,
        )))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def _calculate_summary(scans: List[CIScanHistory]) -> Dict[str, Any]:
        """Calculate summary statistics from scans."""
        if not scans:
            return {
                'total_scans': 0,
                'successful': 0,
                'failed': 0,
                'pass_rate': 0.0,
                'critical': 0,
                'errors': 0,
                'warnings': 0,
            }

        successful = len([s for s in scans if s.status == 'success'])
        failed = len([s for s in scans if s.status == 'failure'])

        return {
            'total_scans': len(scans),
            'successful': successful,
            'failed': failed,
            'pass_rate': (successful / len(scans) * 100) if scans else 0,
            'critical': sum(s.critical_count for s in scans),
            'errors': sum(s.error_count for s in scans),
            'warnings': sum(s.warning_count for s in scans),
        }

    @staticmethod
    def _aggregate_by_repository(scans: List[CIScanHistory]) -> Dict[str, Dict[str, Any]]:
        """Aggregate statistics by repository."""
        repos = {}
        for scan in scans:
            if scan.repository not in repos:
                repos[scan.repository] = {
                    'count': 0,
                    'successful': 0,
                    'critical': 0,
                    'errors': 0,
                }
            repos[scan.repository]['count'] += 1
            if scan.status == 'success':
                repos[scan.repository]['successful'] += 1
            repos[scan.repository]['critical'] += scan.critical_count
            repos[scan.repository]['errors'] += scan.error_count

        # Calculate averages
        for repo in repos:
            count = repos[repo]['count']
            repos[repo]['pass_rate'] = (repos[repo]['successful'] / count * 100) if count > 0 else 0
            repos[repo]['avg_critical'] = repos[repo]['critical'] / count if count > 0 else 0
            repos[repo]['avg_errors'] = repos[repo]['errors'] / count if count > 0 else 0

        return repos

    @staticmethod
    def _aggregate_by_platform(scans: List[CIScanHistory]) -> Dict[str, Dict[str, Any]]:
        """Aggregate statistics by platform."""
        platforms = {}
        for scan in scans:
            if scan.platform not in platforms:
                platforms[scan.platform] = {
                    'count': 0,
                    'successful': 0,
                    'critical': 0,
                    'errors': 0,
                    'warnings': 0,
                }
            platforms[scan.platform]['count'] += 1
            if scan.status == 'success':
                platforms[scan.platform]['successful'] += 1
            platforms[scan.platform]['critical'] += scan.critical_count
            platforms[scan.platform]['errors'] += scan.error_count
            platforms[scan.platform]['warnings'] += scan.warning_count

        # Calculate statistics
        for plat in platforms:
            count = platforms[plat]['count']
            platforms[plat]['pass_rate'] = (platforms[plat]['successful'] / count * 100) if count > 0 else 0
            platforms[plat]['total_issues'] = (
                platforms[plat]['critical'] +
                platforms[plat]['errors'] +
                platforms[plat]['warnings']
            )

        return platforms
