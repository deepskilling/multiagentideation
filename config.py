"""
Configuration module for Multi-Agent Creativity System
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """System configuration"""
    
    # Paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    DATABASE_PATH = DATA_DIR / "ideas.db"
    VECTOR_STORE_PATH = DATA_DIR / "vectors"
    REPORTS_DIR = BASE_DIR / "reports"
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")
    
    # AWS Bedrock Configuration (optimized for local development)
    USE_AWS_BEDROCK = os.getenv("USE_AWS_BEDROCK", "true").lower() == "true"
    AWS_PROFILE = os.getenv("AWS_PROFILE", "diligent")  # Default to 'diligent' profile for local dev
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    
    # Agent Configuration
    MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "10"))
    TOP_K_IDEAS = int(os.getenv("TOP_K_IDEAS", "5"))
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.85"))
    
    # Scoring Weights
    NOVELTY_WEIGHT = float(os.getenv("NOVELTY_WEIGHT", "0.3"))
    FEASIBILITY_WEIGHT = float(os.getenv("FEASIBILITY_WEIGHT", "0.3"))
    MARKET_FIT_WEIGHT = float(os.getenv("MARKET_FIT_WEIGHT", "0.2"))
    VIABILITY_WEIGHT = float(os.getenv("VIABILITY_WEIGHT", "0.2"))
    
    # Model Selection - Using Claude 3.5 Sonnet via AWS Bedrock (on-demand)
    GENERATOR_MODEL = os.getenv("GENERATOR_MODEL", "claude-3-5-sonnet")
    CRITIC_MODEL = os.getenv("CRITIC_MODEL", "claude-3-5-sonnet")
    SYNTHESIZER_MODEL = os.getenv("SYNTHESIZER_MODEL", "claude-3-5-sonnet")
    DISRUPTOR_MODEL = os.getenv("DISRUPTOR_MODEL", "claude-3-5-sonnet")
    STRATEGIST_MODEL = os.getenv("STRATEGIST_MODEL", "claude-3-5-sonnet")
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    # Domains
    DOMAINS = [
        "DevOps",
        "Cloud Infrastructure",
        "GRC (Governance, Risk, Compliance)",
        "Business Intelligence",
        "AI/ML Operations",
        "Cybersecurity",
        "Data Analytics",
        "Enterprise Collaboration"
    ]
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.VECTOR_STORE_PATH.mkdir(exist_ok=True)
        cls.REPORTS_DIR.mkdir(exist_ok=True)

config = Config()

