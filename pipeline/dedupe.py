"""Deduplication and content hashing module."""

import hashlib
from typing import Tuple


def generate_content_hash(employer: str, title: str, location: str) -> str:
    """Generate stable unique hash for deduplication based on (employer, title, location)."""
    raw_str = f"{(employer or '').lower().strip()}|{(title or '').lower().strip()}|{(location or '').lower().strip()}"
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()
