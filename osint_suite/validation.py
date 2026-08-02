"""Input validation and safe presentation helpers for the local application."""

from __future__ import annotations

import html
import re
from urllib.parse import urlparse


EMAIL_PATTERN = re.compile(r"[^\s@]+@[^\s@]+\.[^\s@]+")
IP_PATTERN = re.compile(r"[0-9A-Fa-f:.]+")
MAX_TARGET_LENGTH = 240


def escape(value: object) -> str:
    """Escape dynamic content before placing it in an HTML block."""
    return html.escape(str(value), quote=True)


def clean_target(value: str) -> str:
    """Normalize whitespace and reject control characters in public-search input."""
    cleaned = " ".join(value.strip().split())
    if not cleaned:
        return ""
    if len(cleaned) > MAX_TARGET_LENGTH:
        raise ValueError(f"Target values must be {MAX_TARGET_LENGTH} characters or fewer.")
    if any(ord(character) < 32 for character in cleaned):
        raise ValueError("Target values cannot contain control characters.")
    return cleaned


def validate_typed_target(target_type: str, value: str) -> str:
    """Lightweight client-side validation without contacting any service."""
    cleaned = clean_target(value)
    if not cleaned:
        return cleaned
    if target_type == "email" and not EMAIL_PATTERN.fullmatch(cleaned):
        raise ValueError("Enter a valid email address.")
    if target_type == "ip_address" and not IP_PATTERN.fullmatch(cleaned):
        raise ValueError("Enter a valid IPv4 or IPv6 address.")
    if target_type in {"domain", "website"}:
        candidate = cleaned if "://" in cleaned else f"https://{cleaned}"
        if not urlparse(candidate).netloc:
            raise ValueError("Enter a valid domain or website.")
    return cleaned
