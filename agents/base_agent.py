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
from core.error_recovery import get_error_recovery_engine, ErrorType


class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    # Class-level token tracking (shared across all agents)
    _total_input_tokens = 0
    _total_output_tokens = 0
    _api_calls = 0
    
    # Claude Sonnet 4.5 pricing (cross-region inference profile)
    INPUT_TOKEN_COST = 0.003 / 1000  # $3 per 1M tokens = $0.003 per 1K
    OUTPUT_TOKEN_COST = 0.015 / 1000  # $15 per 1M tokens = $0.015 per 1K
    
    def __init__(self, name: str, model: str, role_description: str, enable_error_recovery: bool = True):
        self.name = name
        self.model = model
        self.role_description = role_description
        self.message_history = []
        self.enable_error_recovery = enable_error_recovery
        self.error_recovery_engine = get_error_recovery_engine() if enable_error_recovery else None
        
        # Instance-level token tracking
        self.input_tokens = 0
        self.output_tokens = 0
        self.api_calls = 0
        
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
        """Call the appropriate LLM based on model configuration with error recovery"""
        
        if self.enable_error_recovery:
            return self._call_llm_with_recovery(prompt, system_message, temperature, max_tokens)
        else:
            return self._call_llm_direct(prompt, system_message, temperature, max_tokens)
    
    def _call_llm_direct(self, prompt: str, system_message: Optional[str] = None,
                        temperature: float = 0.7, max_tokens: int = 4000) -> str:
        """Direct LLM call without error recovery"""
        # Determine if using AWS Bedrock, OpenAI, or Anthropic
        if config.USE_AWS_BEDROCK and "claude" in self.model.lower():
            return self._call_bedrock_claude(prompt, system_message, temperature, max_tokens)
        elif "gpt" in self.model.lower():
            return self._call_openai(prompt, system_message, temperature, max_tokens)
        elif "claude" in self.model.lower():
            return self._call_anthropic(prompt, system_message, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported model: {self.model}")
    
    def _call_llm_with_recovery(self, prompt: str, system_message: Optional[str] = None,
                                temperature: float = 0.7, max_tokens: int = 4000) -> str:
        """Call LLM with automatic error recovery"""
        
        attempt = 0
        last_error = None
        last_response = None
        
        while attempt < self.error_recovery_engine.max_retries:
            attempt += 1
            
            try:
                # Try the LLM call
                response = self._call_llm_direct(prompt, system_message, temperature, max_tokens)
                
                # Check for errors in response
                detected_error = self.error_recovery_engine.detect_error(response)
                
                if detected_error is None:
                    # Success! Return the response
                    if attempt > 1:
                        print(f"      ✅ {self.name}: Success after {attempt} attempts")
                    return response
                else:
                    # Response has errors, treat as exception
                    print(f"      ⚠️  {self.name}: Detected {detected_error.value} in response")
                    raise ValueError(f"Response validation failed: {detected_error.value}")
                    
            except Exception as e:
                last_error = e
                last_response = None
                
                if attempt < self.error_recovery_engine.max_retries:
                    # Try to recover
                    print(f"      🔧 {self.name}: Attempting recovery (attempt {attempt})")
                    
                    # Build recovery prompt
                    error_type = self.error_recovery_engine.analyze_error(e, last_response)
                    error_key = f"{error_type.value}:{str(e)[:100]}"
                    strategy = self.error_recovery_engine.get_recovery_strategy(error_type, error_key)
                    
                    # Record error
                    self.error_recovery_engine.record_error(error_type, str(e))
                    
                    # Modify prompt and parameters for retry
                    prompt = self.error_recovery_engine.build_recovery_prompt(
                        prompt, error_type, strategy, str(e)
                    )
                    
                    # Adjust parameters based on strategy
                    if "simplified" in strategy.value:
                        max_tokens = min(max_tokens, max_tokens // 2)
                        temperature = max(0.3, temperature - 0.2)
                    
                    # Log and continue to retry
                    continue
                else:
                    # Max retries reached
                    print(f"      ❌ {self.name}: Max retries reached. Raising error.")
                    raise
        
        # Should not reach here, but just in case
        if last_error:
            raise last_error
        return last_response or ""
    
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
            
            # Track token usage
            if 'usage' in response_body:
                input_tokens = response_body['usage'].get('input_tokens', 0)
                output_tokens = response_body['usage'].get('output_tokens', 0)
                
                # Update instance-level counters
                self.input_tokens += input_tokens
                self.output_tokens += output_tokens
                self.api_calls += 1
                
                # Update class-level counters (shared across all agents)
                BaseAgent._total_input_tokens += input_tokens
                BaseAgent._total_output_tokens += output_tokens
                BaseAgent._api_calls += 1
            
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
    
    def get_error_statistics(self) -> Optional[Dict[str, Any]]:
        """Get error recovery statistics for this agent"""
        if self.error_recovery_engine:
            return self.error_recovery_engine.get_error_statistics()
        return None
    
    def save_error_patterns(self, filepath: str):
        """Save learned error patterns to file"""
        if self.error_recovery_engine:
            self.error_recovery_engine.save_error_patterns(filepath)
    
    @classmethod
    def get_total_cost(cls) -> float:
        """
        Calculate total cost across all agents
        
        Returns:
            Total cost in USD
        """
        input_cost = cls._total_input_tokens * cls.INPUT_TOKEN_COST
        output_cost = cls._total_output_tokens * cls.OUTPUT_TOKEN_COST
        return input_cost + output_cost
    
    @classmethod
    def get_cost_summary(cls) -> Dict[str, Any]:
        """
        Get detailed cost summary for all agent calls
        
        Returns:
            Dictionary with cost details
        """
        input_cost = cls._total_input_tokens * cls.INPUT_TOKEN_COST
        output_cost = cls._total_output_tokens * cls.OUTPUT_TOKEN_COST
        total_cost = input_cost + output_cost
        
        return {
            'total_api_calls': cls._api_calls,
            'total_input_tokens': cls._total_input_tokens,
            'total_output_tokens': cls._total_output_tokens,
            'total_tokens': cls._total_input_tokens + cls._total_output_tokens,
            'input_cost_usd': input_cost,
            'output_cost_usd': output_cost,
            'total_cost_usd': total_cost,
            'cost_per_1k_input_tokens': cls.INPUT_TOKEN_COST,
            'cost_per_1k_output_tokens': cls.OUTPUT_TOKEN_COST,
            'model': 'Claude Sonnet 4.5 (AWS Bedrock)'
        }
    
    @classmethod
    def reset_cost_tracking(cls):
        """Reset all cost tracking counters"""
        cls._total_input_tokens = 0
        cls._total_output_tokens = 0
        cls._api_calls = 0
    
    def __str__(self):
        return f"{self.name} ({self.model})"
    
    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"

