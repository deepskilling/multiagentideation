"""
Multi-Agent Creativity System for SaaS Product Ideation

An autonomous multi-agent AI system that generates, evaluates, and evolves 
innovative SaaS product ideas using specialized LLM agents.
"""

__version__ = "1.0.0"
__author__ = "Deepskilling / CognitiveBricks"

from core.orchestrator import CreativityOrchestrator
from core.models import SaaSIdea, Evaluation, Domain, RevenueModel
from core.database import IdeaDatabase
from core.scoring import ScoringEngine

__all__ = [
    'CreativityOrchestrator',
    'SaaSIdea',
    'Evaluation',
    'Domain',
    'RevenueModel',
    'IdeaDatabase',
    'ScoringEngine'
]

