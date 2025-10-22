from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


# ============================================================================
# LEVEL 1: INITIAL SCREENING & ELIGIBILITY
# ============================================================================

class DocumentCheckDetails(BaseModel):
    """Details of individual document verification"""
    document_name: str = Field(description="Name of the document")
    present: bool = Field(description="Whether document is present")
    valid: bool = Field(description="Whether document is valid/readable")
    s3_path: Optional[str] = Field(None, description="S3 path if document exists")
    issue: Optional[str] = Field(None, description="Issue description if invalid")

class GPAAnalysis(BaseModel):
    """GPA conversion and validation details"""
    original_gpa: str = Field(description="Original GPA as stated (e.g., '8.5/10.0')")
    converted_gpa: float = Field(description="GPA converted to 4.0 scale")
    meets_minimum: bool = Field(description="Whether GPA meets minimum threshold (3.0)")
    minimum_required: float = Field(default=3.0, description="Minimum GPA required")
    margin: float = Field(description="Margin above/below minimum")

class EnglishProficiencyAnalysis(BaseModel):
    """English test score analysis"""
    test_type: str = Field(description="TOEFL or IELTS")
    score: int = Field(description="Total score")
    breakdown: Optional[str] = Field(None, description="Section-wise scores if available")
    minimum_required: int = Field(description="Minimum score required (TOEFL 79, IELTS 6.5)")
    meets_minimum: bool = Field(description="Whether score meets threshold")
    margin: int = Field(description="Points above/below minimum")

class PassportAnalysis(BaseModel):
    """Passport validity analysis"""
    passport_number: str = Field(description="Passport number from document")
    expiry_date: str = Field(description="Expiry date (YYYY-MM-DD)")
    months_remaining: int = Field(description="Months until expiry from today")
    valid: bool = Field(description="Whether valid for 6+ months beyond program start")
    issue: Optional[str] = Field(None, description="Issue if invalid")

class PrerequisiteCheck(BaseModel):
    """Prerequisite coursework verification"""
    course_name: str = Field(description="Name of prerequisite course")
    completed: bool = Field(description="Whether course was completed")
    grade: Optional[str] = Field(None, description="Grade received if completed")

class Level1Result(BaseModel):
    """Level 1: Initial Screening & Eligibility Results"""
    
    level: int = Field(default=1, description="Evaluation level identifier")
    application_id: str = Field(description="Unique application identifier")
    
    status: str = Field(description="PASS | INCOMPLETE | FAIL")
    
    checklist: Dict[str, bool] = Field(
        description="High-level eligibility checks: documents_complete, minimum_gpa_met, english_proficiency_valid, passport_valid, prerequisites_met, fee_paid"
    )
    
    # document_details: List[DocumentCheckDetails] = Field(
    #     description="Detailed verification status of each required document"
    # )
    
    missing_items: List[str] = Field(
        description="List of missing or invalid documents/requirements"
    )
    
    gpa_analysis: GPAAnalysis = Field(
        description="Detailed GPA conversion and validation"
    )
    
    english_analysis: EnglishProficiencyAnalysis = Field(
        description="Detailed English test score analysis"
    )
    
    passport_analysis: PassportAnalysis = Field(
        description="Passport validity verification details"
    )
    
    prerequisite_analysis: List[PrerequisiteCheck] = Field(
        description="Verification of prerequisite courses (Plant Science, Soil Science, Statistics)"
    )
    
    next_action: str = Field(
        description="Next pipeline stage: level2 | request_documents | reject"
    )
    
    processing_notes: str = Field(
        description="Comprehensive summary of Level 1 screening findings"
    )
    
    # processed_at: datetime = Field(
    #     default_factory=datetime.utcnow,
    #     description="ISO timestamp when Level 1 processing completed"
    # )


# ============================================================================
# LEVEL 2: ACADEMIC CREDENTIALS EVALUATION
# ============================================================================

class GPADetailedAnalysis(BaseModel):
    """Detailed GPA analysis with trends and context"""
    original_gpa: str = Field(description="Original GPA format")
    converted_gpa: float = Field(description="4.0 scale GPA")
    trend: str = Field(description="IMPROVING | STABLE | DECLINING")
    semester_progression: List[float] = Field(description="Semester-by-semester GPA values")
    core_agriculture_gpa: Optional[float] = Field(None, description="GPA in core agriculture courses")
    specialization_gpa: Optional[float] = Field(None, description="GPA in specialization courses")
    institutional_context: str = Field(description="Context about institution's grading rigor")
    gpa_score: float = Field(ge=0, le=100, description="Normalized GPA score (0-100)")

class GREAnalysis(BaseModel):
    """GRE test score analysis"""
    quantitative_score: int = Field(ge=130, le=170, description="GRE Quantitative score")
    quantitative_percentile: int = Field(ge=0, le=100, description="Quantitative percentile")
    verbal_score: int = Field(ge=130, le=170, description="GRE Verbal score")
    verbal_percentile: int = Field(ge=0, le=100, description="Verbal percentile")
    awa_score: float = Field(ge=0, le=6, description="Analytical Writing Assessment score")
    awa_percentile: int = Field(ge=0, le=100, description="AWA percentile")
    composite_percentile: int = Field(description="Weighted composite percentile (Quant 70%, Verbal 20%, AWA 10%)")
    assessment: str = Field(description="EXCELLENT | STRONG | GOOD | ADEQUATE | WEAK")
    gre_score: float = Field(ge=0, le=100, description="Normalized GRE score (0-100)")

