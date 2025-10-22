"""
Student Feedback Report Generator
Generates constructive, professional feedback reports for graduate school applicants
with actionable insights and development recommendations.
"""

import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Any
import statistics
import boto3
from botocore.exceptions import ClientError
import logging
import traceback

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle Decimal types from DynamoDB"""
    def default(self, obj):
        try:
            if isinstance(obj, Decimal):
                return float(obj)
            return super().default(obj)
        except Exception as e:
            logger.error(f"Error encoding Decimal object: {e}")
            return str(obj)

def convert_decimals(obj):
    """Recursively convert Decimal objects to float"""
    try:
        if isinstance(obj, list):
            return [convert_decimals(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: convert_decimals(value) for key, value in obj.items()}
        elif isinstance(obj, Decimal):
            return float(obj)
        return obj
    except Exception as e:
        logger.error(f"Error converting decimals: {e}")
        return obj

class StudentFeedbackReportGenerator:
    def __init__(self, student_data: Dict[str, Any], s3_bucket: str = None, s3_prefix: str = "student-reports"):
        """Initialize student feedback report generator
        
        Args:
            student_data: Individual student application evaluation
            s3_bucket: S3 bucket name to save reports to
            s3_prefix: S3 prefix/folder path for reports
        """
        try:
            self.student = convert_decimals(student_data)
            self.generation_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
            self.s3_bucket = s3_bucket
            self.s3_prefix = s3_prefix
            
            # Initialize S3 client if bucket is provided
            self.s3_client = None
            if s3_bucket:
                self.s3_client = boto3.client('s3')
            
            self.colors = {
                'primary': '#2E86AB',
                'secondary': '#A23B72',
                'accent': '#F18F01',
                'success': '#06A77D',
                'danger': '#C73E1D',
                'warning': '#F4A261',
                'info': '#2A9D8F',
                'light': '#F8F9FA'
            }
            
            logger.info(f"Initialized student feedback report for: {self.student.get('student_name', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Error initializing feedback report generator: {e}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to initialize feedback report generator: {str(e)}")
    
    def _get_decision_info(self) -> Dict[str, str]:
        """Get decision information with student-friendly language"""
        decision = self.student.get('level4_Result', {}).get('final_decision', 'PENDING')
        
        decision_map = {
            'ACCEPT': {
                'title': 'Congratulations! Application Accepted',
                'message': 'We are pleased to inform you that your application has been recommended for acceptance to the M.Ag.Sc. program.',
                'color': self.colors['success'],
                'icon': 'fa-check-circle',
                'next_steps': 'You will receive an official admission letter with further instructions regarding enrollment, visa documentation, and orientation.'
            },
            'WAITLIST': {
                'title': 'Application Status: Waitlist',
                'message': 'Your application has been placed on our waitlist. This means you are a competitive candidate, and we may be able to offer you admission as space becomes available.',
                'color': self.colors['warning'],
                'icon': 'fa-clock',
                'next_steps': 'We will notify you of any changes to your application status. In the meantime, you may submit any additional materials that strengthen your application.'
            },
            'REJECT': {
                'title': 'Application Decision',
                'message': 'After careful review, we are unable to offer you admission at this time. We appreciate your interest in our program.',
                'color': self.colors['danger'],
                'icon': 'fa-info-circle',
                'next_steps': 'Please review the feedback provided below to strengthen future applications. You are welcome to reapply in future admission cycles.'
            },
            'CONDITIONAL': {
                'title': 'Conditional Acceptance',
                'message': 'Your application has been conditionally accepted pending fulfillment of specific requirements outlined below.',
                'color': self.colors['info'],
                'icon': 'fa-file-contract',
                'next_steps': 'Please review the conditions carefully and submit required documentation by the specified deadline.'
            }
        }
        
        return decision_map.get(decision, decision_map['WAITLIST'])
    
    def _create_score_overview_chart(self) -> str:
        """Create visual overview of application scores"""
        try:
            level2 = self.student.get('level2_result', {})
            level3 = self.student.get('level3_result', {})
            level4 = self.student.get('level4_Result', {})
            
            categories = ['Academic\nPerformance', 'Research &\nExperience', 'Statement\nof Purpose', 
                         'Letters of\nRecommendation', 'Program\nFit']
            
            scores = [
                level2.get('academic_score', 0),
                level3.get('research_tech_analysis', {}).get('research_tech_score', 0),
                level3.get('sop_analysis', {}).get('sop_score', 0),
                level3.get('lor_analysis', {}).get('weighted_lor_score', 0),
                level4.get('program_fit_score', 0)
            ]
            
            # Create radar chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=scores,
                theta=categories,
                fill='toself',
                name='Your Scores',
                line=dict(color=self.colors['primary'], width=3),
                fillcolor=f"rgba(46, 134, 171, 0.3)"
            ))
            
            # Add reference line at 75 (strong performance)
            fig.add_trace(go.Scatterpolar(
                r=[75]*5,
                theta=categories,
                line=dict(color=self.colors['success'], width=2, dash='dash'),
                name='Strong Performance Threshold',
                showlegend=True
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        tickfont=dict(size=12),
                        gridcolor='lightgray'
                    ),
                    angularaxis=dict(
                        tickfont=dict(size=13, color='#333')
                    )
                ),
                showlegend=True,
                title=dict(
                    text="Application Profile Overview",
                    font=dict(size=18, color=self.colors['primary']),
                    x=0.5,
                    xanchor='center'
                ),
                height=500,
                template='plotly_white'
            )
            
            return fig.to_html(include_plotlyjs=False, div_id="score_overview")
            
        except Exception as e:
            logger.error(f"Error creating score overview chart: {e}")
            return ""
    
    def _create_component_breakdown_chart(self) -> str:
        """Create detailed breakdown of academic components"""
        try:
            level2 = self.student.get('level2_result', {})
            component_scores = level2.get('component_scores', {})
            
            components = ['GPA', 'GRE Scores', 'Coursework<br>Depth']
            scores = [
                component_scores.get('gpa_score', 0),
                component_scores.get('gre_score', 0),
                component_scores.get('coursework_score', 0)
            ]
            
            weights = [50, 30, 20]
            
            fig = go.Figure()
            
            # Create grouped bar chart
            fig.add_trace(go.Bar(
                x=components,
                y=scores,
                name='Your Score',
                marker=dict(
                    color=scores,
                    colorscale=[[0, self.colors['danger']], [0.5, self.colors['warning']], [1, self.colors['success']]],
                    showscale=False,
                    line=dict(color='white', width=2)
                ),
                text=[f"{s:.1f}" for s in scores],
                textposition='outside',
                textfont=dict(size=14, color='#333'),
                hovertemplate='<b>%{x}</b><br>Score: %{y:.1f}/100<extra></extra>'
            ))
            
            # Add reference line
            fig.add_hline(y=75, line_dash="dash", line_color=self.colors['success'], 
                         annotation_text="Strong Performance", annotation_position="right")
            
            # Add weight annotations
            for i, (comp, weight) in enumerate(zip(components, weights)):
                fig.add_annotation(
                    x=i,
                    y=-15,
                    text=f"Weight: {weight}%",
                    showarrow=False,
                    font=dict(size=11, color='#666')
                )
            
            fig.update_layout(
                title=dict(
                    text="Academic Component Analysis",
                    font=dict(size=18, color=self.colors['primary']),
                    x=0.5,
                    xanchor='center'
                ),
                yaxis=dict(
                    title="Score (out of 100)",
                    range=[0, 105],
                    gridcolor='lightgray'
                ),
                xaxis=dict(
                    title="",
                    tickfont=dict(size=13)
                ),
                height=450,
                showlegend=False,
                template='plotly_white',
                margin=dict(b=80)
            )
            
            return fig.to_html(include_plotlyjs=False, div_id="component_breakdown")
            
        except Exception as e:
            logger.error(f"Error creating component breakdown chart: {e}")
            return ""
    
    def _generate_academic_feedback_html(self) -> str:
        """Generate detailed academic performance feedback"""
        level2 = self.student.get('level2_result', {})
        gpa_info = level2.get('gpa_analysis', {})
        gre_info = level2.get('gre_analysis', {})
        coursework = level2.get('coursework_analysis', {})
        
        gpa_converted = gpa_info.get('converted_gpa', 0)
        gpa_meets_min = gpa_converted >= 3.0
        
        return f"""
        <div class="feedback-section">
            <h4 style="color: {self.colors['primary']}; margin-bottom: 20px;">
                <i class="fas fa-graduation-cap"></i> Academic Performance Analysis
            </h4>
            
            <!-- GPA Analysis -->
            <div class="metric-card {'success-border' if gpa_meets_min else 'warning-border'}">
                <div class="metric-header">
                    <i class="fas fa-chart-line"></i> Grade Point Average
                </div>
                <div class="metric-content">
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>Your GPA:</strong> {gpa_info.get('original_gpa', 'N/A')} (Converted: {gpa_converted:.2f}/4.0)</p>
                            <p><strong>Trend:</strong> <span class="badge bg-info">{gpa_info.get('trend', 'N/A')}</span></p>
                            <p><strong>Core Agriculture Courses:</strong> {gpa_info.get('core_agriculture_gpa', 0):.2f}/10.0</p>
                            <p><strong>Specialization Courses:</strong> {gpa_info.get('specialization_gpa', 0):.2f}/10.0</p>
                        </div>
                        <div class="col-md-6">
                            <div class="feedback-box {'success-box' if gpa_meets_min else 'warning-box'}">
                                <p><strong>Assessment:</strong></p>
                                {self._generate_gpa_feedback(gpa_info)}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- GRE Analysis -->
            <div class="metric-card" style="margin-top: 20px;">
                <div class="metric-header">
                    <i class="fas fa-pen-fancy"></i> GRE Performance
                </div>
                <div class="metric-content">
                    <div class="row">
                        <div class="col-md-6">
                            <table class="table table-sm">
                                <tr>
                                    <td><strong>Quantitative:</strong></td>
                                    <td>{gre_info.get('quantitative_score', 0)} ({gre_info.get('quantitative_percentile', 0):.0f}th percentile)</td>
                                </tr>
                                <tr>
                                    <td><strong>Verbal:</strong></td>
                                    <td>{gre_info.get('verbal_score', 0)} ({gre_info.get('verbal_percentile', 0):.0f}th percentile)</td>
                                </tr>
                                <tr>
                                    <td><strong>Analytical Writing:</strong></td>
                                    <td>{gre_info.get('awa_score', 0):.1f}/6.0 ({gre_info.get('awa_percentile', 0):.0f}th percentile)</td>
                                </tr>
                            </table>
                        </div>
                        <div class="col-md-6">
                            <div class="feedback-box info-box">
                                <p><strong>Assessment:</strong></p>
                                {self._generate_gre_feedback(gre_info)}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Coursework Analysis -->
            <div class="metric-card" style="margin-top: 20px;">
                <div class="metric-header">
                    <i class="fas fa-book-open"></i> Coursework Profile
                </div>
                <div class="metric-content">
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>Total Agriculture Courses:</strong> {coursework.get('total_agriculture_courses', 0)}</p>
                            <p><strong>Advanced Level Courses:</strong> {coursework.get('advanced_courses', 0)}</p>
                            <p><strong>Specialization Courses:</strong> {coursework.get('specialization_courses', 0)}</p>
                            <p><strong>Prerequisites Status:</strong> 
                                <span class="badge {'bg-success' if coursework.get('prerequisites_met') else 'bg-danger'}">
                                    {'✓ All Met' if coursework.get('prerequisites_met') else '✗ Some Missing'}
                                </span>
                            </p>
                        </div>
                        <div class="col-md-6">
                            <div class="feedback-box success-box">
                                <p><strong>Strengths:</strong></p>
                                <ul style="margin-bottom: 0;">
                                    {self._generate_coursework_feedback(coursework)}
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_gpa_feedback(self, gpa_info: Dict) -> str:
        """Generate personalized GPA feedback"""
        converted = gpa_info.get('converted_gpa', 0)
        spec_gpa = gpa_info.get('specialization_gpa', 0)
        trend = gpa_info.get('trend', 'STABLE')
        
        feedback = "<ul style='margin-bottom: 0;'>"
        
        if converted >= 3.5:
            feedback += "<li>Excellent academic performance that exceeds program requirements.</li>"
        elif converted >= 3.0:
            feedback += "<li>Solid academic foundation that meets program standards.</li>"
        else:
            feedback += f"<li>Your overall GPA ({converted:.2f}) is slightly below the typical 3.0 threshold.</li>"
            if spec_gpa > 8.0:
                feedback += f"<li>However, your strong performance in specialization courses ({spec_gpa:.1f}/10) demonstrates focused competency.</li>"
        
        if trend == "IMPROVING":
            feedback += "<li>Your upward grade trend shows strong adaptation to academic rigor.</li>"
        elif trend == "STABLE":
            feedback += "<li>Consistent performance throughout your studies shows reliability.</li>"
        
        feedback += "</ul>"
        return feedback
    
    def _generate_gre_feedback(self, gre_info: Dict) -> str:
        """Generate personalized GRE feedback"""
        quant_pct = gre_info.get('quantitative_percentile', 0)
        verbal_pct = gre_info.get('verbal_percentile', 0)
        awa = gre_info.get('awa_score', 0)
        
        feedback = "<ul style='margin-bottom: 0;'>"
        
        if quant_pct >= 70:
            feedback += f"<li>Strong quantitative skills ({quant_pct:.0f}th percentile) excellent for research work.</li>"
        elif quant_pct >= 50:
            feedback += f"<li>Solid quantitative foundation ({quant_pct:.0f}th percentile) suitable for graduate coursework.</li>"
        else:
            feedback += f"<li>Consider strengthening quantitative skills for advanced statistical analysis.</li>"
        
        if verbal_pct >= 70:
            feedback += f"<li>Excellent verbal reasoning skills ({verbal_pct:.0f}th percentile) for academic communication.</li>"
        elif verbal_pct >= 50:
            feedback += f"<li>Good verbal skills ({verbal_pct:.0f}th percentile) for graduate-level reading and discussion.</li>"
        
        if awa >= 4.5:
            feedback += f"<li>Strong analytical writing ability (AWA: {awa:.1f}) important for thesis work.</li>"
        elif awa >= 3.5:
            feedback += f"<li>Adequate writing skills (AWA: {awa:.1f}) for academic papers.</li>"
        
        feedback += "</ul>"
        return feedback
    
    def _generate_coursework_feedback(self, coursework: Dict) -> str:
        """Generate coursework feedback"""
        feedback = ""
        
        advanced = coursework.get('advanced_courses', 0)
        if advanced >= 8:
            feedback += f"<li>Excellent breadth with {advanced} advanced courses.</li>"
        elif advanced >= 5:
            feedback += f"<li>Good exposure with {advanced} advanced courses.</li>"
        
        spec_courses = coursework.get('specialization_courses', 0)
        if spec_courses >= 10:
            feedback += f"<li>Strong specialization focus with {spec_courses} relevant courses.</li>"
        
        grade_quality = coursework.get('grade_quality', '')
        if 'Strong' in grade_quality or 'Excellent' in grade_quality:
            feedback += "<li>Consistently high grades in major courses demonstrate mastery.</li>"
        
        if not feedback:
            feedback = "<li>Solid coursework foundation for graduate studies.</li>"
        
        return feedback
    
    def _generate_holistic_feedback_html(self) -> str:
        """Generate feedback on holistic components"""
        level3 = self.student.get('level3_result', {})
        sop = level3.get('sop_analysis', {})
        lor = level3.get('lor_analysis', {})
        research = level3.get('research_tech_analysis', {})
        
        return f"""
        <div class="feedback-section">
            <h4 style="color: {self.colors['primary']}; margin-bottom: 20px;">
                <i class="fas fa-user-graduate"></i> Holistic Profile Assessment
            </h4>
            
            <!-- Statement of Purpose -->
            <div class="metric-card">
                <div class="metric-header">
                    <i class="fas fa-file-alt"></i> Statement of Purpose
                </div>
                <div class="metric-content">
                    <div class="row">
                        <div class="col-md-4">
                            <div class="score-display">
                                <div class="score-value">{sop.get('sop_score', 0):.0f}</div>
                                <div class="score-label">out of 100</div>
                            </div>
                        </div>
                        <div class="col-md-8">
                            {self._generate_sop_feedback_details(sop)}
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Letters of Recommendation -->
            <div class="metric-card" style="margin-top: 20px;">
                <div class="metric-header">
                    <i class="fas fa-envelope"></i> Letters of Recommendation
                </div>
                <div class="metric-content">
                    <div class="row">
                        <div class="col-md-4">
                            <div class="score-display">
                                <div class="score-value">{lor.get('weighted_lor_score', 0):.0f}</div>
                                <div class="score-label">out of 100</div>
                            </div>
                        </div>
                        <div class="col-md-8">
                            {self._generate_lor_feedback_details(lor)}
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Research & Experience -->
            <div class="metric-card" style="margin-top: 20px;">
                <div class="metric-header">
                    <i class="fas fa-microscope"></i> Research & Practical Experience
                </div>
                <div class="metric-content">
                    <div class="row">
                        <div class="col-md-4">
                            <div class="score-display">
                                <div class="score-value">{research.get('research_tech_score', 0):.0f}</div>
                                <div class="score-label">out of 100</div>
                            </div>
                        </div>
                        <div class="col-md-8">
                            {self._generate_research_feedback_details(research)}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_sop_feedback_details(self, sop: Dict) -> str:
        """Generate detailed SOP feedback"""
        research_align = sop.get('research_alignment_score', 0)
        clarity = sop.get('clarity_of_goals_score', 0)
        personal = sop.get('personal_context_score', 0)
        writing = sop.get('writing_quality_score', 0)
        
        html = "<div class='feedback-details'>"
        
        # Component breakdown
        html += "<p><strong>Component Scores:</strong></p>"
        html += "<ul>"
        html += f"<li>Research Alignment: {research_align}/30 {self._get_score_badge(research_align, 30)}</li>"
        html += f"<li>Clarity of Goals: {clarity}/30 {self._get_score_badge(clarity, 30)}</li>"
        html += f"<li>Personal Context: {personal}/20 {self._get_score_badge(personal, 20)}</li>"
        html += f"<li>Writing Quality: {writing}/20 {self._get_score_badge(writing, 20)}</li>"
        html += "</ul>"
        
        # Key themes
        themes = sop.get('key_themes', [])
        if themes:
            html += "<p style='margin-top: 15px;'><strong>Your Key Themes:</strong></p>"
            html += "<div class='theme-tags'>"
            for theme in themes[:5]:
                html += f"<span class='theme-tag'>{theme}</span>"
            html += "</div>"
        
        # Feedback
        html += "<div class='feedback-box info-box' style='margin-top: 15px;'>"
        html += "<p><strong>Feedback:</strong></p>"
        html += self._generate_sop_specific_feedback(sop)
        html += "</div>"
        
        html += "</div>"
        return html
    
    def _generate_sop_specific_feedback(self, sop: Dict) -> str:
        """Generate specific SOP feedback"""
        research_align = sop.get('research_alignment_score', 0)
        clarity = sop.get('clarity_of_goals_score', 0)
        
        feedback = "<ul style='margin-bottom: 0;'>"
        
        if research_align >= 20:
            feedback += "<li>Your research interests align well with the program offerings.</li>"
        elif research_align >= 15:
            feedback += "<li>Good connection between your interests and program focus.</li>"
        else:
            feedback += "<li>Consider researching specific faculty members and their work to strengthen program fit.</li>"
        
        if clarity >= 20:
            feedback += "<li>Your career goals are clearly articulated and realistic.</li>"
        elif clarity >= 15:
            feedback += "<li>Your goals are outlined; more specificity would strengthen your statement.</li>"
        else:
            feedback += "<li>Work on defining more concrete short-term and long-term career objectives.</li>"
        
        feedback += "</ul>"
        return feedback
    
    def _generate_lor_feedback_details(self, lor: Dict) -> str:
        """Generate detailed LOR feedback"""
        lor_count = lor.get('lor_count', 0)
        consistency = lor.get('consistency', 'MEDIUM')
        strengths = lor.get('key_strengths_mentioned', [])
        
        html = "<div class='feedback-details'>"
        
        html += f"<p><strong>Number of Recommendations:</strong> {lor_count}</p>"
        html += f"<p><strong>Consistency:</strong> <span class='badge bg-{'success' if consistency == 'HIGH' else 'warning'}'>{consistency}</span></p>"
        
        if strengths:
            html += "<p style='margin-top: 15px;'><strong>Key Strengths Highlighted:</strong></p>"
            html += "<ul>"
            for strength in strengths[:6]:
                html += f"<li><i class='fas fa-check' style='color: {self.colors['success']};'></i> {strength}</li>"
            html += "</ul>"
        
        html += "<div class='feedback-box success-box' style='margin-top: 15px;'>"
        html += "<p><strong>Assessment:</strong></p>"
        html += self._generate_lor_specific_feedback(lor)
        html += "</div>"
        
        html += "</div>"
        return html
    
    def _generate_lor_specific_feedback(self, lor: Dict) -> str:
        """Generate specific LOR feedback"""
        consistency = lor.get('consistency', 'MEDIUM')
        lor_count = lor.get('lor_count', 0)
        
        feedback = "<ul style='margin-bottom: 0;'>"
        
        if lor_count >= 3:
            feedback += "<li>You submitted the recommended number of letters.</li>"
        
        if consistency == 'HIGH':
            feedback += "<li>Your recommenders consistently highlight complementary strengths.</li>"
        elif consistency == 'MEDIUM':
            feedback += "<li>Your recommenders provided good insights from different perspectives.</li>"
        
        feedback += "<li>Strong letters from credible recommenders strengthen your application significantly.</li>"
        feedback += "</ul>"
        
        return feedback
    
    def _generate_research_feedback_details(self, research: Dict) -> str:
        """Generate detailed research feedback"""
        projects = research.get('research_project_count', 0)
        duration = research.get('research_duration_months', 0)
        publications = research.get('publications', 0)
        internship = research.get('internship_months', 0)
        skills = research.get('lab_skills', [])
        
        html = "<div class='feedback-details'>"
        
        html += "<div class='row'>"
        html += "<div class='col-md-6'>"
        html += f"<p><strong>Research Projects:</strong> {projects}</p>"
        html += f"<p><strong>Research Duration:</strong> {duration} months</p>"
        html += f"<p><strong>Publications:</strong> {publications}</p>"
        html += "</div>"
        html += "<div class='col-md-6'>"
        html += f"<p><strong>Internship Experience:</strong> {internship} months</p>"
        html += f"<p><strong>Fieldwork:</strong> {research.get('fieldwork_experience', 'N/A')}</p>"
        html += "</div>"
        html += "</div>"
        
        if skills:
            html += "<p style='margin-top: 15px;'><strong>Technical Skills:</strong></p>"
            html += "<div class='skill-tags'>"
            for skill in skills:
                html += f"<span class='skill-tag'>{skill}</span>"
            html += "</div>"
        
        html += "<div class='feedback-box info-box' style='margin-top: 15px;'>"
        html += "<p><strong>Assessment:</strong></p>"
        html += self._generate_research_specific_feedback(research)
        html += "</div>"
        
        html += "</div>"
        return html
    
    def _generate_research_specific_feedback(self, research: Dict) -> str:
        """Generate specific research feedback"""
        projects = research.get('research_project_count', 0)
        duration = research.get('research_duration_months', 0)
        publications = research.get('publications', 0)
        
        feedback = "<ul style='margin-bottom: 0;'>"
        
        if publications > 0:
            feedback += f"<li>Excellent research output with {publications} publication(s).</li>"
        elif duration >= 6:
            feedback += f"<li>Substantial research experience ({duration} months) demonstrates commitment.</li>"
        elif projects >= 1:
            feedback += "<li>Good research foundation; consider seeking publication opportunities.</li>"
        else:
            feedback += "<li>Consider gaining more hands-on research experience before graduate studies.</li>"
        
        if research.get('fieldwork_experience') in ['EXCELLENT', 'GOOD']:
            feedback += "<li>Strong practical field experience enhances your research profile.</li>"
        
        feedback += "</ul>"
        
        return feedback
    
    def _get_score_badge(self, score: float, max_score: float) -> str:
        """Get color-coded badge for score"""
        percentage = (score / max_score) * 100 if max_score > 0 else 0
        
        if percentage >= 75:
            return f"<span class='badge bg-success'>Strong</span>"
        elif percentage >= 60:
            return f"<span class='badge bg-info'>Good</span>"
        elif percentage >= 50:
            return f"<span class='badge bg-warning'>Fair</span>"
        else:
            return f"<span class='badge bg-secondary'>Needs Work</span>"
    
    def _generate_strengths_weaknesses_html(self) -> str:
        """Generate strengths and areas for improvement"""
        level4 = self.student.get('level4_Result', {})
        strengths = level4.get('strengths', [])
        weaknesses = level4.get('weaknesses', [])
        
        return f"""
        <div class="feedback-section">
            <h4 style="color: {self.colors['primary']}; margin-bottom: 20px;">
                <i class="fas fa-balance-scale"></i> Application Profile Summary
            </h4>
            
            <div class="row">
                <div class="col-lg-6">
                    <div class="metric-card success-border">
                        <div class="metric-header" style="background: {self.colors['success']};">
                            <i class="fas fa-star"></i> Key Strengths
                        </div>
                        <div class="metric-content">
                            <ul class="strength-list">
                                {self._format_list_items(strengths, 'strength')}
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-6">
                    <div class="metric-card warning-border">
                        <div class="metric-header" style="background: {self.colors['info']};">
                            <i class="fas fa-lightbulb"></i> Areas for Development
                        </div>
                        <div class="metric-content">
                            <ul class="development-list">
                                {self._format_list_items(weaknesses, 'development')}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _format_list_items(self, items: List[str], item_type: str) -> str:
        """Format list items with icons"""
        if not items:
            return "<li>No specific items identified.</li>"
        
        icon = 'fa-check-circle' if item_type == 'strength' else 'fa-arrow-circle-up'
        color = self.colors['success'] if item_type == 'strength' else self.colors['info']
        
        html = ""
        for item in items:
            html += f"<li><i class='fas {icon}' style='color: {color}; margin-right: 8px;'></i> {item}</li>"
        
        return html
    
    def _generate_recommendations_html(self) -> str:
        """Generate actionable recommendations"""
        level4 = self.student.get('level4_Result', {})
        decision = level4.get('final_decision', 'PENDING')
        
        recommendations = []
        
        # Based on weaknesses
        weaknesses = level4.get('weaknesses', [])
        
        if any('GPA' in w for w in weaknesses):
            recommendations.append({
                'title': 'Strengthen Academic Record',
                'icon': 'fa-book',
                'points': [
                    'Consider taking additional coursework in your area of interest',
                    'If reapplying, focus on earning strong grades in advanced courses',
                    'Highlight your specialization GPA in future applications'
                ]
            })
        
        if any('research' in w.lower() or 'publication' in w.lower() for w in weaknesses):
            recommendations.append({
                'title': 'Enhance Research Profile',
                'icon': 'fa-microscope',
                'points': [
                    'Seek research assistant positions in your field',
                    'Consider presenting at conferences or submitting to journals',
                    'Develop relationships with faculty for research mentorship',
                    'Document all research projects and outcomes systematically'
                ]
            })
        
        if decision in ['WAITLIST', 'REJECT']:
            recommendations.append({
                'title': 'Strengthen Future Applications',
                'icon': 'fa-clipboard-check',
                'points': [
                    'Gain more practical experience through internships or work',
                    'Take GRE again if scores are below 60th percentile',
                    'Develop stronger connections with potential recommenders',
                    'Refine your statement of purpose with specific research interests'
                ]
            })
        
        if decision == 'ACCEPT' or decision == 'CONDITIONAL':
            recommendations.append({
                'title': 'Prepare for Graduate Studies',
                'icon': 'fa-graduation-cap',
                'points': [
                    'Review foundational concepts in your specialization area',
                    'Familiarize yourself with key faculty research at OSU',
                    'Begin planning your research interests and potential thesis topics',
                    'Connect with current graduate students in the program'
                ]
            })
        
        # Always include professional development
        recommendations.append({
            'title': 'Professional Development',
            'icon': 'fa-user-tie',
            'points': [
                'Join professional organizations in agricultural sciences',
                'Attend webinars and workshops in your field',
                'Build your professional network through LinkedIn',
                'Stay updated on current research trends and innovations'
            ]
        })
        
        html = f"""
        <div class="feedback-section">
            <h4 style="color: {self.colors['primary']}; margin-bottom: 20px;">
                <i class="fas fa-route"></i> Recommendations for Success
            </h4>
            
            <div class="row">
        """
        
        for i, rec in enumerate(recommendations):
            html += f"""
                <div class="col-lg-6" style="margin-bottom: 20px;">
                    <div class="recommendation-card">
                        <h5 style="color: {self.colors['accent']};">
                            <i class="fas {rec['icon']}"></i> {rec['title']}
                        </h5>
                        <ul>
            """
            for point in rec['points']:
                html += f"<li>{point}</li>"
            html += """
                        </ul>
                    </div>
                </div>
            """
        
        html += """
            </div>
        </div>
        """
        
        return html
    
    def _generate_next_steps_html(self) -> str:
        """Generate next steps based on decision"""
        decision_info = self._get_decision_info()
        level4 = self.student.get('level4_Result', {})
        decision = level4.get('final_decision', 'PENDING')
        
        html = f"""
        <div class="feedback-section">
            <h4 style="color: {self.colors['primary']}; margin-bottom: 20px;">
                <i class="fas fa-directions"></i> Next Steps
            </h4>
            
            <div class="next-steps-card">
                <p style="font-size: 1.1em; margin-bottom: 20px;">{decision_info['next_steps']}</p>
        """
        
        if decision == 'ACCEPT':
            html += """
                <div class="alert alert-success">
                    <h5><i class="fas fa-tasks"></i> Action Items:</h5>
                    <ol>
                        <li>Review and accept your admission offer by the specified deadline</li>
                        <li>Complete enrollment paperwork and submit required documents</li>
                        <li>Apply for F-1 student visa at your nearest U.S. embassy/consulate</li>
                        <li>Arrange housing and plan your arrival to campus</li>
                        <li>Register for orientation and initial coursework</li>
                    </ol>
                </div>
            """
        elif decision == 'WAITLIST':
            html += """
                <div class="alert alert-info">
                    <h5><i class="fas fa-tasks"></i> While on Waitlist:</h5>
                    <ol>
                        <li>Monitor your email regularly for updates on your status</li>
                        <li>Submit any additional materials that might strengthen your application</li>
                        <li>Consider applying to other programs as backup options</li>
                        <li>Update the admissions office of any new achievements or awards</li>
                    </ol>
                </div>
            """
        elif decision == 'CONDITIONAL':
            html += """
                <div class="alert alert-warning">
                    <h5><i class="fas fa-tasks"></i> Conditions to Fulfill:</h5>
                    <ol>
                        <li>Review all conditions specified in your admission letter</li>
                        <li>Submit required documentation by the deadline</li>
                        <li>Maintain communication with the admissions office</li>
                        <li>Complete any prerequisite coursework if required</li>
                    </ol>
                </div>
            """
        else:  # REJECT
            html += """
                <div class="alert alert-secondary">
                    <h5><i class="fas fa-tasks"></i> Moving Forward:</h5>
                    <ol>
                        <li>Review the feedback provided carefully</li>
                        <li>Work on addressing identified areas for improvement</li>
                        <li>Gain additional experience or strengthen weak areas</li>
                        <li>Consider reapplying in a future admission cycle</li>
                        <li>Explore other graduate programs that match your profile</li>
                    </ol>
                </div>
            """
        
        html += """
                <div class="contact-info" style="margin-top: 30px;">
                    <h5><i class="fas fa-envelope"></i> Questions?</h5>
                    <p>If you have questions about your application or this feedback, please contact:</p>
                    <p>
                        <strong>Graduate Admissions Office</strong><br>
                        University<br>
                        Email: gradadmissions@higherdummy.edu<br>
                        Phone: (XXX) XXX-XXXX
                    </p>
                </div>
            </div>
        </div>
        """
        
        return html
    
    def _upload_to_s3(self, html_content: str, s3_key: str) -> Dict[str, Any]:
        """Upload HTML content to S3"""
        try:
            if not self.s3_client or not self.s3_bucket:
                return {
                    'success': False,
                    'error': 'S3 bucket not configured',
                    'message': 'No S3 bucket specified. Report generated but not uploaded.'
                }
            
            if not html_content:
                return {
                    'success': False,
                    'error': 'No content to upload',
                    'message': 'HTML content is empty'
                }
            
            logger.info(f"Uploading student report to s3://{self.s3_bucket}/{s3_key}")
            
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=html_content.encode('utf-8'),
                ContentType='text/html',
                CacheControl='max-age=3600'
            )
            
            s3_url = f"https://{self.s3_bucket}.s3.amazonaws.com/{s3_key}"
            
            logger.info(f"Successfully uploaded student report to S3: {s3_url}")
            
            return {
                'success': True,
                'bucket': self.s3_bucket,
                'key': s3_key,
                'url': s3_url,
                'message': 'Report successfully uploaded to S3'
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"S3 upload failed: {error_code} - {error_message}")
            return {
                'success': False,
                'error': error_code,
                'message': error_message,
                'bucket': self.s3_bucket,
                'key': s3_key
            }
        except Exception as e:
            logger.error(f"Unexpected error during S3 upload: {e}")
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(type(e).__name__),
                'message': str(e),
                'bucket': self.s3_bucket,
                'key': s3_key
            }
    
    def generate_html_report(self, s3_key: str = None) -> Dict[str, Any]:
        """Generate student feedback report and save to S3
        
        Args:
            s3_key: S3 object key for the report. If None, will be auto-generated.
        
        Returns:
            Dictionary with generation and upload status
        """
        
        student_name = self.student.get('student_name', 'N/A')
        app_id = self.student.get('application_id', 'N/A')
        specialization = self.student.get('specialization', 'N/A')
        
        decision_info = self._get_decision_info()
        
        # Generate charts
        logger.info("Generating student feedback charts...")
        score_overview = self._create_score_overview_chart()
        component_breakdown = self._create_component_breakdown_chart()
        
        # Generate feedback sections
        academic_feedback = self._generate_academic_feedback_html()
        holistic_feedback = self._generate_holistic_feedback_html()
        strengths_weaknesses = self._generate_strengths_weaknesses_html()
        recommendations = self._generate_recommendations_html()
        next_steps = self._generate_next_steps_html()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Application Feedback - {student_name}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        :root {{
            --primary: #2E86AB;
            --secondary: #A23B72;
            --accent: #F18F01;
            --success: #06A77D;
            --danger: #C73E1D;
            --warning: #F4A261;
            --info: #2A9D8F;
            --light: #F8F9FA;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #333;
            line-height: 1.6;
        }}
        
        .navbar {{
            background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%) !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            padding: 1rem 0;
        }}
        
        .navbar-brand {{
            font-weight: 700;
            font-size: 1.3em;
        }}
        
        .container-main {{
            max-width: 1400px;
            margin: 30px auto;
            padding: 0 20px;
        }}
        
        .decision-banner {{
            background: linear-gradient(135deg, {decision_info['color']} 0%, {decision_info['color']}dd 100%);
            color: white;
            padding: 50px 40px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }}
        
        .decision-icon {{
            font-size: 4em;
            margin-bottom: 20px;
        }}
        
        .decision-title {{
            font-size: 2.2em;
            font-weight: 700;
            margin-bottom: 15px;
        }}
        
        .decision-message {{
            font-size: 1.2em;
            margin-bottom: 0;
        }}
        
        .header-info {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }}
        
        .feedback-section {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }}
        
        .metric-card {{
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 20px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        }}
        
        .metric-card.success-border {{
            border-left: 5px solid var(--success);
        }}
        
        .metric-card.warning-border {{
            border-left: 5px solid var(--info);
        }}
        
        .metric-header {{
            background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 15px 20px;
            font-weight: 600;
            font-size: 1.1em;
        }}
        
        .metric-content {{
            padding: 20px;
        }}
        
        .score-display {{
            text-align: center;
            padding: 20px;
        }}
        
        .score-value {{
            font-size: 3em;
            font-weight: 700;
            color: var(--primary);
        }}
        
        .score-label {{
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .feedback-box {{
            padding: 15px;
            border-radius: 8px;
            margin-top: 10px;
        }}
        
        .info-box {{
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-left: 4px solid var(--info);
        }}
        
        .success-box {{
            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
            border-left: 4px solid var(--success);
        }}
        
        .warning-box {{
            background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
            border-left: 4px solid var(--warning);
        }}
        
        .feedback-details ul {{
            margin-bottom: 10px;
        }}
        
        .feedback-details li {{
            margin-bottom: 8px;
        }}
        
        .theme-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
        
        .theme-tag {{
            display: inline-block;
            background: var(--info);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
        
        .skill-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
        
        .skill-tag {{
            display: inline-block;
            background: var(--accent);
            color: white;
            padding: 5px 12px;
            border-radius: 5px;
            font-size: 0.85em;
        }}
        
        .strength-list li, .development-list li {{
            margin-bottom: 15px;
            padding-left: 10px;
        }}
        
        .recommendation-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid var(--accent);
            height: 100%;
        }}
        
        .recommendation-card h5 {{
            margin-bottom: 15px;
        }}
        
        .recommendation-card ul {{
            margin-bottom: 0;
        }}
        
        .recommendation-card li {{
            margin-bottom: 10px;
        }}
        
        .next-steps-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            border: 2px solid var(--primary);
        }}
        
        .contact-info {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid var(--primary);
        }}
        
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 25px;
        }}
        
        .alert {{
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }}
        
        .footer {{
            background: white;
            padding: 30px;
            text-align: center;
            color: #666;
            margin-top: 60px;
            border-top: 2px solid #e9ecef;
            border-radius: 10px;
        }}
        
        @media (max-width: 768px) {{
            .container-main {{
                padding: 0 15px;
            }}
            
            .decision-banner {{
                padding: 30px 20px;
            }}
            
            .decision-title {{
                font-size: 1.6em;
            }}
            
            .decision-message {{
                font-size: 1em;
            }}
            
            .score-value {{
                font-size: 2.2em;
            }}
        }}
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-dark sticky-top">
        <div class="container-fluid">
            <span class="navbar-brand">
                <i class="fas fa-graduation-cap"></i> M.Ag.Sc. Graduate Admissions
            </span>
            <span class="navbar-text text-white">
                Application Feedback Report
            </span>
        </div>
    </nav>
    
    <div class="container-main">
        <!-- Header Info -->
        <div class="header-info">
            <h1 style="color: var(--primary); margin-bottom: 15px;">
                <i class="fas fa-user"></i> {student_name}
            </h1>
            <div class="row">
                <div class="col-md-4">
                    <p class="mb-2">
                        <i class="fas fa-id-card"></i> <strong>Application ID:</strong> {app_id}
                    </p>
                </div>
                <div class="col-md-4">
                    <p class="mb-2">
                        <i class="fas fa-flask"></i> <strong>Specialization:</strong> {specialization}
                    </p>
                </div>
                <div class="col-md-4">
                    <p class="mb-2">
                        <i class="fas fa-calendar"></i> <strong>Report Date:</strong> {self.generation_time}
                    </p>
                </div>
            </div>
        </div>
        
        <!-- Decision Banner -->
        <div class="decision-banner">
            <div class="decision-icon">
                <i class="fas {decision_info['icon']}"></i>
            </div>
            <div class="decision-title">{decision_info['title']}</div>
            <p class="decision-message">{decision_info['message']}</p>
        </div>
        
        <!-- Score Overview -->
        <div class="feedback-section">
            <h4 style="color: var(--primary); margin-bottom: 20px;">
                <i class="fas fa-chart-radar"></i> Your Application at a Glance
            </h4>
            <div class="chart-container">
                {score_overview}
            </div>
            <div class="info-box">
                <p style="margin-bottom: 0;">
                    <i class="fas fa-info-circle"></i> <strong>Understanding Your Profile:</strong>
                    This radar chart visualizes your performance across five key evaluation areas. 
                    Scores closer to the outer edge indicate stronger performance. The dashed line represents 
                    the threshold for strong performance in each area.
                </p>
            </div>
        </div>
        
        <!-- Component Breakdown -->
        <div class="feedback-section">
            <h4 style="color: var(--primary); margin-bottom: 20px;">
                <i class="fas fa-tasks"></i> Academic Component Breakdown
            </h4>
            <div class="chart-container">
                {component_breakdown}
            </div>
        </div>
        
        <!-- Academic Feedback -->
        {academic_feedback}
        
        <!-- Holistic Feedback -->
        {holistic_feedback}
        
        <!-- Strengths & Weaknesses -->
        {strengths_weaknesses}
        
        <!-- Recommendations -->
        {recommendations}
        
        <!-- Next Steps -->
        {next_steps}
        
        <!-- Footer -->
        <div class="footer">
            <p style="margin-bottom: 10px;">
                <i class="fas fa-file-alt"></i> This feedback report was generated to help you understand your application evaluation.
            </p>
            <p style="margin-bottom: 10px;">
                We appreciate your interest in our University's M.Ag.Sc. program.
            </p>
            <p style="margin-bottom: 0; font-size: 0.9em;">
                For questions or clarifications, please contact our Graduate Admissions Office.
            </p>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""
        
        # Generate S3 key if not provided
        if not s3_key:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = student_name.replace(' ', '_').replace('/', '_')
            s3_key = f"{self.s3_prefix}/{app_id}_{safe_name}_feedback_{timestamp}.html"
        
        logger.info(f"Uploading student feedback report to S3: s3://{self.s3_bucket}/{s3_key}")
        upload_result = self._upload_to_s3(html_content, s3_key)
        
        return {
            'generation': {
                'success': True,
                'student_name': student_name,
                'application_id': app_id,
                'report_type': 'student_feedback',
                'report_generated': True,
                'html_length': len(html_content)
            },
            'upload': upload_result
        }
