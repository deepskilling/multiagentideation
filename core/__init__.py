"""
Core package - Contains core functionality for the multi-agent system
"""
from core.models import (
    SaaSIdea, 
    Evaluation, 
    Domain, 
    RevenueModel,
    AgentMessage,
    IterationResult,
    SystemState
)
from core.database import IdeaDatabase

__all__ = [
    'SaaSIdea',
    'Evaluation',
    'Domain',
    'RevenueModel',
    'AgentMessage',
    'IterationResult',
    'SystemState',
    'IdeaDatabase'
]