class CourseworkAnalysis(BaseModel):
    """Coursework depth and breadth analysis"""
    total_agriculture_courses: int = Field(description="Total number of agriculture courses taken")
    advanced_courses: int = Field(description="Number of advanced (400/500+ level) courses")
    specialization_courses: int = Field(description="Courses in intended specialization area")
    core_prerequisites: Dict[str, str] = Field(
        description="Core prerequisite courses with grades (e.g., {'Data Structures': 'A', 'Algorithms': 'A-'})"
    )
    prerequisites_met: bool = Field(description="Whether all prerequisites are satisfied")
    grade_quality: str = Field(description="Overall grade quality in agriculture courses (e.g., '85% A/A+ grades')")
    coursework_score: float = Field(ge=0, le=100, description="Normalized coursework score (0-100)")

class Level2Result(BaseModel):
    """Level 2: Academic Credentials Evaluation Results"""
    
    level: int = Field(default=2, description="Evaluation level identifier")
    application_id: str = Field(description="Unique application identifier")
    
    academic_score: float = Field(
        ge=0, le=100,
        description="Overall academic score (GPA 50%, GRE 35%, Coursework 15%)"
    )
    
    component_scores: Dict[str, float] = Field(
        description="Breakdown of scores: gpa_score, gre_score, coursework_score (each 0-100)"
    )
    
    gpa_analysis: GPADetailedAnalysis = Field(
        description="Comprehensive GPA analysis with trends and context"
    )
    
    gre_analysis: GREAnalysis = Field(
        description="Detailed GRE score analysis with percentiles and assessment"
    )
    
    coursework_analysis: CourseworkAnalysis = Field(
        description="Analysis of coursework depth, breadth, and prerequisite satisfaction"
    )
    
    status: str = Field(
        description="PASS | CONDITIONAL | FAIL"
    )
    
    next_action: str = Field(
        description="Next pipeline stage: level3 | conditional_admit | reject"
    )
    
    detailed_analysis: str = Field(
        description="Comprehensive narrative assessment of academic credentials, strengths, and concerns"
    )
    
    # processed_at: datetime = Field(
    #     default_factory=datetime.utcnow,
    #     description="ISO timestamp when Level 2 processing completed"
    # )


# ============================================================================
# LEVEL 3: HOLISTIC REVIEW
# ============================================================================

class SOPAnalysis(BaseModel):
    """Statement of Purpose detailed analysis"""
    clarity_of_goals_score: int = Field(ge=0, le=25, description="Clarity of academic and career goals (0-25)")
    research_alignment_score: int = Field(ge=0, le=25, description="Research interest alignment with program (0-25)")
    writing_quality_score: int = Field(ge=0, le=15, description="Writing quality and communication (0-15)")
    personal_context_score: int = Field(ge=0, le=15, description="Personal background and motivation (0-15)")
    key_themes: List[str] = Field(description="Main themes identified in SOP (e.g., ['sustainable agriculture', 'soil health'])")
    agricultural_relevance: str = Field(description="HIGH | MEDIUM | LOW - relevance to agricultural sciences")
    program_fit: str = Field(description="Assessment of fit with OSU program and faculty")
    sop_score: float = Field(ge=0, le=100, description="Overall SOP score (0-100)")

class LORAnalysis(BaseModel):
    """Letters of Recommendation analysis"""
    lor_count: int = Field(ge=0, le=3, description="Number of LORs received")
    lor_scores: List[int] = Field(description="Individual LOR scores (0-100 each)")
    lor_credibility: List[str] = Field(description="Credibility of each recommender: HIGH | MEDIUM | LOW")
    lor_strength: List[str] = Field(description="Strength of each letter: EXCEPTIONAL | STRONG | GOOD | ADEQUATE | WEAK")
    consistency: str = Field(description="Consistency across letters: HIGH | MEDIUM | LOW")
    key_strengths_mentioned: List[str] = Field(description="Common strengths highlighted across LORs")
    red_flags: List[str] = Field(description="Any concerns or red flags identified in LORs")
    weighted_lor_score: float = Field(ge=0, le=100, description="Weighted LOR score (LOR1 40%, LOR2 35%, LOR3 25%)")

class ResearchTechAnalysis(BaseModel):
    """Research and technical experience analysis"""
    research_project_count: int = Field(description="Number of research projects completed")
    publications: int = Field(description="Number of publications (peer-reviewed)")
    conferences: int = Field(description="Number of conference presentations")
    research_duration_months: int = Field(description="Total months of research experience")
    lab_skills: List[str] = Field(description="Laboratory and technical skills demonstrated")
    fieldwork_experience: str = Field(description="Quality of field/practical experience: EXCELLENT | GOOD | ADEQUATE | LIMITED")
    internship_months: int = Field(description="Total months of internship/work experience")
    research_quality: str = Field(description="OUTSTANDING | SUBSTANTIAL | MODERATE | LIMITED | NONE")
    research_tech_score: float = Field(ge=0, le=100, description="Overall research/technical score (0-100)")

