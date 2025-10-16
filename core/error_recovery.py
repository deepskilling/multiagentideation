"""
Error Recovery System - Self-debugging and automatic error correction
"""
import json
import traceback
from typing import Any, Dict, Optional, Callable, List
from datetime import datetime
from enum import Enum
import re


class ErrorType(Enum):
    """Types of errors that can occur"""
    JSON_PARSE_ERROR = "json_parse"
    VALIDATION_ERROR = "validation"
    LLM_TIMEOUT = "llm_timeout"
    INCOMPLETE_OUTPUT = "incomplete_output"
    MALFORMED_RESPONSE = "malformed_response"
    LOGIC_ERROR = "logic_error"
    API_ERROR = "api_error"


class ErrorRecoveryStrategy(Enum):
    """Recovery strategies for different error types"""
    RETRY_SAME = "retry_same"
    RETRY_SIMPLIFIED = "retry_simplified"
    RETRY_WITH_EXAMPLES = "retry_with_examples"
    RETRY_STRUCTURED = "retry_structured"
    FALLBACK_DEFAULT = "fallback_default"


class ErrorPattern:
    """Tracks patterns in errors for learning"""
    
    def __init__(self, error_type: ErrorType, error_message: str):
        self.error_type = error_type
        self.error_message = error_message
        self.occurrences = 1
        self.successful_recoveries = 0
        self.failed_recoveries = 0
        self.best_strategy: Optional[ErrorRecoveryStrategy] = None
        self.first_seen = datetime.utcnow()
        self.last_seen = datetime.utcnow()
    
    def record_occurrence(self):
        """Record another occurrence of this error"""
        self.occurrences += 1
        self.last_seen = datetime.utcnow()
    
    def record_recovery(self, success: bool, strategy: ErrorRecoveryStrategy):
        """Record recovery attempt"""
        if success:
            self.successful_recoveries += 1
            # Update best strategy if this one is working well
            if self.best_strategy is None or strategy == self.best_strategy:
                self.best_strategy = strategy
        else:
            self.failed_recoveries += 1
    
    def get_success_rate(self) -> float:
        """Calculate recovery success rate"""
        total_attempts = self.successful_recoveries + self.failed_recoveries
        if total_attempts == 0:
            return 0.0
        return self.successful_recoveries / total_attempts


