"""
Data models for the Multi-Agent Creativity System
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class Domain(str, Enum):
    """SaaS domains"""
    DEVOPS = "DevOps"
    CLOUD = "Cloud Infrastructure"
    GRC = "GRC (Governance, Risk, Compliance)"
    BI = "Business Intelligence"
    AIML = "AI/ML Operations"
    CYBERSECURITY = "Cybersecurity"
    DATA_ANALYTICS = "Data Analytics"
    COLLABORATION = "Enterprise Collaboration"


class RevenueModel(str, Enum):
    """Revenue models for SaaS"""
    SUBSCRIPTION = "Subscription"
    FREEMIUM = "Freemium"
    USAGE_BASED = "Usage-Based"
    PERPETUAL = "Perpetual License"
    HYBRID = "Hybrid"


class SaaSIdea(BaseModel):
    """Schema for a SaaS product idea"""
    idea_id: Optional[str] = None
    idea_name: str = Field(..., description="Name of the SaaS product")
    problem_statement: str = Field(..., description="Problem this product solves")
    target_user: str = Field(..., description="Target user persona or segment")
    core_features: List[str] = Field(..., description="List of core features")
    differentiator: str = Field(..., description="What makes this product unique")
    tech_stack: List[str] = Field(..., description="Recommended technology stack")
    revenue_model: RevenueModel = Field(..., description="Business model")
    domain: Domain = Field(..., description="Primary domain/category")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    iteration: int = Field(default=0, description="Which iteration this was generated in")
    parent_ideas: List[str] = Field(default_factory=list, description="IDs of parent ideas if synthesized")
    
    class Config:
        json_schema_extra = {
            "example": {
                "idea_name": "CloudAudit Pro",
                "problem_statement": "Organizations struggle to maintain compliance across multi-cloud environments",
                "target_user": "Cloud Security Engineers and Compliance Officers",
                "core_features": [
                    "Real-time compliance monitoring",
                    "Automated audit reports",
                    "Multi-cloud support (AWS, Azure, GCP)"
                ],
                "differentiator": "AI-powered risk prediction and remediation suggestions",
                "tech_stack": ["Python", "React", "Terraform", "PostgreSQL"],
                "revenue_model": "Subscription",
                "domain": "GRC"
            }
        }


class Evaluation(BaseModel):
    """Evaluation scores and justification for an idea"""
    idea_id: str
    novelty: float = Field(..., ge=0.0, le=1.0, description="Novelty score (0-1)")
    feasibility: float = Field(..., ge=0.0, le=1.0, description="Feasibility score (0-1)")
    market_fit: float = Field(..., ge=0.0, le=1.0, description="Market fit score (0-1)")
    viability: float = Field(..., ge=0.0, le=1.0, description="Business viability score (0-1)")
    composite_score: Optional[float] = None
    justification: str = Field(..., description="Detailed reasoning for the scores")
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)
    evaluated_by: str = Field(..., description="Name of the agent that evaluated")
    
    def calculate_composite_score(self, novelty_weight: float = 0.3, 
                                  feasibility_weight: float = 0.3,
                                  market_fit_weight: float = 0.2,
                                  viability_weight: float = 0.2) -> float:
        """Calculate weighted composite score"""
        self.composite_score = (
            novelty_weight * self.novelty +
            feasibility_weight * self.feasibility +
            market_fit_weight * self.market_fit +
            viability_weight * self.viability
        )
        return self.composite_score


class AgentMessage(BaseModel):
    """Message format for inter-agent communication"""
    sender: str
    receiver: str
    content: Any
    message_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class IterationResult(BaseModel):
    """Results from one iteration of the creative loop"""
    iteration_number: int
    generated_ideas: List[SaaSIdea]
    evaluations: List[Evaluation]
    top_ideas: List[str]  # Idea IDs
    merged_ideas: Optional[List[SaaSIdea]] = None
    disrupted_ideas: Optional[List[SaaSIdea]] = None
    should_continue: bool
    strategist_notes: str


class SystemState(BaseModel):
    """Overall system state"""
    current_iteration: int = 0
    total_ideas_generated: int = 0
    best_score: float = 0.0
    converged: bool = False
    domain_focus: Optional[Domain] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