class Level3Result(BaseModel):
    """Level 3: Holistic Review Results"""
    
    level: int = Field(default=3, description="Evaluation level identifier")
    application_id: str = Field(description="Unique application identifier")
    
    holistic_score: float = Field(
        ge=0, le=100,
        description="Overall holistic score (SOP 30%, LOR 40%, Research/Tech 30%)"
    )
    
    component_scores: Dict[str, float] = Field(
        description="Breakdown: sop_score, lor_score, research_tech_score (each 0-100)"
    )
    
    sop_analysis: SOPAnalysis = Field(
        description="Detailed Statement of Purpose evaluation"
    )
    
    lor_analysis: LORAnalysis = Field(
        description="Comprehensive Letters of Recommendation analysis"
    )
    
    research_tech_analysis: ResearchTechAnalysis = Field(
        description="Research experience and technical skills assessment"
    )
    
    strengths: List[str] = Field(
        description="Top 3-5 qualitative strengths identified (specific with evidence)"
    )
    
    weaknesses: List[str] = Field(
        description="Key 2-3 weaknesses or areas of concern (specific with context)"
    )
    
    status: str = Field(
        description="PASS | WAITLIST | FAIL"
    )
    
    next_action: str = Field(
        description="Next pipeline stage: level4 | waitlist | reject"
    )
    
    narrative_summary: str = Field(
        description="Comprehensive narrative integrating all holistic factors, providing officer-level insight"
    )
    
    # processed_at: datetime = Field(
    #     default_factory=datetime.utcnow,
    #     description="ISO timestamp when Level 3 processing completed"
    # )

class ComponentBreakdown(BaseModel):
    """Weighted contributions to the composite score."""
    academic: float = Field(description="Academic (Level 2) contribution")
    holistic: float = Field(description="Holistic (Level 3) contribution")
    program_fit: float = Field(description="Program Fit contribution")
    potential: float = Field(description="Potential contribution")

class FacultyMatch(BaseModel):
    """Faculty alignment details."""
    faculty: str = Field(description="Faculty name")
    expertise: str = Field(description="Faculty research expertise")
    match_quality: str = Field(description="EXCELLENT | GOOD | ADEQUATE | POOR")


# ============================================================================
# LEVEL 4: Aggregate final
# ============================================================================

class Level4Result(BaseModel):
    """Final decision and synthesis of evaluation."""
    level: int = Field(4, description="Evaluation level identifier")
    application_id: str = Field(description="Unique application identifier")
    
    composite_score: float = Field(
        description="Overall composite score (0-100)"
    )
    component_breakdown: ComponentBreakdown = Field(
        description="Breakdown of weighted score contributions"
    )
    
    program_fit_score: float = Field(
        description="Raw score for program fit (0-15 scaled to 0-100)"
    )
    potential_score: float = Field(
        description="Raw score for potential & trajectory (0-10 scaled to 0-100)"
    )
    
    final_decision: str = Field(
        description="ACCEPT | WAITLIST | REJECT"
    )
    confidence_level: str = Field(
        description="HIGH | MEDIUM | LOW"
    )
    confidence_basis: List[str] = Field(
        description="Reasons for confidence level"
    )
    
    funding_recommendation: str = Field(
        description="Recommended funding type"
    )
    funding_rationale: str = Field(
        description="Explanation for funding recommendation"
    )
    
    strengths: List[str] = Field(
        description="key strengths with evidence"
    )
    weaknesses: List[str] = Field(
        description="Key weaknesses or concerns"
    )
    
    # faculty_matches: List[FacultyMatch] = Field(
    #     description="List of faculty alignment matches"
    # )
    
    # next_steps: str = Field(
    #     description="Suggested next actions (e.g., send offer letter)"
    # )
    
    # processed_at: datetime = Field(
    #     default_factory=datetime.utcnow,
    #     description="Timestamp when Level 4 processing completed"
    # )

# ============================================================================
# AGGREGATED EVALUATION (All Levels)
# ============================================================================

class AggregatedEvaluation(BaseModel):
    """Complete evaluation aggregating all levels"""
    application_id: str = Field(description="Unique application identifier")
    student_name: str = Field(description="Applicant's full name")
    specialization: str = Field(description="Intended specialization track")
    
    level1_result: Optional[Level1Result] = Field(None, description="Level 1 screening results")
    level2_result: Optional[Level2Result] = Field(None, description="Level 2 academic evaluation results")
    level3_result: Optional[Level3Result] = Field(None, description="Level 3 holistic review results")
    level4_Result: Optional[Level4Result] = Field(None, description="Level 4 Comprehensive final evaluation, actionable recommendations, and decision rationale for university officers")
    
    # created_at: datetime = Field(default_factory=datetime.utcnow, description="Evaluation start timestamp")
    # updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")