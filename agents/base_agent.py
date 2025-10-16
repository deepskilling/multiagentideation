"""
Base Agent class for all specialized agents
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import openai
import anthropic
import boto3
from botocore.config import Config
import json
from config import config


class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, name: str, model: str, role_description: str):
        self.name = name
        self.model = model
        self.role_description = role_description
        self.message_history = []
        
        # Initialize LLM clients
        self.openai_client = None
        self.anthropic_client = None
        self.bedrock_client = None
        
        # Check if using AWS Bedrock
        if config.USE_AWS_BEDROCK:
            # Initialize AWS Bedrock client with Diligent profile
            # Configure with longer timeouts for large PRD generation
            boto_config = Config(
                read_timeout=300,  # 5 minutes
                connect_timeout=60,
                retries={'max_attempts': 3}
            )
            session = boto3.Session(profile_name=config.AWS_PROFILE)
            self.bedrock_client = session.client(
                service_name='bedrock-runtime',
                region_name=config.AWS_REGION,
                config=boto_config
            )
        elif config.OPENAI_API_KEY:
            self.openai_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        elif config.ANTHROPIC_API_KEY:
            self.anthropic_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    
    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """Execute the agent's primary function"""
        pass
    
    def _call_llm(self, prompt: str, system_message: Optional[str] = None, 
                  temperature: float = 0.7, max_tokens: int = 4000) -> str:
        """Call the appropriate LLM based on model configuration"""
        
        # Determine if using AWS Bedrock, OpenAI, or Anthropic
        if config.USE_AWS_BEDROCK and "claude" in self.model.lower():
            return self._call_bedrock_claude(prompt, system_message, temperature, max_tokens)
        elif "gpt" in self.model.lower():
            return self._call_openai(prompt, system_message, temperature, max_tokens)
        elif "claude" in self.model.lower():
            return self._call_anthropic(prompt, system_message, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported model: {self.model}")
    
    def _call_openai(self, prompt: str, system_message: Optional[str] = None,
                     temperature: float = 0.7, max_tokens: int = 4000) -> str:
        """Call OpenAI API"""
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized. Check API key.")
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    def _call_anthropic(self, prompt: str, system_message: Optional[str] = None,
                       temperature: float = 0.7, max_tokens: int = 4000) -> str:
        """Call Anthropic API"""
        if not self.anthropic_client:
            raise RuntimeError("Anthropic client not initialized. Check API key.")
        
        response = self.anthropic_client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_message or self.role_description,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def _call_bedrock_claude(self, prompt: str, system_message: Optional[str] = None,
                            temperature: float = 0.7, max_tokens: int = 4000) -> str:
        """Call Claude via AWS Bedrock"""
        if not self.bedrock_client:
            raise RuntimeError("Bedrock client not initialized. Check AWS configuration.")
        
        # Map model name to Bedrock model ID
        bedrock_model_id = self._get_bedrock_model_id(self.model)
        
        # Prepare the request body for Claude models
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        # Add system message if provided
        if system_message:
            body["system"] = system_message or self.role_description
        
        # Call Bedrock
        try:
            response = self.bedrock_client.invoke_model(
                modelId=bedrock_model_id,
                body=json.dumps(body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            raise RuntimeError(f"Bedrock API call failed: {str(e)}")
    
    def _get_bedrock_model_id(self, model: str) -> str:
        """Map model name to AWS Bedrock model ID"""
        # Map common model names to Bedrock IDs
        # Note: For newer models (v2), use us.{model-id} for cross-region inference profiles
        model_mapping = {
            "claude-sonnet-4.5": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
            "claude-sonnet-4.5-20250514": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
            "claude-sonnet-4-5": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
            "claude-3-5-sonnet": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            "claude-3-5-sonnet-20241022": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            "claude-3-opus": "anthropic.claude-3-opus-20240229-v1:0",
            "claude-3-sonnet": "anthropic.claude-3-sonnet-20240229-v1:0",
            "claude-3-haiku": "anthropic.claude-3-haiku-20240307-v1:0"
        }
        
        # Try exact match first
        if model in model_mapping:
            return model_mapping[model]
        
        # Try partial match
        model_lower = model.lower()
        for key, bedrock_id in model_mapping.items():
            if key in model_lower:
                return bedrock_id
        
        # Default to Claude 3 Haiku if no match (most compatible)
        print(f"Warning: Model '{model}' not found in mapping, using Claude 3 Haiku")
        return "anthropic.claude-3-haiku-20240307-v1:0"
    
    def log_message(self, message: str):
        """Log a message from this agent"""
        from datetime import datetime
        self.message_history.append({
            "timestamp": datetime.utcnow(),
            "agent": self.name,
            "message": message
        })
    
    def get_history(self) -> list:
        """Get agent's message history"""
        return self.message_history
    
    def __str__(self):
        return f"{self.name} ({self.model})"
    
    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"

