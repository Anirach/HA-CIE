"""
PDF Report Service for generating accreditation reports.
Uses ReportLab for PDF generation.
"""

from datetime import datetime, date
from typing import Optional, List
from io import BytesIO
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from app.services.standards_service import get_standards_service
from app.services.assessment_service import get_assessment_service
from app.services.insights_service import get_insights_service


class ReportType:
    """Report types available."""
    EXECUTIVE_SUMMARY = "executive_summary"
    FULL_ASSESSMENT = "full_assessment"
    GAP_ANALYSIS = "gap_analysis"
    PROGRESS_REPORT = "progress_report"


class ReportService:
    """Service for generating PDF reports."""
    
    def __init__(self):
        self.standards_service = get_standards_service()
        self.assessment_service = get_assessment_service()
        self.insights_service = get_insights_service()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Set up custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#1e3a5f'),
            alignment=TA_CENTER,
        ))
        self.styles.add(ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=20,
            textColor=colors.grey,
            alignment=TA_CENTER,
        ))
        self.styles.add(ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#1e3a5f'),
        ))
        self.styles.add(ParagraphStyle(
            'SubSectionHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceBefore=10,
            spaceAfter=5,
            textColor=colors.HexColor('#4a5568'),
        ))
        self.styles.add(ParagraphStyle(
            'CustomBodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leading=14,
        ))
        self.styles.add(ParagraphStyle(
            'Metric',
            parent=self.styles['Normal'],
            fontSize=28,
            textColor=colors.HexColor('#667eea'),
            alignment=TA_CENTER,
            spaceAfter=5,
        ))
        self.styles.add(ParagraphStyle(
            'MetricLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=TA_CENTER,
        ))
    
    def get_available_reports(self) -> list:
        """Get list of available report types."""
        return [
            {
                "id": ReportType.EXECUTIVE_SUMMARY,
                "name": "Executive Summary",
                "description": "High-level overview for leadership",
                "pages": "2-3",
            },
            {
                "id": ReportType.FULL_ASSESSMENT,
                "name": "Full Assessment Report",
                "description": "Comprehensive assessment details",
                "pages": "10-15",
            },
            {
                "id": ReportType.GAP_ANALYSIS,
                "name": "Gap Analysis Report",
                "description": "Detailed gap analysis with recommendations",
                "pages": "5-8",
            },
            {
                "id": ReportType.PROGRESS_REPORT,
                "name": "Progress Report",
                "description": "Assessment-over-assessment comparison",
                "pages": "4-6",
            },
        ]
    
    def generate_report(self, hospital_id: str, report_type: str) -> bytes:
        """Generate a PDF report."""
        if report_type == ReportType.EXECUTIVE_SUMMARY:
            return self._generate_executive_summary(hospital_id)
        elif report_type == ReportType.FULL_ASSESSMENT:
            return self._generate_full_assessment(hospital_id)
        elif report_type == ReportType.GAP_ANALYSIS:
            return self._generate_gap_analysis(hospital_id)
        elif report_type == ReportType.PROGRESS_REPORT:
            return self._generate_progress_report(hospital_id)
        else:
            raise ValueError(f"Unknown report type: {report_type}")
    
    def _generate_executive_summary(self, hospital_id: str) -> bytes:
        """Generate executive summary report."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1*inch,
            leftMargin=1*inch,
            topMargin=1*inch,
            bottomMargin=1*inch,
        )
        
        story = []
        
        # Get data
        assessment = self.assessment_service.get_latest_by_hospital(hospital_id)
        insights = self.insights_service.generate_insights(hospital_id)
        
        if not assessment:
            story.append(Paragraph("No assessment data available", self.styles['CustomBodyText']))
            doc.build(story)
            return buffer.getvalue()
        
        # Title
        story.append(Paragraph("Executive Summary", self.styles['CustomTitle']))
        story.append(Paragraph(
            f"Hospital Accreditation Assessment Report",
            self.styles['CustomSubtitle']
        ))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y')}",
            self.styles['CustomSubtitle']
        ))
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
        story.append(Spacer(1, 20))
        
        # Key Metrics Table
        story.append(Paragraph("Key Metrics", self.styles['SectionHeader']))
        
        metrics_data = [
            ['Overall Score', 'Accreditation Level', 'Risk Level'],
            [
                f"{assessment.overall_maturity_score:.1f}/5.0",
                assessment.accreditation_level.value.replace('_', ' ').title(),
                insights['risk_level'].title(),
            ],
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2*inch, 2.5*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, 1), 16),
            ('TEXTCOLOR', (0, 1), (0, 1), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (1, 1), (1, 1), colors.HexColor('#48bb78')),
            ('TEXTCOLOR', (2, 1), (2, 1), self._get_risk_color(insights['risk_level'])),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 1), (-1, 1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f7fafc')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 20))
        
        # Summary Statistics
        story.append(Paragraph("Assessment Summary", self.styles['SectionHeader']))
        
        summary_text = f"""
        This report summarizes the accreditation assessment conducted on 
        {assessment.assessment_date.strftime('%B %d, %Y') if assessment.assessment_date else 'N/A'}. 
        The overall maturity score of {assessment.overall_maturity_score:.2f} indicates 
        {'strong compliance with' if assessment.overall_maturity_score >= 3.5 else 
         'moderate progress toward' if assessment.overall_maturity_score >= 2.5 else 
         'significant gaps in'} HA Thailand Standards requirements.
        """
        story.append(Paragraph(summary_text.strip(), self.styles['CustomBodyText']))
        story.append(Spacer(1, 15))
        
        # Top Recommendations
        story.append(Paragraph("Priority Actions", self.styles['SectionHeader']))
        
        for i, rec in enumerate(insights['recommendations'][:5], 1):
            rec_text = f"<b>{i}. {rec['title']}</b><br/>{rec['description']}"
            story.append(Paragraph(rec_text, self.styles['CustomBodyText']))
            story.append(Spacer(1, 5))
        
        # Build PDF
        doc.build(story)
        return buffer.getvalue()
    
    def _generate_full_assessment(self, hospital_id: str) -> bytes:
        """Generate full assessment report."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=1*inch,
        )
        
        story = []
        
        # Get data
        assessment = self.assessment_service.get_latest_by_hospital(hospital_id)
        if not assessment:
            story.append(Paragraph("No assessment data available", self.styles['CustomBodyText']))
            doc.build(story)
            return buffer.getvalue()
        
        # Title Page
        story.append(Spacer(1, 100))
        story.append(Paragraph("Full Assessment Report", self.styles['CustomTitle']))
        story.append(Paragraph(
            f"Hospital Accreditation Assessment",
            self.styles['CustomSubtitle']
        ))
        story.append(Spacer(1, 30))
        story.append(Paragraph(
            f"Assessment Date: {assessment.assessment_date.strftime('%B %d, %Y') if assessment.assessment_date else 'N/A'}",
            self.styles['CustomSubtitle']
        ))
        story.append(Paragraph(
            f"Report Generated: {datetime.now().strftime('%B %d, %Y')}",
            self.styles['CustomSubtitle']
        ))
        story.append(PageBreak())
        
        # Overview Section
        story.append(Paragraph("1. Assessment Overview", self.styles['SectionHeader']))
        story.append(Paragraph(
            f"Overall Maturity Score: {assessment.overall_maturity_score:.2f}/5.00",
            self.styles['CustomBodyText']
        ))
        story.append(Paragraph(
            f"Accreditation Level: {assessment.accreditation_level.value.replace('_', ' ').title()}",
            self.styles['CustomBodyText']
        ))
        story.append(Spacer(1, 15))
        
        # Domain Scores
        story.append(Paragraph("2. Domain Scores", self.styles['SectionHeader']))
        
        parts = self.standards_service.get_parts()
        domain_data = [['Domain', 'Weight', 'Score', 'Status']]
        
        for part in parts:
            # Calculate average score for this part
            part_scores = [
                cs.score for cs in assessment.criterion_scores
                if cs.criterion_id.startswith(part.number)
            ]
            avg_score = sum(part_scores) / len(part_scores) if part_scores else 0
            status = 'Good' if avg_score >= 3.5 else 'Needs Work' if avg_score >= 2.5 else 'Critical'
            
            domain_data.append([
                f"Part {part.number}: {part.name}",
                f"{part.weight * 100:.0f}%",
                f"{avg_score:.2f}",
                status,
            ])
        
        domain_table = Table(domain_data, colWidths=[3*inch, 0.8*inch, 0.8*inch, 1*inch])
        domain_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
        ]))
        story.append(domain_table)
        story.append(Spacer(1, 20))
        
        # Chapter Details
        story.append(Paragraph("3. Chapter Details", self.styles['SectionHeader']))
        
        for part in parts:
            story.append(Paragraph(
                f"Part {part.number}: {part.name}",
                self.styles['SubSectionHeader']
            ))
            
            chapter_data = [['Chapter', 'Focus', 'Score']]
            for chapter in part.chapters:
                chapter_scores = [
                    cs.score for cs in assessment.criterion_scores
                    if cs.criterion_id.startswith(chapter.id)
                ]
                avg_score = sum(chapter_scores) / len(chapter_scores) if chapter_scores else 0
                
                chapter_data.append([
                    f"{chapter.id}: {chapter.name}",
                    chapter.focus[:50] + '...' if len(chapter.focus) > 50 else chapter.focus,
                    f"{avg_score:.2f}",
                ])
            
            if len(chapter_data) > 1:
                chapter_table = Table(chapter_data, colWidths=[2*inch, 3*inch, 0.8*inch])
                chapter_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
                    ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ]))
                story.append(chapter_table)
                story.append(Spacer(1, 10))
        
        # Build PDF
        doc.build(story)
        return buffer.getvalue()
    
    def _generate_gap_analysis(self, hospital_id: str) -> bytes:
        """Generate gap analysis report."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=1*inch,
        )
        
        story = []
        
        # Get data
        assessment = self.assessment_service.get_latest_by_hospital(hospital_id)
        insights = self.insights_service.generate_insights(hospital_id)
        
        if not assessment:
            story.append(Paragraph("No assessment data available", self.styles['CustomBodyText']))
            doc.build(story)
            return buffer.getvalue()
        
        # Title
        story.append(Paragraph("Gap Analysis Report", self.styles['CustomTitle']))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y')}",
            self.styles['CustomSubtitle']
        ))
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
        story.append(Spacer(1, 20))
        
        # Risk Overview
        story.append(Paragraph("Risk Assessment", self.styles['SectionHeader']))
        story.append(Paragraph(
            f"Overall Risk Score: {insights['risk_score']}/100 ({insights['risk_level'].title()} Risk)",
            self.styles['CustomBodyText']
        ))
        story.append(Spacer(1, 10))
        
        # Critical Gaps
        story.append(Paragraph("Critical Gaps", self.styles['SectionHeader']))
        
        low_scores = [
            cs for cs in assessment.criterion_scores
            if cs.score < 3.0
        ]
        low_scores.sort(key=lambda x: x.score)
        
        if low_scores:
            gaps_data = [['Criterion', 'Score', 'Gap to Target']]
            for cs in low_scores[:15]:
                gaps_data.append([
                    cs.criterion_id,
                    f"{cs.score:.1f}",
                    f"{3.0 - cs.score:.1f}",
                ])
            
            gaps_table = Table(gaps_data, colWidths=[3*inch, 1.2*inch, 1.2*inch])
            gaps_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fc8181')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ]))
            story.append(gaps_table)
        else:
            story.append(Paragraph("No critical gaps identified.", self.styles['CustomBodyText']))
        
        story.append(Spacer(1, 20))
        
        # Insights
        story.append(Paragraph("AI-Generated Insights", self.styles['SectionHeader']))
        
        for insight in insights['insights'][:5]:
            story.append(Paragraph(
                f"<b>{insight['title']}</b>",
                self.styles['SubSectionHeader']
            ))
            story.append(Paragraph(insight['description'], self.styles['CustomBodyText']))
            if insight.get('action_items'):
                for action in insight['action_items'][:2]:
                    story.append(Paragraph(f"• {action}", self.styles['CustomBodyText']))
            story.append(Spacer(1, 10))
        
        # Build PDF
        doc.build(story)
        return buffer.getvalue()
    
    def _generate_progress_report(self, hospital_id: str) -> bytes:
        """Generate progress report comparing assessments."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=1*inch,
        )
        
        story = []
        
        # Get data
        assessments = self.assessment_service.get_by_hospital(hospital_id)
        
        if len(assessments) < 2:
            story.append(Paragraph("Progress Report", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            story.append(Paragraph(
                "At least two assessments are required to generate a progress report.",
                self.styles['CustomBodyText']
            ))
            doc.build(story)
            return buffer.getvalue()
        
        # Title
        story.append(Paragraph("Progress Report", self.styles['CustomTitle']))
        story.append(Paragraph(
            f"Assessment Comparison",
            self.styles['CustomSubtitle']
        ))
        story.append(Spacer(1, 20))
        
        # Score Progression
        story.append(Paragraph("Score Progression", self.styles['SectionHeader']))
        
        progress_data = [['Assessment Date', 'Score', 'Change', 'Level']]
        prev_score = None
        
        for a in assessments:
            change = ""
            if prev_score is not None:
                diff = a.overall_maturity_score - prev_score
                change = f"+{diff:.2f}" if diff >= 0 else f"{diff:.2f}"
            
            progress_data.append([
                a.assessment_date.strftime('%Y-%m-%d') if a.assessment_date else 'N/A',
                f"{a.overall_maturity_score:.2f}",
                change,
                a.accreditation_level.value.replace('_', ' ').title(),
            ])
            prev_score = a.overall_maturity_score
        
        progress_table = Table(progress_data, colWidths=[2*inch, 1.2*inch, 1*inch, 1.5*inch])
        progress_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ]))
        story.append(progress_table)
        story.append(Spacer(1, 20))
        
        # Overall Progress Summary
        first = assessments[0]
        latest = assessments[-1]
        total_change = latest.overall_maturity_score - first.overall_maturity_score
        
        story.append(Paragraph("Summary", self.styles['SectionHeader']))
        story.append(Paragraph(
            f"Total improvement from first to latest assessment: "
            f"{'+'if total_change >= 0 else ''}{total_change:.2f} points",
            self.styles['CustomBodyText']
        ))
        story.append(Paragraph(
            f"Number of assessments: {len(assessments)}",
            self.styles['CustomBodyText']
        ))
        
        # Build PDF
        doc.build(story)
        return buffer.getvalue()
    
    def _get_risk_color(self, risk_level: str) -> colors.Color:
        """Get color for risk level."""
        colors_map = {
            'critical': colors.HexColor('#e53e3e'),
            'high': colors.HexColor('#dd6b20'),
            'medium': colors.HexColor('#d69e2e'),
            'low': colors.HexColor('#38a169'),
        }
        return colors_map.get(risk_level, colors.grey)


# Global instance
_report_service: Optional[ReportService] = None


def get_report_service() -> ReportService:
    """Get or create the report service instance."""
    global _report_service
    if _report_service is None:
        _report_service = ReportService()
    return _report_service