class ErrorRecoveryEngine:
    """Engine for detecting and recovering from errors"""
    
    def __init__(self):
        self.error_patterns: Dict[str, ErrorPattern] = {}
        self.recovery_history: List[Dict[str, Any]] = []
        self.max_retries = 3
    
    def detect_error(self, response: Any, expected_type: Optional[type] = None) -> Optional[ErrorType]:
        """Detect if response contains an error"""
        
        # Check for None or empty response
        if response is None or (isinstance(response, str) and not response.strip()):
            return ErrorType.INCOMPLETE_OUTPUT
        
        if not isinstance(response, str):
            # Check type validation for non-string types
            if expected_type and not isinstance(response, expected_type):
                return ErrorType.VALIDATION_ERROR
            return None
        
        # For string responses, check for valid JSON first
        # If it's valid JSON with good structure, it's likely not an error
        if '{' in response or '[' in response:
            # Check for incomplete JSON (unbalanced brackets)
            if response.count('{') != response.count('}'):
                return ErrorType.MALFORMED_RESPONSE
            if response.count('[') != response.count(']'):
                return ErrorType.MALFORMED_RESPONSE
            
            # Try to parse JSON
            try:
                parsed = json.loads(response)
                
                # If it's valid JSON with expected structure, it's good
                # Check for common success patterns
                if isinstance(parsed, dict):
                    # Has substantive content (not an error object)
                    if any(key in parsed for key in ['ideas', 'idea_name', 'problem_statement', 
                                                       'solution_overview', 'title', 'name', 'content']):
                        return None  # Valid content
                    
                    # Check for actual error objects
                    if 'error' in parsed and isinstance(parsed.get('error'), str):
                        if len(parsed.keys()) <= 2:  # Simple error object
                            return ErrorType.API_ERROR
                
                elif isinstance(parsed, list) and len(parsed) > 0:
                    # Valid list with content
                    return None
                
                # Valid JSON parsed successfully
                return None
                
            except json.JSONDecodeError as e:
                # Only flag as JSON error if it looks like it was trying to be JSON
                # (starts with { or [, has substantial length)
                stripped = response.strip()
                if (stripped.startswith('{') or stripped.startswith('[')) and len(stripped) > 20:
                    return ErrorType.JSON_PARSE_ERROR
                # Otherwise might be markdown or other format - let it pass
        
        # Check for API error indicators - but only at the start of response
        # This avoids false positives from content that mentions errors
        response_start = response[:200].lower()  # Only check first 200 chars
        
        # Very specific API error patterns (not just the word "error" anywhere)
        specific_error_patterns = [
            "error:", "error code", "error message", "api error",
            "exception:", "exception occurred",
            "failed to", "request failed",
            "timeout:", "request timeout", "read timeout",
            "rate limit exceeded", "quota exceeded",
            "invalid request", "invalid api", "authentication failed",
            "internal server error", "service unavailable"
        ]
        
        if any(pattern in response_start for pattern in specific_error_patterns):
            return ErrorType.API_ERROR
        
        # Check type validation
        if expected_type and not isinstance(response, expected_type):
            return ErrorType.VALIDATION_ERROR
        
        return None
    
    def analyze_error(self, error: Exception, response: Any) -> ErrorType:
        """Analyze exception to determine error type"""
        
        error_str = str(error).lower()
        
        if "json" in error_str or "parse" in error_str:
            return ErrorType.JSON_PARSE_ERROR
        elif "timeout" in error_str or "read timeout" in error_str:
            return ErrorType.LLM_TIMEOUT
        elif "validation" in error_str or "invalid" in error_str:
            return ErrorType.VALIDATION_ERROR
        elif "unterminated" in error_str or "malformed" in error_str:
            return ErrorType.MALFORMED_RESPONSE
        elif "incomplete" in error_str:
            return ErrorType.INCOMPLETE_OUTPUT
        else:
            return ErrorType.LOGIC_ERROR
    
    def get_recovery_strategy(self, error_type: ErrorType, error_key: str) -> ErrorRecoveryStrategy:
        """Determine best recovery strategy based on error type and history"""
        
        # Check if we have historical data for this error
        if error_key in self.error_patterns:
            pattern = self.error_patterns[error_key]
            if pattern.best_strategy and pattern.get_success_rate() > 0.5:
                return pattern.best_strategy
        
        # Default strategies based on error type
        strategy_map = {
            ErrorType.JSON_PARSE_ERROR: ErrorRecoveryStrategy.RETRY_STRUCTURED,
            ErrorType.VALIDATION_ERROR: ErrorRecoveryStrategy.RETRY_WITH_EXAMPLES,
            ErrorType.LLM_TIMEOUT: ErrorRecoveryStrategy.RETRY_SIMPLIFIED,
            ErrorType.INCOMPLETE_OUTPUT: ErrorRecoveryStrategy.RETRY_SAME,
            ErrorType.MALFORMED_RESPONSE: ErrorRecoveryStrategy.RETRY_STRUCTURED,
            ErrorType.LOGIC_ERROR: ErrorRecoveryStrategy.RETRY_SIMPLIFIED,
            ErrorType.API_ERROR: ErrorRecoveryStrategy.RETRY_SAME,
        }
        
        return strategy_map.get(error_type, ErrorRecoveryStrategy.RETRY_SAME)
    
    def build_recovery_prompt(self, original_prompt: str, error_type: ErrorType, 
                             strategy: ErrorRecoveryStrategy, error_details: str) -> str:
        """Build improved prompt based on error and strategy"""
        
        recovery_instructions = {
            ErrorRecoveryStrategy.RETRY_SIMPLIFIED: 
                "\n\n**IMPORTANT**: Previous attempt had issues. Please simplify your response. "
                "Focus on the most critical information only. Keep it concise.",
            
            ErrorRecoveryStrategy.RETRY_WITH_EXAMPLES:
                "\n\n**IMPORTANT**: Previous response had validation errors. "
                "Here's an example of the correct format:\n"
                "```json\n{\n  \"field1\": \"value1\",\n  \"field2\": \"value2\"\n}\n```\n"
                "Please follow this structure exactly.",
            
            ErrorRecoveryStrategy.RETRY_STRUCTURED:
                "\n\n**CRITICAL**: Previous response had formatting issues. "
                "You MUST output ONLY valid JSON. No explanatory text before or after. "
                "Ensure all strings are properly quoted and all brackets are balanced. "
                "Double-check your JSON before responding.",
            
            ErrorRecoveryStrategy.RETRY_SAME:
                "\n\n**NOTE**: Previous attempt encountered an issue. "
                "Please try again with extra care for accuracy and completeness."
        }
        
        instruction = recovery_instructions.get(strategy, "")
        
        # Add specific error context
        if error_type == ErrorType.JSON_PARSE_ERROR:
            instruction += "\n\n**JSON ERROR DETECTED**: Ensure valid JSON syntax. " \
                         "Common issues: missing quotes, trailing commas, unescaped characters."
        elif error_type == ErrorType.INCOMPLETE_OUTPUT:
            instruction += "\n\n**INCOMPLETE OUTPUT**: Previous response was cut off. " \
                         "Ensure you complete the entire response."
        elif error_type == ErrorType.LLM_TIMEOUT:
            instruction += "\n\n**TIMEOUT**: Previous response took too long. " \
                         "Be more concise while maintaining quality."
        
        return original_prompt + instruction
    
    def record_error(self, error_type: ErrorType, error_message: str):
        """Record error occurrence for learning"""
        error_key = f"{error_type.value}:{error_message[:100]}"
        
        if error_key in self.error_patterns:
            self.error_patterns[error_key].record_occurrence()
        else:
            self.error_patterns[error_key] = ErrorPattern(error_type, error_message)
    
    def record_recovery_attempt(self, error_type: ErrorType, error_message: str, 
                               strategy: ErrorRecoveryStrategy, success: bool):
        """Record recovery attempt outcome"""
        error_key = f"{error_type.value}:{error_message[:100]}"
        
        if error_key in self.error_patterns:
            self.error_patterns[error_key].record_recovery(success, strategy)
        
        # Store in history
        self.recovery_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'error_type': error_type.value,
            'strategy': strategy.value,
            'success': success
        })
    
    def attempt_recovery(self, 
                        original_function: Callable,
                        original_args: tuple,
                        original_kwargs: dict,
                        error: Exception,
                        response: Any,
                        attempt_number: int) -> Any:
        """Attempt to recover from error by retrying with improved approach"""
        
        # Determine error type
        error_type = self.analyze_error(error, response)
        error_message = str(error)
        
        # Record error
        self.record_error(error_type, error_message)
        
        # Check if we should give up
        if attempt_number >= self.max_retries:
            print(f"      ⚠️  Max retries ({self.max_retries}) reached. Using fallback.")
            return None
        
        # Get recovery strategy
        error_key = f"{error_type.value}:{error_message[:100]}"
        strategy = self.get_recovery_strategy(error_type, error_key)
        
        print(f"      🔧 Error detected: {error_type.value} (attempt {attempt_number}/{self.max_retries})")
        print(f"      🔄 Recovery strategy: {strategy.value}")
        
        # Modify arguments based on strategy
        modified_kwargs = original_kwargs.copy()
        
        # If there's a prompt argument, enhance it
        if 'prompt' in modified_kwargs:
            modified_kwargs['prompt'] = self.build_recovery_prompt(
                modified_kwargs['prompt'], 
                error_type, 
                strategy, 
                error_message
            )
        
        # Adjust parameters based on strategy
        if strategy == ErrorRecoveryStrategy.RETRY_SIMPLIFIED:
            if 'max_tokens' in modified_kwargs:
                modified_kwargs['max_tokens'] = min(
                    modified_kwargs['max_tokens'], 
                    modified_kwargs['max_tokens'] // 2
                )
            if 'temperature' in modified_kwargs:
                modified_kwargs['temperature'] = max(
                    0.3, 
                    modified_kwargs['temperature'] - 0.2
                )
        
        # Retry the function
        try:
            result = original_function(*original_args, **modified_kwargs)
            
            # Verify recovery was successful
            if self.detect_error(result) is None:
                print(f"      ✅ Recovery successful using {strategy.value}")
                self.record_recovery_attempt(error_type, error_message, strategy, True)
                return result
            else:
                print(f"      ⚠️  Recovery attempt produced another error")
                self.record_recovery_attempt(error_type, error_message, strategy, False)
                return None
                
        except Exception as retry_error:
            print(f"      ⚠️  Recovery attempt failed: {str(retry_error)[:100]}")
            self.record_recovery_attempt(error_type, error_message, strategy, False)
            return None
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get statistics about errors and recoveries"""
        total_errors = len(self.error_patterns)
        total_recoveries = sum(p.successful_recoveries for p in self.error_patterns.values())
        total_failures = sum(p.failed_recoveries for p in self.error_patterns.values())
        
        error_type_counts = {}
        for pattern in self.error_patterns.values():
            error_type = pattern.error_type.value
            error_type_counts[error_type] = error_type_counts.get(error_type, 0) + pattern.occurrences
        
        return {
            'total_unique_errors': total_errors,
            'total_recovery_attempts': total_recoveries + total_failures,
            'successful_recoveries': total_recoveries,
            'failed_recoveries': total_failures,
            'recovery_success_rate': total_recoveries / (total_recoveries + total_failures) 
                                    if (total_recoveries + total_failures) > 0 else 0,
            'error_type_distribution': error_type_counts,
            'most_common_errors': sorted(
                [(k, v.occurrences) for k, v in self.error_patterns.items()],
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
    
    def save_error_patterns(self, filepath: str):
        """Save learned error patterns to file"""
        data = {
            'patterns': {
                key: {
                    'error_type': pattern.error_type.value,
                    'occurrences': pattern.occurrences,
                    'successful_recoveries': pattern.successful_recoveries,
                    'failed_recoveries': pattern.failed_recoveries,
                    'best_strategy': pattern.best_strategy.value if pattern.best_strategy else None,
                    'success_rate': pattern.get_success_rate()
                }
                for key, pattern in self.error_patterns.items()
            },
            'statistics': self.get_error_statistics()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


# Global error recovery engine
_error_recovery_engine = None


def get_error_recovery_engine() -> ErrorRecoveryEngine:
    """Get global error recovery engine (singleton)"""
    global _error_recovery_engine
    if _error_recovery_engine is None:
        _error_recovery_engine = ErrorRecoveryEngine()
    return _error_recovery_engine

