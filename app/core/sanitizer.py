# ============================================
# AGTR v6.0 - XSS Protection & Content Sanitizer
# Dosya: app/core/sanitizer.py
# ============================================
"""
HTML Sanitization module for preventing XSS attacks in forum content.
Allows safe HTML tags while removing potentially dangerous content.
"""

import re
import html
from typing import Dict, List, Set
import logging

logger = logging.getLogger(__name__)

# Allowed HTML tags for forum content
ALLOWED_TAGS: Set[str] = {
    'p', 'br', 'b', 'i', 'u', 'strong', 'em', 'a',
    'ul', 'ol', 'li', 'code', 'pre', 'blockquote',
    'h1', 'h2', 'h3', 'img', 'span', 'div'
}

# Allowed attributes per tag
ALLOWED_ATTRS: Dict[str, List[str]] = {
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'width', 'height', 'title'],
    'span': ['class'],
    'div': ['class'],
    'pre': ['class'],
    'code': ['class']
}

# Dangerous patterns to remove
DANGEROUS_PATTERNS = [
    # JavaScript protocol
    re.compile(r'javascript\s*:', re.IGNORECASE),
    # VBScript protocol
    re.compile(r'vbscript\s*:', re.IGNORECASE),
    # Data protocol (can execute scripts)
    re.compile(r'data\s*:\s*text/html', re.IGNORECASE),
    # Expression (IE specific CSS expression)
    re.compile(r'expression\s*\(', re.IGNORECASE),
    # On* event handlers
    re.compile(r'\bon\w+\s*=', re.IGNORECASE),
]

# Pattern for matching HTML tags
TAG_PATTERN = re.compile(r'<(/?)(\w+)([^>]*)(/?)>', re.IGNORECASE | re.DOTALL)

# Pattern for matching attributes
ATTR_PATTERN = re.compile(r'(\w+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s>]*))', re.IGNORECASE)


def remove_dangerous_patterns(content: str) -> str:
    """Remove dangerous patterns like javascript:, on* handlers, etc."""
    for pattern in DANGEROUS_PATTERNS:
        content = pattern.sub('', content)
    return content


def sanitize_url(url: str) -> str:
    """
    Sanitize URL - only allow safe protocols.
    Returns empty string if URL is potentially dangerous.
    """
    if not url:
        return ''

    url = url.strip()

    # Decode HTML entities
    url = html.unescape(url)

    # Check for dangerous protocols
    lower_url = url.lower().strip()

    # Allow only safe protocols
    safe_protocols = ['http://', 'https://', '//', '/', '#', 'mailto:']

    # Check if starts with safe protocol or is relative
    is_safe = False
    for proto in safe_protocols:
        if lower_url.startswith(proto):
            is_safe = True
            break

    # Also allow relative URLs without protocol
    if not is_safe and not ':' in url.split('/')[0]:
        is_safe = True

    if not is_safe:
        logger.warning(f"Blocked potentially dangerous URL: {url[:100]}")
        return ''

    # Additional check for javascript in URL
    if 'javascript' in lower_url or 'vbscript' in lower_url:
        logger.warning(f"Blocked script URL: {url[:100]}")
        return ''

    return url


def sanitize_attribute_value(attr_name: str, attr_value: str, tag_name: str) -> str:
    """Sanitize individual attribute value based on context."""
    if not attr_value:
        return ''

    # Decode HTML entities first
    attr_value = html.unescape(attr_value)

    # Remove dangerous patterns
    attr_value = remove_dangerous_patterns(attr_value)

    # Special handling for href and src
    if attr_name in ('href', 'src'):
        attr_value = sanitize_url(attr_value)

    # Escape quotes in the value
    attr_value = attr_value.replace('"', '&quot;')

    return attr_value


def sanitize_tag(match: re.Match) -> str:
    """Process and sanitize a single HTML tag."""
    closing_slash = match.group(1)
    tag_name = match.group(2).lower()
    attributes_str = match.group(3)
    self_closing = match.group(4)

    # If tag is not allowed, escape it
    if tag_name not in ALLOWED_TAGS:
        return html.escape(match.group(0))

    # For closing tags, just return the clean closing tag
    if closing_slash:
        return f'</{tag_name}>'

    # Parse and sanitize attributes
    allowed_attrs_for_tag = ALLOWED_ATTRS.get(tag_name, [])
    safe_attrs = []

    if attributes_str:
        for attr_match in ATTR_PATTERN.finditer(attributes_str):
            attr_name = attr_match.group(1).lower()
            attr_value = attr_match.group(2) or attr_match.group(3) or attr_match.group(4) or ''

            # Only include allowed attributes
            if attr_name in allowed_attrs_for_tag:
                # Skip if attribute name looks like event handler
                if attr_name.startswith('on'):
                    continue

                sanitized_value = sanitize_attribute_value(attr_name, attr_value, tag_name)

                # Skip empty href/src
                if attr_name in ('href', 'src') and not sanitized_value:
                    continue

                safe_attrs.append(f'{attr_name}="{sanitized_value}"')

    # For <a> tags, add rel="noopener noreferrer" and target="_blank" for external links
    if tag_name == 'a':
        has_target = any(a.startswith('target=') for a in safe_attrs)
        has_rel = any(a.startswith('rel=') for a in safe_attrs)

        if not has_rel:
            safe_attrs.append('rel="noopener noreferrer"')

    # Build the tag
    if safe_attrs:
        attrs_str = ' ' + ' '.join(safe_attrs)
    else:
        attrs_str = ''

    if self_closing or tag_name in ('br', 'img', 'hr'):
        return f'<{tag_name}{attrs_str} />'
    else:
        return f'<{tag_name}{attrs_str}>'


