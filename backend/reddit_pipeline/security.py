"""Security utilities for PII stripping and data sanitization."""

import re
from typing import Any


def strip_pii_from_text(text: str) -> str:
    """Strip PII (emails, phones) from text content.
    
    Args:
        text: Input text that may contain PII
        
    Returns:
        Text with PII replaced by placeholders
    """
    if not text:
        return text
    
    # Email pattern - matches common email formats including Unicode
    email_pattern = r'\b[\w._%+-]+@[\w.-]+\.[A-Za-z]{2,}\b'
    text = re.sub(email_pattern, '[EMAIL_REDACTED]', text)
    
    # Phone pattern - matches various phone number formats
    phone_patterns = [
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 123-456-7890, 123.456.7890, 1234567890
        r'\(\d{3}\)\s*\d{3}[-.]?\d{4}\b',  # (123) 456-7890, (123)456-7890
        r'\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b',  # International
        r'\b\d{10,15}\b',  # Long digit sequences (potential phone numbers)
    ]
    
    for pattern in phone_patterns:
        text = re.sub(pattern, '[PHONE_REDACTED]', text)
    
    return text


def strip_pii_from_comment(comment: dict[str, Any]) -> dict[str, Any]:
    """Strip PII from a comment dictionary.
    
    Args:
        comment: Comment dictionary with potential PII
        
    Returns:
        Comment dictionary with PII stripped from text fields
    """
    if not isinstance(comment, dict):
        return comment
    
    # Create a copy to avoid modifying original
    cleaned_comment = comment.copy()
    
    # Strip PII from text fields
    text_fields = ['body', 'text', 'content', 'message']
    for field in text_fields:
        if field in cleaned_comment and isinstance(cleaned_comment[field], str):
            cleaned_comment[field] = strip_pii_from_text(cleaned_comment[field])
    
    return cleaned_comment


def strip_pii_from_comments(comments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Strip PII from a list of comments.
    
    Args:
        comments: List of comment dictionaries
        
    Returns:
        List of comment dictionaries with PII stripped
    """
    if not isinstance(comments, list):
        return comments
    
    return [strip_pii_from_comment(comment) for comment in comments]


def strip_pii_from_post(post: dict[str, Any]) -> dict[str, Any]:
    """Strip PII from a post dictionary.
    
    Args:
        post: Post dictionary with potential PII
        
    Returns:
        Post dictionary with PII stripped from text fields
    """
    if not isinstance(post, dict):
        return post
    
    # Create a copy to avoid modifying original
    cleaned_post = post.copy()
    
    # Strip PII from text fields
    text_fields = ['title', 'text', 'selftext', 'content', 'description', 'body']
    for field in text_fields:
        if field in cleaned_post and isinstance(cleaned_post[field], str):
            cleaned_post[field] = strip_pii_from_text(cleaned_post[field])
    
    return cleaned_post


def sanitize_for_display(data: Any) -> Any:
    """Sanitize data for external display by stripping PII.
    
    Args:
        data: Data structure that may contain PII
        
    Returns:
        Sanitized data structure with PII stripped
    """
    if isinstance(data, str):
        return strip_pii_from_text(data)
    elif isinstance(data, dict):
        return strip_pii_from_post(data)
    elif isinstance(data, list):
        return [sanitize_for_display(item) for item in data]
    else:
        return data


def validate_no_pii_remaining(text: str) -> bool:
    """Validate that no PII patterns remain in text.
    
    Args:
        text: Text to validate
        
    Returns:
        True if no PII patterns found, False otherwise
    """
    if not text:
        return True
    
    # Check for email patterns
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.search(email_pattern, text):
        return False
    
    # Check for phone patterns
    phone_patterns = [
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        r'\(\d{3}\)\s*\d{3}[-.]?\d{4}\b',
        r'\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b',
        r'\b\d{10,15}\b',
    ]
    
    for pattern in phone_patterns:
        if re.search(pattern, text):
            return False
    
    return True
