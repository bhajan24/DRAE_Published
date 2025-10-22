from pydantic import BaseModel, Field
from typing import List, Optional


class PersonalInformation(BaseModel):
    """Personal and contact information of the applicant"""
    full_name: str = Field(
        default="",
        description="Full legal name of the applicant as it appears on official documents."
    )
    date_of_birth: str = Field(
        default="",
        description="Date of birth of the applicant in YYYY-MM-DD format"
    )
    gender: str = Field(
        default="",
        description="Gender identity of the applicant (Male, Female, Other, Prefer not to say)"
    )
    nationality: str = Field(
        default="",
        description="Country of citizenship of the applicant"
    )
    email: str = Field(
        default="",
        description="Primary email address for communication with the applicant"
    )
    phone: str = Field(
        default="",
        description="Contact phone number with country code (e.g., +91-9876543210)"
    )
    hometown: str = Field(
        default="",
        description="City or town where the applicant currently resides or originates from"
    )
    passport_number: str = Field(
        default="",
        description="Passport number for international applicants"
    )
    family_background: str = Field(
        default="",
        description="Brief description of family background, particularly relevant agricultural or educational context"
    )


class AcademicBackground(BaseModel):
    """Academic credentials and performance history of the applicant"""
    institution: str = Field(
        default="",
        description="Name of the university or college where the undergraduate degree was completed"
    )
    degree: str = Field(
        default="",
        description="Type and field of the undergraduate degree (e.g., B.Sc. Agriculture, B.Tech)"
    )
    graduation_date: str = Field(
        default="",
        description="Date of graduation or expected graduation from undergraduate program"
    )
    gpa: str = Field(
        default="",
        description="Grade Point Average in the original grading scale of the institution (e.g., 7.2/10.0, 3.5/4.0)"
    )
    gpa_4_scale: float = Field(
        default=0.0,
        description="GPA converted to the standard 4.0 scale for comparison purposes"
    )
    trend: str = Field(
        default="",
        description="Overall trend of academic performance throughout the undergraduate program (Improving, Stable, Declining)"
    )
    rank: str = Field(
        default="",
        description="Class rank or percentile standing (e.g., Top 10%, Top 40%)"
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="List of academic subjects or areas where the applicant demonstrated strong performance"
    )
    weaknesses: List[str] = Field(
        default_factory=list,
        description="List of academic subjects or areas where the applicant needs improvement"
    )


class TestScores(BaseModel):
    """Standardized test scores for graduate admissions"""
    gre_verbal: str = Field(
        default="",
        description="GRE Verbal Reasoning score (scale: 130-170)"
    )
    gre_quantitative: str = Field(
        default="",
        description="GRE Quantitative Reasoning score (scale: 130-170)"
    )
    gre_awa: str = Field(
        default="",
        description="GRE Analytical Writing Assessment score (scale: 0.0-6.0)"
    )
    english_test: str = Field(
        default="",
        description="Type of English proficiency test taken (TOEFL, IELTS, PTE, or Duolingo)"
    )
    english_score: str = Field(
        default="",
        description="Score obtained in the English proficiency test (scale varies by test: TOEFL 0-120, IELTS 0-9, PTE 10-90, Duolingo 10-160)"
    )


class ResearchProject(BaseModel):
    """Details of a research project undertaken by the applicant"""
    title: str = Field(
        default="",
        description="Title of the research project"
    )
    duration: str = Field(
        default="",
        description="Duration of the research project (e.g., 6 months, 1 year)"
    )
    description: str = Field(
        default="",
        description="Brief description of the research project objectives and outcomes"
    )
    role: str = Field(
        default="",
        description="Role of the applicant in the research project (e.g., Principal Investigator, Research Assistant)"
    )


class ResearchExperience(BaseModel):
    """Research experience and academic contributions of the applicant"""
    count: str = Field(
        default="",
        description="Total number of research projects completed or participated in"
    )
    projects: List[ResearchProject] = Field(
        default_factory=list,
        description="List of research projects with title, duration, description, and role"
    )
    publications: str = Field(
        default="",
        description="Number of peer-reviewed publications (journals, conferences, etc.)"
    )
    conferences: str = Field(
        default="",
        description="Number of academic conferences attended or presented at"
    )
    lab_skills: List[str] = Field(
        default_factory=list,
        description="List of laboratory techniques and research methodologies the applicant is proficient in"
    )


class WorkExperience(BaseModel):
    """Professional work experience of the applicant"""
    organization: str = Field(
        default="",
        description="Name of the organization or company where the applicant worked"
    )
    role: str = Field(
        default="",
        description="Job title or position held by the applicant"
    )
    duration: str = Field(
        default="",
        description="Length of employment (e.g., 2 years, 6 months)"
    )
    responsibilities: str = Field(
        default="",
        description="Key responsibilities and accomplishments in the role"
    )


class ProgramSpecific(BaseModel):
    """Program-specific information related to the MSc Agriculture application"""
    specialization: str = Field(
        default="",
        description="Intended area of specialization within Agriculture (e.g., Soil Science, Crop Science, Agricultural Economics)"
    )
    research_interest: str = Field(
        default="",
        description="Specific research topics or areas of interest the applicant wishes to pursue during the MSc program"
    )
    career_goal: str = Field(
        default="",
        description="Long-term career objectives and professional aspirations after completing the MSc degree"
    )


class ProfileAnalysis(BaseModel):
    """Holistic analysis of the applicant's profile for admissions assessment"""
    strengths: str = Field(
        default="",
        description="Key strengths and competitive advantages of the applicant's profile"
    )
    challenges: str = Field(
        default="",
        description="Areas of concern or weaknesses that may impact the application"
    )
    profile_type: str = Field(
        default="",
        description="Overall characterization of the applicant's background and experience (e.g., research-focused, industry professional, practical farmer)"
    )


class MSCAgricultureApplication(BaseModel):
    """Complete application for MSc Agriculture program at the university"""
    
    personal_information: PersonalInformation = Field(
        default_factory=PersonalInformation,
        description="Personal details and contact information of the applicant"
    )
    academic_background: AcademicBackground = Field(
        default_factory=AcademicBackground,
        description="Educational qualifications and academic performance history"
    )
    test_scores: TestScores = Field(
        default_factory=TestScores,
        description="Standardized test scores including GRE and English proficiency tests"
    )
    research_experience: ResearchExperience = Field(
        default_factory=ResearchExperience,
        description="Research projects, publications, conferences, and lab skills"
    )
    work_experience: List[WorkExperience] = Field(
        default_factory=list,
        description="Professional work experience relevant to the field of agriculture"
    )
    extracurricular: List[str] = Field(
        default_factory=list,
        description="Extracurricular activities, leadership roles, and community involvement"
    )
    program_specific: ProgramSpecific = Field(
        default_factory=ProgramSpecific,
        description="Information specific to the MSc Agriculture program"
    )
    profile_analysis: ProfileAnalysis = Field(
        default_factory=ProfileAnalysis,
        description="Comprehensive evaluation of the applicant's profile"
    )
