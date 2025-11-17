"""
Input validation utilities for enterprise security
"""
import re
from typing import Optional, Tuple

class ValidationError(Exception):
    """Validation error exception"""
    pass


class InputValidator:
    """Validate and sanitize user inputs"""
    
    # Maximum lengths to prevent abuse
    MAX_MESSAGE_LENGTH = 5000
    MAX_SESSION_ID_LENGTH = 100
    
    # Allowed user modes
    VALID_USER_MODES = {'patient', 'doctor', 'researcher'}
    
    # UUID pattern
    UUID_PATTERN = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    
    @staticmethod
    def validate_message(message: str) -> Tuple[bool, Optional[str]]:
        """
        Validate user message
        
        Returns:
            (is_valid, error_message)
        """
        if not message:
            return False, "Message cannot be empty"
        
        if not isinstance(message, str):
            return False, "Message must be a string"
        
        if len(message) > InputValidator.MAX_MESSAGE_LENGTH:
            return False, f"Message exceeds maximum length of {InputValidator.MAX_MESSAGE_LENGTH} characters"
        
        # Check for potential injection attempts
        if InputValidator._contains_suspicious_patterns(message):
            return False, "Message contains suspicious patterns"
        
        return True, None
    
    @staticmethod
    def validate_session_id(session_id: str) -> Tuple[bool, Optional[str]]:
        """
        Validate session ID format
        
        Returns:
            (is_valid, error_message)
        """
        if not session_id:
            return False, "Session ID cannot be empty"
        
        if len(session_id) > InputValidator.MAX_SESSION_ID_LENGTH:
            return False, "Session ID is too long"
        
        # Check if it's a valid UUID
        if not InputValidator.UUID_PATTERN.match(session_id):
            return False, "Invalid session ID format"
        
        return True, None
    
    @staticmethod
    def validate_user_mode(user_mode: str) -> Tuple[bool, Optional[str]]:
        """
        Validate user mode
        
        Returns:
            (is_valid, error_message)
        """
        if not user_mode:
            return False, "User mode cannot be empty"
        
        if user_mode not in InputValidator.VALID_USER_MODES:
            return False, f"Invalid user mode. Must be one of: {', '.join(InputValidator.VALID_USER_MODES)}"
        
        return True, None
    
    @staticmethod
    def validate_conversation_history(history: list) -> Tuple[bool, Optional[str]]:
        """
        Validate conversation history structure
        
        Returns:
            (is_valid, error_message)
        """
        if not isinstance(history, list):
            return False, "Conversation history must be a list"
        
        # Limit history length
        if len(history) > 100:
            return False, "Conversation history too long"
        
        # Validate each message in history
        for msg in history:
            if not isinstance(msg, dict):
                return False, "Each message must be a dictionary"
            
            if 'role' not in msg or 'content' not in msg:
                return False, "Each message must have 'role' and 'content' fields"
            
            if msg['role'] not in {'user', 'assistant', 'system'}:
                return False, "Invalid message role"
            
            if not isinstance(msg['content'], str):
                return False, "Message content must be a string"
        
        return True, None
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """
        Remove HTML tags and potentially dangerous characters
        
        Args:
            text: Input text to sanitize
            
        Returns:
            Sanitized text
        """
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove JavaScript event handlers
        text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
        
        # Remove script tags content
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        return text.strip()
    
    @staticmethod
    def _contains_suspicious_patterns(text: str) -> bool:
        """
        Check for SQL injection and XSS patterns
        
        Args:
            text: Text to check
            
        Returns:
            True if suspicious patterns found
        """
        suspicious_patterns = [
            r'<script[^>]*>',
            r'javascript:',
            r'on\w+\s*=',
            r'DROP\s+TABLE',
            r'DELETE\s+FROM',
            r'INSERT\s+INTO',
            r'UPDATE\s+\w+\s+SET',
            r'--\s*$',
            r';.*--',
        ]
        
        text_lower = text.lower()
        
        for pattern in suspicious_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        
        return False


# Global validator instance
validator = InputValidator()