def sanitize_html(content: str) -> str:
    """
    Sanitize HTML content while preserving allowed safe tags.

    Process:
    1. Remove dangerous patterns (javascript:, on* handlers, etc.)
    2. Process each HTML tag - allow only safe tags with safe attributes
    3. Escape any remaining dangerous content

    Args:
        content: Raw HTML content to sanitize

    Returns:
        Sanitized HTML safe for display
    """
    if not content:
        return ''

    # First pass: Remove dangerous patterns from raw content
    content = remove_dangerous_patterns(content)

    # Second pass: Process each HTML tag
    content = TAG_PATTERN.sub(sanitize_tag, content)

    # Third pass: Final cleanup - remove any remaining dangerous patterns
    content = remove_dangerous_patterns(content)

    return content


def strip_all_html(content: str) -> str:
    """
    Remove ALL HTML tags, returning plain text.
    Useful for preview text, notifications, etc.
    """
    if not content:
        return ''

    # Remove HTML tags
    content = re.sub(r'<[^>]+>', '', content)

    # Decode HTML entities
    content = html.unescape(content)

    # Clean up whitespace
    content = re.sub(r'\s+', ' ', content).strip()

    return content


def sanitize_forum_content(content: str) -> str:
    """
    Sanitize forum post/reply content.
    Allows markdown-style formatting but sanitizes HTML.

    This is the main function to use for forum topic and reply content.

    Args:
        content: Raw forum content (may contain HTML/markdown)

    Returns:
        Sanitized content safe for storage and display
    """
    if not content:
        return ''

    # Sanitize HTML
    content = sanitize_html(content)

    # Normalize line endings
    content = content.replace('\r\n', '\n').replace('\r', '\n')

    # Limit consecutive newlines to 3 max
    content = re.sub(r'\n{4,}', '\n\n\n', content)

    return content.strip()


def sanitize_username(username: str) -> str:
    """
    Sanitize username - remove any HTML/special characters.
    Usernames should be plain text only.
    """
    if not username:
        return ''

    # Strip HTML
    username = strip_all_html(username)

    # Remove any remaining non-alphanumeric (except underscore, dash)
    username = re.sub(r'[^\w\-_]', '', username, flags=re.UNICODE)

    return username[:50]  # Limit length


def sanitize_title(title: str) -> str:
    """
    Sanitize forum topic title.
    Titles should be plain text - no HTML allowed.
    """
    if not title:
        return ''

    # Strip all HTML
    title = strip_all_html(title)

    # Remove control characters
    title = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', title)

    return title.strip()[:200]  # Limit length


# ==================== VALIDATION HELPERS ====================

def is_content_safe(content: str) -> bool:
    """
    Quick check if content appears safe.
    Returns False if any dangerous patterns detected.
    """
    if not content:
        return True

    for pattern in DANGEROUS_PATTERNS:
        if pattern.search(content):
            return False

    return True


def get_content_warnings(content: str) -> List[str]:
    """
    Check content and return list of potential security warnings.
    Useful for admin review or logging.
    """
    warnings = []

    if not content:
        return warnings

    # Check for script-like content
    if re.search(r'<script', content, re.IGNORECASE):
        warnings.append('Contains <script> tag')

    # Check for event handlers
    if re.search(r'\bon\w+\s*=', content, re.IGNORECASE):
        warnings.append('Contains event handler attribute')

    # Check for javascript: protocol
    if re.search(r'javascript\s*:', content, re.IGNORECASE):
        warnings.append('Contains javascript: protocol')

    # Check for data: protocol
    if re.search(r'data\s*:', content, re.IGNORECASE):
        warnings.append('Contains data: protocol')

    # Check for iframe
    if re.search(r'<iframe', content, re.IGNORECASE):
        warnings.append('Contains <iframe> tag')

    # Check for object/embed
    if re.search(r'<(object|embed)', content, re.IGNORECASE):
        warnings.append('Contains <object> or <embed> tag')

    return warnings


# ==================== EXPORTS ====================

__all__ = [
    'sanitize_html',
    'sanitize_forum_content',
    'sanitize_title',
    'sanitize_username',
    'strip_all_html',
    'is_content_safe',
    'get_content_warnings',
    'ALLOWED_TAGS',
    'ALLOWED_ATTRS'
]
