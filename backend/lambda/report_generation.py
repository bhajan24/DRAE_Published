
"""
Professional Admissions Report Generator
Generates comprehensive HTML reports for university application evaluations
with statistical analysis, visualizations, and detailed breakdowns.
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
from scipy import stats
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

class StatisticalCalculator:
    """Handles all statistical calculations"""
    
    @staticmethod
    def calculate_percentile(value: float, all_values: List[float]) -> float:
        """Calculate percentile rank"""
        if not all_values or value is None or len(all_values) < 2:
            return None
        
        try:
            valid_values = [v for v in all_values if v is not None and not pd.isna(v)]
            if len(valid_values) < 2:
                return None
            
            percentile = stats.percentileofscore(valid_values, value, kind='strict')
            return max(0, min(100, percentile))
        except Exception as e:
            print(f"Error calculating percentile: {e}")
            return None
    
    @staticmethod
    def calculate_z_score(value: float, all_values: List[float]) -> float:
        """Calculate Z-score"""
        if not all_values or len(all_values) < 2:
            return None
        
        try:
            valid_values = [v for v in all_values if v is not None and not pd.isna(v)]
            if len(valid_values) < 2:
                return None
            
            mean = statistics.mean(valid_values)
            stdev = statistics.stdev(valid_values)
            
            if stdev == 0:
                return 0
            
            return (value - mean) / stdev
        except Exception as e:
            print(f"Error calculating z-score: {e}")
            return None
    
    @staticmethod
    def get_distribution_stats(values: List[float]) -> Dict[str, float]:
        """Get comprehensive distribution statistics"""
        valid_values = [v for v in values if v is not None and not pd.isna(v)]
        
        if len(valid_values) < 1:
            return {}
        
        return {
            'mean': statistics.mean(valid_values),
            'median': statistics.median(valid_values),
            'stdev': statistics.stdev(valid_values) if len(valid_values) > 1 else 0,
            'min': min(valid_values),
            'max': max(valid_values),
            'q1': float(np.percentile(valid_values, 25)),
            'q3': float(np.percentile(valid_values, 75)),
            'count': len(valid_values)
        }

class ProfessionalAdmissionsReportGenerator:
    def __init__(self, student_data: Dict[str, Any], all_applicants: List[Dict[str, Any]], 
                 s3_bucket: str = None, s3_prefix: str = "admissions-reports"):
        """Initialize report generator
        
        Args:
            student_data: Individual student application report
            all_applicants: List of all student application reports
            s3_bucket: S3 bucket name to save reports to
            s3_prefix: S3 prefix/folder path for reports
        """
        try:
            self.student = convert_decimals(student_data)
            self.all_applicants = [convert_decimals(applicant) for applicant in all_applicants]
            self.generation_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
            self.stats_calc = StatisticalCalculator()
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
            
            logger.info(f"Initialized report generator for student: {self.student.get('student_name', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Error initializing report generator: {e}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to initialize report generator: {str(e)}")
        
    def _extract_all_scores(self) -> Dict[str, List[float]]:
        """Extract all score types from applicants"""
        scores = {
            'composite': [],
            'academic': [],
            'holistic': [],
            'program_fit': [],
            'potential': [],
            'gpa': [],
            'core_ag_gpa': [],
            'spec_gpa': [],
            'gre_quant': [],
            'gre_verbal': [],
            'gre_composite': [],
            'gre_awa': [],
            'toefl': [],
            'ielts': [],
            'sop': [],
            'lor': [],
            'research': []
        }
        
        for applicant in self.all_applicants:
            try:
                if 'level4_Result' in applicant:
                    l4 = applicant['level4_Result']
                    if 'composite_score' in l4:
                        scores['composite'].append(l4['composite_score'])
                    if 'program_fit_score' in l4:
                        scores['program_fit'].append(l4['program_fit_score'])
                    if 'potential_score' in l4:
                        scores['potential'].append(l4['potential_score'])
                
                if 'level2_result' in applicant:
                    l2 = applicant['level2_result']
                    if 'academic_score' in l2:
                        scores['academic'].append(l2['academic_score'])
                    
                    gpa = l2.get('gpa_analysis', {}).get('converted_gpa')
                    if gpa:
                        scores['gpa'].append(gpa)
                    
                    core_gpa = l2.get('gpa_analysis', {}).get('core_agriculture_gpa')
                    if core_gpa:
                        scores['core_ag_gpa'].append(core_gpa)
                    
                    spec_gpa = l2.get('gpa_analysis', {}).get('specialization_gpa')
                    if spec_gpa:
                        scores['spec_gpa'].append(spec_gpa)
                    
                    gre = l2.get('gre_analysis', {})
                    if 'quantitative_percentile' in gre:
                        scores['gre_quant'].append(gre['quantitative_percentile'])
                    if 'verbal_percentile' in gre:
                        scores['gre_verbal'].append(gre['verbal_percentile'])
                    if 'composite_percentile' in gre:
                        scores['gre_composite'].append(gre['composite_percentile'])
                    if 'awa_score' in gre:
                        scores['gre_awa'].append(gre['awa_score'])
                
                if 'level3_result' in applicant:
                    l3 = applicant['level3_result']
                    if 'holistic_score' in l3:
                        scores['holistic'].append(l3['holistic_score'])
                    
                    comp = l3.get('component_scores', {})
                    if 'sop_score' in comp:
                        scores['sop'].append(comp['sop_score'])
                    if 'lor_score' in comp:
                        scores['lor'].append(comp['lor_score'])
                    if 'research_tech_score' in comp:
                        scores['research'].append(comp['research_tech_score'])
                
                if 'level1_result' in applicant:
                    eng = applicant['level1_result'].get('english_analysis', {})
                    if eng.get('test_type') == 'TOEFL' and 'score' in eng:
                        scores['toefl'].append(eng['score'])
                    elif eng.get('test_type') == 'IELTS' and 'score' in eng:
                        scores['ielts'].append(eng['score'])
                        
            except Exception as e:
                continue
        
        return scores
    
    def _create_multi_metric_comparison(self) -> str:
        """Create multi-metric bar chart comparison"""
        try:
            data_points = []
            student_name = self.student.get('student_name', 'This Applicant')
            
            for i, applicant in enumerate(self.all_applicants):
                try:
                    name = applicant.get('student_name', f'Applicant {i}')
                    is_student = (name == student_name)
                    
                    data_points.append({
                        'name': name,
                        'Academic': applicant.get('level2_result', {}).get('academic_score', 0),
                        'Holistic': applicant.get('level3_result', {}).get('holistic_score', 0),
                        'Program Fit': applicant.get('level4_Result', {}).get('program_fit_score', 0),
                        'Composite': applicant.get('level4_Result', {}).get('composite_score', 0),
                        'is_student': is_student,
                        'decision': applicant.get('level4_Result', {}).get('final_decision', 'N/A')
                    })
                except:
                    continue
            
            if not data_points:
                return ""
            
            df = pd.DataFrame(data_points).sort_values('Composite', ascending=True).reset_index(drop=True)
            
            # Calculate averages
            avg_academic = df['Academic'].mean()
            avg_holistic = df['Holistic'].mean()
            avg_program_fit = df['Program Fit'].mean()
            avg_composite = df['Composite'].mean()
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=("Academic Score", "Holistic Score", "Program Fit", "Composite Score"),
                specs=[[{'type': 'bar'}, {'type': 'bar'}],
                      [{'type': 'bar'}, {'type': 'bar'}]]
            )
            
            for idx, row in df.iterrows():
                is_student = row['is_student']
                color = self.colors['success'] if is_student else self.colors['secondary']
                name = row['name']
                
                # Academic
                fig.add_trace(
                    go.Bar(
                        y=[name], x=[row['Academic']], orientation='h',
                        marker=dict(color=color), showlegend=False,
                        text=[f"{row['Academic']:.1f}"], textposition='auto',
                        hovertemplate=f"<b>{name}</b><br>Academic: {{x:.1f}}<extra></extra>"
                    ),
                    row=1, col=1
                )
                
                # Holistic
                fig.add_trace(
                    go.Bar(
                        y=[name], x=[row['Holistic']], orientation='h',
                        marker=dict(color=color), showlegend=False,
                        text=[f"{row['Holistic']:.1f}"], textposition='auto',
                        hovertemplate=f"<b>{name}</b><br>Holistic: {{x:.1f}}<extra></extra>"
                    ),
                    row=1, col=2
                )
                
                # Program Fit
                fig.add_trace(
                    go.Bar(
                        y=[name], x=[row['Program Fit']], orientation='h',
                        marker=dict(color=color), showlegend=False,
                        text=[f"{row['Program Fit']:.1f}"], textposition='auto',
                        hovertemplate=f"<b>{name}</b><br>Program Fit: {{x:.1f}}<extra></extra>"
                    ),
                    row=2, col=1
                )
                
                # Composite
                fig.add_trace(
                    go.Bar(
                        y=[name], x=[row['Composite']], orientation='h',
                        marker=dict(color=color), showlegend=False,
                        text=[f"{row['Composite']:.1f}"], textposition='auto',
                        hovertemplate=f"<b>{name}</b><br>Composite: {{x:.1f}}<extra></extra>"
                    ),
                    row=2, col=2
                )
            
            # Add average lines
            fig.add_vline(x=avg_academic, line_dash="dash", line_color=self.colors['accent'], row=1, col=1)
            fig.add_vline(x=avg_holistic, line_dash="dash", line_color=self.colors['accent'], row=1, col=2)
            fig.add_vline(x=avg_program_fit, line_dash="dash", line_color=self.colors['accent'], row=2, col=1)
            fig.add_vline(x=avg_composite, line_dash="dash", line_color=self.colors['accent'], row=2, col=2)
            
            fig.update_xaxes(title_text="Score", row=1, col=1)
            fig.update_xaxes(title_text="Score", row=1, col=2)
            fig.update_xaxes(title_text="Score", row=2, col=1)
            fig.update_xaxes(title_text="Score", row=2, col=2)
            
            fig.update_layout(
                title_text="Multi-Metric Applicant Comparison (Sorted by Composite Score)",
                height=900,
                width=1200,
                showlegend=False,
                template='plotly_white'
            )
            
            return fig.to_html(include_plotlyjs=False, div_id="multi_metric")
        except Exception as e:
            print(f"Error: {e}")
            return ""
    
    def _create_score_distribution_analysis(self) -> str:
        """Create statistical distribution analysis with box plots"""
        try:
            all_scores = self._extract_all_scores()
            student_name = self.student.get('student_name', 'This Applicant')
            
            # Get this student's scores
            student_composite = self.student.get('level4_Result', {}).get('composite_score', 0)
            student_academic = self.student.get('level2_result', {}).get('academic_score', 0)
            student_holistic = self.student.get('level3_result', {}).get('holistic_score', 0)
            student_gpa = self.student.get('level2_result', {}).get('gpa_analysis', {}).get('converted_gpa', 0)
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=("Composite Score Distribution", "Academic Score Distribution", 
                               "Holistic Score Distribution", "GPA Distribution"),
                specs=[[{'type': 'box'}, {'type': 'box'}],
                      [{'type': 'box'}, {'type': 'box'}]]
            )
            
            # Composite
            fig.add_trace(
                go.Box(y=all_scores['composite'], name='Cohort', marker_color=self.colors['secondary'], showlegend=False),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(y=[student_composite], x=['This Applicant'], mode='markers', 
                          marker=dict(size=15, color=self.colors['success'], symbol='star'),
                          name='This Applicant', showlegend=False,
                          hovertemplate=f"<b>{student_name}</b><br>Composite: {student_composite:.1f}<extra></extra>"),
                row=1, col=1
            )
            
            # Academic
            fig.add_trace(
                go.Box(y=all_scores['academic'], name='Cohort', marker_color=self.colors['secondary'], showlegend=False),
                row=1, col=2
            )
            fig.add_trace(
                go.Scatter(y=[student_academic], x=['This Applicant'], mode='markers',
                          marker=dict(size=15, color=self.colors['success'], symbol='star'),
                          name='This Applicant', showlegend=False,
                          hovertemplate=f"<b>{student_name}</b><br>Academic: {student_academic:.1f}<extra></extra>"),
                row=1, col=2
            )
            
            # Holistic
            fig.add_trace(
                go.Box(y=all_scores['holistic'], name='Cohort', marker_color=self.colors['secondary'], showlegend=False),
                row=2, col=1
            )
            fig.add_trace(
                go.Scatter(y=[student_holistic], x=['This Applicant'], mode='markers',
                          marker=dict(size=15, color=self.colors['success'], symbol='star'),
                          name='This Applicant', showlegend=False,
                          hovertemplate=f"<b>{student_name}</b><br>Holistic: {student_holistic:.1f}<extra></extra>"),
                row=2, col=1
            )
            
            # GPA
            if all_scores['gpa']:
                fig.add_trace(
                    go.Box(y=all_scores['gpa'], name='Cohort', marker_color=self.colors['secondary'], showlegend=False),
                    row=2, col=2
                )
                fig.add_trace(
                    go.Scatter(y=[student_gpa], x=['This Applicant'], mode='markers',
                              marker=dict(size=15, color=self.colors['success'], symbol='star'),
                              name='This Applicant', showlegend=False,
                              hovertemplate=f"<b>{student_name}</b><br>GPA: {student_gpa:.2f}<extra></extra>"),
                    row=2, col=2
                )
            
            fig.update_yaxes(title_text="Score", row=1, col=1)
            fig.update_yaxes(title_text="Score", row=1, col=2)
            fig.update_yaxes(title_text="Score", row=2, col=1)
            fig.update_yaxes(title_text="GPA (4.0)", row=2, col=2)
            
            fig.update_layout(
                title_text="Score Distribution Analysis with Cohort (Stars indicate this applicant's scores)",
                height=900,
                width=1200,
                showlegend=False,
                template='plotly_white'
            )
            
            return fig.to_html(include_plotlyjs=False, div_id="distribution_analysis")
        except Exception as e:
            print(f"Error: {e}")
            return ""
    
    def _create_score_breakdown_details(self) -> str:
        """Create detailed score breakdown with drill-down"""
        level2 = self.student.get('level2_result', {})
        level3 = self.student.get('level3_result', {})
        level4 = self.student.get('level4_Result', {})
        
        academic_score = level2.get('academic_score', 0)
        holistic_score = level3.get('holistic_score', 0)
        composite_score = level4.get('composite_score', 0)
        
        gpa_score = level2.get('component_scores', {}).get('gpa_score', 0)
        gre_score = level2.get('component_scores', {}).get('gre_score', 0)
        coursework_score = level2.get('component_scores', {}).get('coursework_score', 0)
        
        sop_score = level3.get('component_scores', {}).get('sop_score', 0)
        lor_score = level3.get('component_scores', {}).get('lor_score', 0)
        research_score = level3.get('component_scores', {}).get('research_tech_score', 0)
        
        components = level4.get('component_breakdown', {})
        
        html = f"""
        <div style="padding: 20px;">
            <h5 style="color: {self.colors['primary']}; margin-bottom: 20px;">
                <i class="fas fa-sitemap"></i> Score Composition & Justification
            </h5>
            
            <div class="accordion" id="scoreAccordion">
                <!-- Composite Score -->
                <div class="accordion-item">
                    <h2 class="accordion-header">
                        <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#composite">
                            <strong style="font-size: 1.1em;">Composite Score: {composite_score:.1f}/100</strong>
                        </button>
                    </h2>
                    <div id="composite" class="accordion-collapse collapse show" data-bs-parent="#scoreAccordion">
                        <div class="accordion-body" style="background: #f8f9fa;">
                            <p><strong>Weighted Composition:</strong></p>
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Component</th>
                                        <th>Score</th>
                                        <th>Weight</th>
                                        <th>Contribution</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>Academic Performance</td>
                                        <td>{academic_score:.1f}</td>
                                        <td>40%</td>
                                        <td>{components.get('academic', 0):.1f} points</td>
                                    </tr>
                                    <tr>
                                        <td>Holistic Review</td>
                                        <td>{holistic_score:.1f}</td>
                                        <td>35%</td>
                                        <td>{components.get('holistic', 0):.1f} points</td>
                                    </tr>
                                    <tr>
                                        <td>Program Fit</td>
                                        <td>{level4.get('program_fit_score', 0):.1f}</td>
                                        <td>15%</td>
                                        <td>{components.get('program_fit', 0):.1f} points</td>
                                    </tr>
                                    <tr>
                                        <td>Growth Potential</td>
                                        <td>{level4.get('potential_score', 0):.1f}</td>
                                        <td>10%</td>
                                        <td>{components.get('potential', 0):.1f} points</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                
                <!-- Academic Score -->
                <div class="accordion-item">
                    <h2 class="accordion-header">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#academic">
                            <strong>Academic Score: {academic_score:.1f}/100</strong> (40% of Composite)
                        </button>
                    </h2>
                    <div id="academic" class="accordion-collapse collapse" data-bs-parent="#scoreAccordion">
                        <div class="accordion-body" style="background: #f8f9fa;">
                            {self._generate_academic_breakdown_html(level2)}
                        </div>
                    </div>
                </div>
                
                <!-- Holistic Score -->
                <div class="accordion-item">
                    <h2 class="accordion-header">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#holistic">
                            <strong>Holistic Review: {holistic_score:.1f}/100</strong> (35% of Composite)
                        </button>
                    </h2>
                    <div id="holistic" class="accordion-collapse collapse" data-bs-parent="#scoreAccordion">
                        <div class="accordion-body" style="background: #f8f9fa;">
                            {self._generate_holistic_breakdown_html(level3)}
                        </div>
                    </div>
                </div>
                
                <!-- Program Fit -->
                <div class="accordion-item">
                    <h2 class="accordion-header">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#programfit">
                            <strong>Program Fit: {level4.get('program_fit_score', 0):.1f}/100</strong> (15% of Composite)
                        </button>
                    </h2>
                    <div id="programfit" class="accordion-collapse collapse" data-bs-parent="#scoreAccordion">
                        <div class="accordion-body" style="background: #f8f9fa;">
                            <p><strong>Specialization Alignment:</strong> {self.student.get('specialization', 'N/A')}</p>
                            <p style="margin-top: 10px;"><strong>Justification:</strong></p>
                            <ul>
                                {self._generate_program_fit_justification()}
                            </ul>
                        </div>
                    </div>
                </div>
                
                <!-- Potential Score -->
                <div class="accordion-item">
                    <h2 class="accordion-header">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#potential">
                            <strong>Growth Potential: {level4.get('potential_score', 0):.1f}/100</strong> (10% of Composite)
                        </button>
                    </h2>
                    <div id="potential" class="accordion-collapse collapse" data-bs-parent="#scoreAccordion">
                        <div class="accordion-body" style="background: #f8f9fa;">
                            <p><strong>Potential Assessment Factors:</strong></p>
                            <ul>
                                <li>Academic Trajectory: {level2.get('gpa_analysis', {}).get('trend', 'N/A')}</li>
                                <li>Research Capability: Based on experience and coursework depth</li>
                                <li>Career Readiness: Evaluated through LORs and SOP</li>
                                <li>Leadership Indicators: From recommendations and practical experience</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        
        return html
    
    def _generate_academic_breakdown_html(self, level2: Dict) -> str:
        """Generate detailed academic breakdown"""
        gpa_score = level2.get('component_scores', {}).get('gpa_score', 0)
        gre_score = level2.get('component_scores', {}).get('gre_score', 0)
        coursework_score = level2.get('component_scores', {}).get('coursework_score', 0)
        
        gpa_info = level2.get('gpa_analysis', {})
        gre_info = level2.get('gre_analysis', {})
        coursework = level2.get('coursework_analysis', {})
        
        return f"""
        <p><strong>Component Breakdown (50% GPA, 30% GRE, 20% Coursework):</strong></p>
        <table class="table table-sm mb-3">
            <thead>
                <tr>
                    <th>Component</th>
                    <th>Score</th>
                    <th>Weight</th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>GPA Analysis</strong></td>
                    <td>{gpa_score:.1f}</td>
                    <td>50%</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" data-bs-toggle="collapse" data-bs-target="#gpaDetails">
                            View Details
                        </button>
                    </td>
                </tr>
                <tr>
                    <td><strong>GRE Performance</strong></td>
                    <td>{gre_score:.1f}</td>
                    <td>30%</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" data-bs-toggle="collapse" data-bs-target="#greDetails">
                            View Details
                        </button>
                    </td>
                </tr>
                <tr>
                    <td><strong>Coursework Depth</strong></td>
                    <td>{coursework_score:.1f}</td>
                    <td>20%</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" data-bs-toggle="collapse" data-bs-target="#courseDetails">
                            View Details
                        </button>
                    </td>
                </tr>
            </tbody>
        </table>
        
        <!-- GPA Details Collapse -->
        <div class="collapse mb-3" id="gpaDetails">
            <div class="card card-body" style="background: #e8f4f8;">
                <p><strong>GPA Metrics:</strong></p>
                <ul style="margin-bottom: 10px;">
                    <li>Original GPA: {gpa_info.get('original_gpa', 'N/A')}</li>
                    <li>Converted GPA (4.0): {gpa_info.get('converted_gpa', 0):.2f}</li>
                    <li>Core Agriculture GPA: {gpa_info.get('core_agriculture_gpa', 0):.2f}</li>
                    <li>Specialization GPA: {gpa_info.get('specialization_gpa', 0):.2f}</li>
                    <li>Trend: <span class="badge bg-success">{gpa_info.get('trend', 'N/A')}</span></li>
                </ul>
                <p style="margin-bottom: 0; font-size: 0.9em; color: #666;"><strong>Note:</strong> Strong performance in core courses indicates deep subject matter knowledge. Improving trend shows adaptation to graduate-level rigor.</p>
            </div>
        </div>
        
        <!-- GRE Details Collapse -->
        <div class="collapse mb-3" id="greDetails">
            <div class="card card-body" style="background: #e8f4f8;">
                <p><strong>GRE Score Analysis:</strong></p>
                <ul style="margin-bottom: 10px;">
                    <li>Quantitative: {gre_info.get('quantitative_score', 0)} ({gre_info.get('quantitative_percentile', 0):.0f}th percentile)</li>
                    <li>Verbal: {gre_info.get('verbal_score', 0)} ({gre_info.get('verbal_percentile', 0):.0f}th percentile)</li>
                    <li>Analytical Writing: {gre_info.get('awa_score', 0):.1f}/6.0</li>
                    <li>Composite Percentile: {gre_info.get('composite_percentile', 0):.0f}th</li>
                </ul>
                <p style="margin-bottom: 0; font-size: 0.9em; color: #666;"><strong>Note:</strong> Quantitative strength is valuable for agricultural sciences research. Solid verbal and writing skills important for graduate-level communication.</p>
            </div>
        </div>
        
        <!-- Coursework Details Collapse -->
        <div class="collapse mb-3" id="courseDetails">
            <div class="card card-body" style="background: #e8f4f8;">
                <p><strong>Coursework Profile:</strong></p>
                <ul style="margin-bottom: 10px;">
                    <li>Total Agriculture Courses: {coursework.get('total_agriculture_courses', 0)}</li>
                    <li>Advanced Courses: {coursework.get('advanced_courses', 0)}</li>
                    <li>Specialization Courses: {coursework.get('specialization_courses', 0)}</li>
                    <li>Grade Quality: {coursework.get('grade_quality', 'N/A')}</li>
                    <li>Prerequisites: {'✓ Met' if coursework.get('prerequisites_met') else '✗ Not Met'}</li>
                </ul>
                <p style="margin-bottom: 0; font-size: 0.9em; color: #666;"><strong>Note:</strong> Comprehensive coursework demonstrates broad agricultural knowledge with specialization focus. High grades in major courses predict graduate success.</p>
            </div>
        </div>
        """
    
    def _generate_holistic_breakdown_html(self, level3: Dict) -> str:
        """Generate detailed holistic breakdown"""
        sop_score = level3.get('component_scores', {}).get('sop_score', 0)
        lor_score = level3.get('component_scores', {}).get('lor_score', 0)
        research_score = level3.get('component_scores', {}).get('research_tech_score', 0)
        
        sop = level3.get('sop_analysis', {})
        lor = level3.get('lor_analysis', {})
        research = level3.get('research_tech_analysis', {})
        
        return f"""
        <p><strong>Component Breakdown (30% SOP, 40% LORs, 30% Research/Practical):</strong></p>
        <table class="table table-sm mb-3">
            <thead>
                <tr>
                    <th>Component</th>
                    <th>Score</th>
                    <th>Weight</th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Statement of Purpose</strong></td>
                    <td>{sop_score:.1f}</td>
                    <td>30%</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" data-bs-toggle="collapse" data-bs-target="#sopDetails">
                            View Details
                        </button>
                    </td>
                </tr>
                <tr>
                    <td><strong>Letters of Recommendation</strong></td>
                    <td>{lor_score:.1f}</td>
                    <td>40%</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" data-bs-toggle="collapse" data-bs-target="#lorDetails">
                            View Details
                        </button>
                    </td>
                </tr>
                <tr>
                    <td><strong>Research & Practical Experience</strong></td>
                    <td>{research_score:.1f}</td>
                    <td>30%</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" data-bs-toggle="collapse" data-bs-target="#researchDetails">
                            View Details
                        </button>
                    </td>
                </tr>
            </tbody>
        </table>
        
        <!-- SOP Details -->
        <div class="collapse mb-3" id="sopDetails">
            <div class="card card-body" style="background: #e8f4f8;">
                <p><strong>SOP Analysis:</strong></p>
                <ul style="margin-bottom: 10px;">
                    <li>Research Alignment: {sop.get('research_alignment_score', 0)}/30</li>
                    <li>Clarity of Goals: {sop.get('clarity_of_goals_score', 0)}/30</li>
                    <li>Personal Context: {sop.get('personal_context_score', 0)}/20</li>
                    <li>Writing Quality: {sop.get('writing_quality_score', 0)}/20</li>
                    <li>Agricultural Relevance: <span class="badge bg-info">{sop.get('agricultural_relevance', 'N/A')}</span></li>
                </ul>
                <p><strong>Key Themes:</strong></p>
                <p>{', '.join(sop.get('key_themes', []))}</p>
                <p style="margin-bottom: 0; font-size: 0.9em; color: #666;"><strong>Note:</strong> SOP demonstrates understanding of program, realistic career planning, and fit with program offerings.</p>
            </div>
        </div>
        
        <!-- LOR Details -->
        <div class="collapse mb-3" id="lorDetails">
            <div class="card card-body" style="background: #e8f4f8;">
                <p><strong>Letters of Recommendation Analysis:</strong></p>
                <ul style="margin-bottom: 15px;">
                    <li>Number of Letters: {lor.get('lor_count', 0)}</li>
                    <li>Weighted Score: {lor.get('weighted_lor_score', 0):.0f}/100</li>
                    <li>Consistency Across Recommendations: <span class="badge bg-success">{lor.get('consistency', 'N/A')}</span></li>
                </ul>
                
                {self._generate_lor_details(lor)}
                
                <p style="margin-top: 10px; margin-bottom: 0; font-size: 0.9em; color: #666;"><strong>Note:</strong> Consistent positive themes across recommenders strengthen application. Credible recommenders (faculty, supervisors) carry more weight.</p>
            </div>
        </div>
        
        <!-- Research Details -->
        <div class="collapse mb-3" id="researchDetails">
            <div class="card card-body" style="background: #e8f4f8;">
                <p><strong>Research & Practical Experience:</strong></p>
                <ul style="margin-bottom: 10px;">
                    <li>Research Projects: {research.get('research_project_count', 0)}</li>
                    <li>Research Duration: {research.get('research_duration_months', 0)} months</li>
                    <li>Internship Experience: {research.get('internship_months', 0)} months</li>
                    <li>Publications: {research.get('publications', 0)}</li>
                    <li>Fieldwork Quality: <span class="badge bg-warning">{research.get('fieldwork_experience', 'N/A')}</span></li>
                </ul>
                
                {self._generate_research_details(research)}
                
                <p style="margin-bottom: 0; font-size: 0.9em; color: #666;"><strong>Note:</strong> Hands-on experience crucial for agricultural sciences. Demonstrates capability to apply theory to real-world scenarios.</p>
            </div>
        </div>
        """
    
    def _generate_lor_details(self, lor: Dict) -> str:
        """Generate LOR details with key strengths mentioned"""
        html = "<p><strong>Individual Recommendations:</strong></p>"
        
        # Check if we have any LOR data
        lor_count = lor.get('lor_count', 0)
        weighted_score = lor.get('weighted_lor_score', 0)
        
        html += f"""
        <div style="background: #f8f9fa; padding: 12px; border-radius: 5px; margin-bottom: 15px;">
            <p style="margin-bottom: 5px;"><strong>Summary:</strong> {lor_count} recommendation(s) received with weighted score of {weighted_score:.0f}/100</p>
        </div>
        """
        
        # Add key strengths mentioned across recommendations
        key_strengths = lor.get('key_strengths_mentioned', [])
        if key_strengths:
            html += "<p><strong>Key Strengths Highlighted by Recommenders:</strong></p>"
            html += "<ul style='margin-bottom: 15px;'>"
            for strength in key_strengths:
                html += f"<li><span class='badge bg-info'>{strength}</span></li>"
            html += "</ul>"
        
        # Add any red flags if present
        red_flags = lor.get('red_flags', [])
        if red_flags:
            html += "<p><strong>Concerns Noted:</strong></p>"
            html += "<ul style='margin-bottom: 15px; color: #C73E1D;'>"
            for flag in red_flags:
                html += f"<li>{flag}</li>"
            html += "</ul>"
        else:
            html += "<p style='font-size: 0.9em; color: #666; margin-bottom: 15px;'><i class='fas fa-check' style='color: #06A77D; margin-right: 5px;'></i> No significant concerns noted across recommendations.</p>"
        
        return html
    
    def _generate_research_details(self, research: Dict) -> str:
        """Generate research details"""
        skills = research.get('lab_skills', [])
        html = ""
        if skills:
            html = f"<p><strong>Technical Skills:</strong> {', '.join(skills)}</p>"
        return html
    
    def _generate_program_fit_justification(self) -> str:
        """Generate program fit justification"""
        specialization = self.student.get('specialization', '')
        sop_themes = self.student.get('level3_result', {}).get('sop_analysis', {}).get('key_themes', [])
        
        html = ""
        html += f"<li>Selected Specialization: <strong>{specialization}</strong></li>"
        html += "<li>Clear alignment between research interests and program offerings</li>"
        if sop_themes:
            html += f"<li>Key research interests align: {', '.join(sop_themes[:3])}</li>"
        html += "<li>Demonstrated commitment through relevant coursework and experience</li>"
        
        return html
    
    def _create_eligibility_checklist(self) -> str:
        """Create detailed eligibility checklist"""
        level1 = self.student.get('level1_result', {})
        checklist = level1.get('checklist', {})
        prerequisites = level1.get('prerequisite_analysis', [])
        gpa_info = level1.get('gpa_analysis', {})
        eng_info = level1.get('english_analysis', {})
        
        status_color = '#06A77D' if level1.get('status') == 'PASS' else '#F18F01'
        
        prereq_html = ""
        for prereq in prerequisites:
            prereq_html += f"""
            <tr>
                <td>{prereq.get('course_name', 'N/A')}</td>
                <td><span class="badge bg-success">✓ Completed</span></td>
                <td>{prereq.get('grade', 'N/A')}</td>
            </tr>
            """
        
        return f"""
        <div class="card">
            <div class="card-header" style="background: linear-gradient(90deg, {status_color} 0%, {status_color}dd 100%); color: white;">
                <i class="fas fa-passport"></i> Level 1: Initial Screening & Eligibility - <strong>{level1.get('status', 'N/A')}</strong>
            </div>
            <div class="card-body">
                <p style="margin-bottom: 20px;"><strong>Processing Notes:</strong></p>
                <div style="background: #f0f4f8; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                    {level1.get('processing_notes', 'N/A')}
                </div>
                
                <h6 style="color: {self.colors['primary']}; margin-top: 20px; margin-bottom: 15px;">
                    <i class="fas fa-tasks"></i> Eligibility Checklist
                </h6>
                
                <table class="table table-sm" style="margin-bottom: 20px;">
                    <thead>
                        <tr>
                            <th>Requirement</th>
                            <th>Status</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Bachelor's Degree</td>
                            <td>{'<span class="badge bg-success">✓</span>' if checklist.get('documents_complete') else '<span class="badge bg-danger">✗</span>'}</td>
                            <td>4-year degree in Agriculture or related field</td>
                        </tr>
                        <tr>
                            <td>Official Transcripts</td>
                            <td>{'<span class="badge bg-success">✓</span>' if checklist.get('documents_complete') else '<span class="badge bg-danger">✗</span>'}</td>
                            <td>All semesters/years submitted</td>
                        </tr>
                        <tr>
                            <td>English Proficiency</td>
                            <td>{'<span class="badge bg-success">✓</span>' if checklist.get('english_proficiency_valid') else '<span class="badge bg-danger">✗</span>'}</td>
                            <td>{eng_info.get('test_type', 'N/A')}: {eng_info.get('score', 0)} (Min: {eng_info.get('minimum_required', 79)})</td>
                        </tr>
                        <tr>
                            <td>GPA Requirement</td>
                            <td>{'<span class="badge bg-success">✓</span>' if gpa_info.get('meets_minimum') else '<span class="badge bg-danger">✗</span>'}</td>
                            <td>Converted: {gpa_info.get('converted_gpa', 0):.2f}/4.0 (Min: 3.0)</td>
                        </tr>
                        <tr>
                            <td>Application Fee</td>
                            <td>{'<span class="badge bg-success">✓</span>' if checklist.get('fee_paid') else '<span class="badge bg-danger">✗</span>'}</td>
                            <td>Payment confirmed</td>
                        </tr>
                    </tbody>
                </table>
                
                <h6 style="color: {self.colors['primary']}; margin-top: 20px; margin-bottom: 15px;">
                    <i class="fas fa-book"></i> Prerequisite Coursework
                </h6>
                
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Course</th>
                            <th>Status</th>
                            <th>Grade</th>
                        </tr>
                    </thead>
                    <tbody>
                        {prereq_html}
                    </tbody>
                </table>
            </div>
        </div>
        """
    
    def _generate_cohort_comparison_text(self, composite_score: float, all_scores: List[float]) -> str:
        """Generate accurate cohort comparison text"""
        percentile = self.stats_calc.calculate_percentile(composite_score, all_scores)
        
        if percentile is None or len(all_scores) < 2:
            return """
            <div class="comparison-note">
                <i class="fas fa-info-circle"></i> <strong>Cohort Comparison:</strong> Insufficient cohort data for percentile ranking comparison.
            </div>
            """
        
        # Get statistics
        stats_obj = self.stats_calc.get_distribution_stats(all_scores)
        median = stats_obj.get('median', 0)
        mean = stats_obj.get('mean', 0)
        
        # Generate comparison text
        comparison_text = f"""
            <div class="comparison-note">
                <i class="fas fa-info-circle"></i> <strong>Cohort Comparison:</strong> 
                This applicant's composite score of {composite_score:.1f} ranks in the {percentile:.0f}th percentile. 
                The cohort median is {median:.1f} and the mean is {mean:.1f}.
            </div>
            """
        
        return comparison_text
    
    def _upload_to_s3(self, html_content: str, s3_key: str) -> Dict[str, Any]:
        """Upload HTML content to S3
        
        Args:
            html_content: HTML content to upload
            s3_key: S3 object key/path
            
        Returns:
            Dictionary with upload status and information
        """
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
            
            logger.info(f"Uploading report to s3://{self.s3_bucket}/{s3_key}")
            
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=html_content.encode('utf-8'),
                ContentType='text/html',
                CacheControl='max-age=3600'
            )
            
            # Generate S3 URL
            s3_url = f"https://{self.s3_bucket}.s3.amazonaws.com/{s3_key}"
            
            logger.info(f"Successfully uploaded report to S3: {s3_url}")
            
            return {
                'success': True,
                'bucket': self.s3_bucket,
                'key': s3_key,
                'url': s3_url,
                'message': f'Report successfully uploaded to S3'
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
        """Generate comprehensive professional report and save to S3
        
        Args:
            s3_key: S3 object key for the report. If None, will be auto-generated as:
                   {s3_prefix}/{application_id}_{student_name}_{timestamp}.html
        
        Returns:
            Dictionary with generation and upload status
        """
        
        student_name = self.student.get('student_name', 'N/A')
        app_id = self.student.get('application_id', 'N/A')
        specialization = self.student.get('specialization', 'N/A')
        final_decision = self.student.get('level4_Result', {}).get('final_decision', 'N/A')
        confidence = self.student.get('level4_Result', {}).get('confidence_level', 'N/A')
        composite_score = self.student.get('level4_Result', {}).get('composite_score', 0)
        
        all_scores = self._extract_all_scores()
        comp_percentile = self.stats_calc.calculate_percentile(composite_score, all_scores['composite'])
        
        # Generate charts
        print("Generating multi-metric comparison chart...")
        multi_metric = self._create_multi_metric_comparison()
        print("Generating distribution analysis chart...")
        distribution_analysis = self._create_score_distribution_analysis()
        
        print("Generating score breakdown...")
        score_breakdown = self._create_score_breakdown_details()
        eligibility = self._create_eligibility_checklist()
        cohort_comparison = self._generate_cohort_comparison_text(composite_score, all_scores['composite'])
        
        decision_color = self._get_decision_color(final_decision)
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Professional Admissions Report - {student_name}</title>
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
            max-width: 1500px;
            margin-top: 30px;
            margin-bottom: 30px;
            margin-left: auto;
            margin-right: auto;
            padding-left: 20px;
            padding-right: 20px;
        }}
        
        .card {{
            border: none;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            border-radius: 10px;
            margin-bottom: 20px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        }}
        
        .card-header {{
            background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            border: none;
            border-radius: 10px 10px 0 0;
            font-weight: 600;
            padding: 15px 20px;
        }}
        
        .decision-banner {{
            background: linear-gradient(135deg, {decision_color} 0%, {decision_color}dd 100%);
            color: white;
            padding: 50px 40px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }}
        
        .decision-badge {{
            display: inline-block;
            padding: 25px 60px;
            background: rgba(255,255,255,0.2);
            border-radius: 60px;
            font-size: 2.2em;
            font-weight: 700;
            border: 3px solid white;
            margin: 20px 0;
        }}
        
        .metric-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            border-top: 5px solid var(--primary);
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }}
        
        .metric-value {{
            font-size: 2.5em;
            font-weight: 700;
            color: var(--primary);
            margin: 15px 0;
        }}
        
        .metric-label {{
            font-size: 0.95em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 500;
        }}
        
        .section-title {{
            font-size: 1.6em;
            color: var(--primary);
            margin: 40px 0 25px 0;
            padding-bottom: 15px;
            border-bottom: 3px solid var(--accent);
            font-weight: 700;
        }}
        
        .chart-container {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }}
        
        .accordion-button {{
            font-weight: 600;
            color: var(--primary);
            background-color: #f8f9fa;
        }}
        
        .accordion-button:not(.collapsed) {{
            background-color: #e8f4f8;
            color: var(--primary);
        }}
        
        .accordion-button:focus {{
            box-shadow: 0 0 0 0.25rem rgba(46, 134, 171, 0.25);
        }}
        
        .nav-tabs {{
            border-bottom: 2px solid #e9ecef;
            margin-bottom: 20px;
        }}
        
        .nav-tabs .nav-link {{
            color: var(--primary);
            border: none;
            border-bottom: 3px solid transparent;
            font-weight: 600;
            padding: 12px 20px;
        }}
        
        .nav-tabs .nav-link:hover {{
            border-bottom-color: var(--accent);
            color: var(--accent);
        }}
        
        .nav-tabs .nav-link.active {{
            background-color: transparent;
            color: var(--primary);
            border-bottom-color: var(--primary);
        }}
        
        .info-box {{
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-left: 5px solid var(--primary);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        
        .success-box {{
            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
            border-left: 5px solid var(--success);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        
        .warning-box {{
            background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
            border-left: 5px solid var(--warning);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        
        .strength-item {{
            background: #E8F5E9;
            border-left: 5px solid var(--success);
            padding: 15px;
            margin-bottom: 12px;
            border-radius: 5px;
            color: #2E7D32;
        }}
        
        .weakness-item {{
            background: #FFEBEE;
            border-left: 5px solid var(--danger);
            padding: 15px;
            margin-bottom: 12px;
            border-radius: 5px;
            color: #B71C1C;
        }}
        
        .detail-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        
        .detail-table th {{
            background: #f0f4f8;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: var(--primary);
            border-bottom: 2px solid var(--primary);
        }}
        
        .detail-table td {{
            padding: 12px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .detail-table tbody tr:hover {{
            background: #f8f9fa;
        }}
        
        .header-info {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }}
        
        .header-info h1 {{
            color: var(--primary);
            font-weight: 700;
            margin-bottom: 15px;
        }}
        
        .badge {{
            padding: 8px 15px;
            font-weight: 600;
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
        
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        @media (max-width: 768px) {{
            .container-main {{
                padding-left: 15px;
                padding-right: 15px;
            }}
            
            .decision-badge {{
                font-size: 1.5em;
                padding: 15px 30px;
            }}
            
            .metric-value {{
                font-size: 2em;
            }}
            
            .metric-grid {{
                grid-template-columns: 1fr;
            }}
            
            .section-title {{
                font-size: 1.3em;
            }}
        }}
        
        .comparison-note {{
            background: #FFF9E6;
            border-left: 4px solid var(--accent);
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
            font-size: 0.95em;
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
                Comprehensive Application Review Report
            </span>
        </div>
    </nav>
    
    <div class="container-main">
        <!-- Header Info Card -->
        <div class="header-info">
            <h1>
                <i class="fas fa-user-graduate"></i> {student_name}
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
        <div class="decision-banner fade-in">
            <h2 style="font-weight: 700; margin-bottom: 15px;">RECOMMENDED DECISION</h2>
            <div class="decision-badge">
                {final_decision}
            </div>
            <p style="font-size: 1.1em; margin-bottom: 0;">
                <strong>Confidence: {confidence}</strong> | 
                <strong>Funding: {self.student.get('level4_Result', {}).get('funding_recommendation', 'N/A')}</strong>
            </p>
        </div>
        
        <!-- Key Metrics -->
        <div class="section-title">
            <i class="fas fa-chart-bar"></i> Composite Score Analysis
        </div>
        
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Composite Score</div>
                <div class="metric-value">{composite_score:.1f}</div>
                <div class="metric-label" style="font-size: 0.85em; margin-top: 10px;">out of 100</div>
                {f'<p style="color: var(--primary); margin-top: 10px;"><strong>Percentile: {comp_percentile:.1f}%</strong></p>' if comp_percentile is not None else '<p style="color: #999; margin-top: 10px; font-size: 0.85em;">Percentile: N/A</p>'}
            </div>
            <div class="metric-card" style="border-top-color: var(--accent);">
                <div class="metric-label">Academic Component</div>
                <div class="metric-value">{self.student.get('level2_result', {}).get('academic_score', 0):.1f}</div>
                <div class="metric-label" style="font-size: 0.85em; margin-top: 10px;">40% weight</div>
            </div>
            <div class="metric-card" style="border-top-color: var(--info);">
                <div class="metric-label">Holistic Review</div>
                <div class="metric-value">{self.student.get('level3_result', {}).get('holistic_score', 0):.1f}</div>
                <div class="metric-label" style="font-size: 0.85em; margin-top: 10px;">35% weight</div>
            </div>
            <div class="metric-card" style="border-top-color: var(--success);">
                <div class="metric-label">Program Fit Score</div>
                <div class="metric-value">{self.student.get('level4_Result', {}).get('program_fit_score', 0):.1f}</div>
                <div class="metric-label" style="font-size: 0.85em; margin-top: 10px;">out of 100</div>
            </div>
        </div>
        
        <!-- Comparison Note -->
        {cohort_comparison}
        
        <!-- Detailed Comparative Analysis -->
        <div class="section-title" style="margin-top: 50px;">
            <i class="fas fa-chart-line"></i> Cohort Comparative Analysis
        </div>
        
        <!-- Tabs for different analyses -->
        <ul class="nav nav-tabs">
            <li class="nav-item">
                <a class="nav-link active" data-bs-toggle="tab" href="#multiMetric">
                    <i class="fas fa-th"></i> Multi-Metric Overview
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" data-bs-toggle="tab" href="#distribution">
                    <i class="fas fa-box-plot"></i> Score Distribution
                </a>
            </li>
        </ul>
        
        <div class="tab-content">
            <div id="multiMetric" class="tab-pane fade show active">
                <div class="chart-container">
                    <div class="info-box">
                        <i class="fas fa-lightbulb"></i> <strong>Multi-Metric Overview:</strong>
                        <p style="margin-top: 10px; margin-bottom: 0;">Four key scores displayed for all applicants, sorted by composite score (lowest to highest). Dashed lines show cohort averages. Your scores highlighted in green.</p>
                    </div>
                    {multi_metric}
                </div>
            </div>
            <div id="distribution" class="tab-pane fade">
                <div class="chart-container">
                    <div class="info-box">
                        <i class="fas fa-box-plot"></i> <strong>Score Distribution Analysis:</strong>
                        <p style="margin-top: 10px; margin-bottom: 0;">Box plots show the range and quartiles of each score across the cohort. Stars indicate this applicant's scores, helping you see where they fall within the distribution.</p>
                    </div>
                    {distribution_analysis}
                </div>
            </div>
        </div>
        
        <!-- Score Breakdown & Justification -->
        <div class="section-title" style="margin-top: 50px;">
            <i class="fas fa-sitemap"></i> Score Composition & Detailed Justification
        </div>
        
        <div class="card">
            <div class="card-body" style="padding: 0;">
                {score_breakdown}
            </div>
        </div>
        
        <!-- Eligibility -->
        <div class="section-title" style="margin-top: 50px;">
            <i class="fas fa-check-square"></i> Eligibility & Prerequisites
        </div>
        
        {eligibility}
        
        <!-- Strengths & Weaknesses -->
        <div class="section-title" style="margin-top: 50px;">
            <i class="fas fa-balance-scale"></i> Application Profile
        </div>
        
        <div class="row">
            <div class="col-lg-6">
                <div class="card">
                    <div class="card-header">
                        <i class="fas fa-star"></i> Key Strengths
                    </div>
                    <div class="card-body">
                        {self._generate_strength_items()}
                    </div>
                </div>
            </div>
            <div class="col-lg-6">
                <div class="card">
                    <div class="card-header" style="background: linear-gradient(90deg, var(--warning) 0%, var(--danger) 100%);">
                        <i class="fas fa-exclamation-triangle"></i> Areas for Development
                    </div>
                    <div class="card-body">
                        {self._generate_weakness_items()}
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Final Recommendation -->
        <div class="section-title" style="margin-top: 50px;">
            <i class="fas fa-clipboard-check"></i> Admissions Officer Recommendation
        </div>
        
        <div class="success-box">
            <h5 style="color: var(--success); margin-bottom: 15px;">
                <i class="fas fa-thumbs-up"></i> Comprehensive Assessment
            </h5>
            <p>{self.student.get('level4_Result', {}).get('funding_rationale', 'Assessment pending.')}</p>
        </div>
        
        <!-- Confidence Basis -->
        <div class="info-box">
            <h5 style="color: var(--primary); margin-bottom: 15px;">
                <i class="fas fa-shield-alt"></i> Confidence Basis
            </h5>
            <ul style="margin-bottom: 0;">
                {self._generate_confidence_list()}
            </ul>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p style="margin-bottom: 10px;">
                <i class="fas fa-file-pdf"></i> This comprehensive admissions report was automatically generated.
            </p>
            <p style="margin-bottom: 0; font-size: 0.9em;">
                For questions regarding this evaluation, please contact the Graduate Admissions Office.
            </p>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Refresh plotly charts when tabs change
        document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {{
            tab.addEventListener('shown.bs.tab', function() {{
                window.dispatchEvent(new Event('resize'));
            }});
        }});
    </script>
</body>
</html>
"""
        
        # Generate S3 key if not provided
        if not s3_key:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = student_name.replace(' ', '_').replace('/', '_')
            s3_key = f"{self.s3_prefix}/{app_id}_{safe_name}_{timestamp}.html"
        
        print(f"Uploading report to S3: s3://{self.s3_bucket}/{s3_key}")
        upload_result = self._upload_to_s3(html_content, s3_key)
        
        return {
            'generation': {
                'success': True,
                'student_name': student_name,
                'application_id': app_id,
                'report_generated': True,
                'html_length': len(html_content)
            },
            'upload': upload_result
        }
    
    def _get_decision_color(self, decision: str) -> str:
        color_map = {
            'ACCEPT': '#06A77D',
            'WAITLIST': '#F18F01',
            'REJECT': '#C73E1D',
            'CONDITIONAL': '#2E86AB'
        }
        return color_map.get(decision, '#999999')
    
    def _get_confidence_color(self, confidence: str) -> str:
        color_map = {
            'HIGH': '#06A77D',
            'MEDIUM': '#F18F01',
            'LOW': '#C73E1D'
        }
        return color_map.get(confidence, '#999999')
    
    def _generate_strength_items(self) -> str:
        strengths = self.student.get('level4_Result', {}).get('strengths', [])
        html = ""
        for strength in strengths:
            html += f'<div class="strength-item"><i class="fas fa-check-circle"></i> {strength}</div>\n'
        return html if html else '<p style="color: #999;">No additional strengths documented.</p>'
    
    def _generate_weakness_items(self) -> str:
        weaknesses = self.student.get('level4_Result', {}).get('weaknesses', [])
        html = ""
        for weakness in weaknesses:
            html += f'<div class="weakness-item"><i class="fas fa-exclamation-circle"></i> {weakness}</div>\n'
        return html if html else '<p style="color: #999;">No significant weaknesses identified.</p>'
    
    def _generate_confidence_list(self) -> str:
        basis = self.student.get('level4_Result', {}).get('confidence_basis', [])
        html = ""
        for item in basis:
            html += f'<li style="margin-bottom: 10px;"><i class="fas fa-check" style="color: var(--success); margin-right: 10px;"></i> {item}</li>\n'
        return html