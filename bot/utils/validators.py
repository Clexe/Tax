"""
Input validation utilities for NaijaTax Bot.

parse_amount() is the single entry point for all monetary user inputs.
"""

from __future__ import annotations
import re
import math

# Maximum plausible monthly income (₦1 billion)
MAX_AMOUNT = 1_000_000_000


def parse_amount(text: str | None) -> int | None:
    """
    Parse a user-entered monetary amount and return it as an integer (Naira).

    Accepted formats:
        "150000"    → 150000
        "150,000"   → 150000
        "150k"      → 150000
        "150K"      → 150000
        "1.5m"      → 1500000
        "1.5M"      → 1500000
        "₦150,000"  → 150000
        "₦1.5m"     → 1500000
        "0"         → 0
        "150000.99" → 150000  (floor to integer)

    Returns None for:
        - Empty or whitespace-only strings
        - None input
        - Negative values
        - Non-numeric strings
        - Amounts over ₦1,000,000,000

    Args:
        text: The raw string from the user's Telegram message.

    Returns:
        Integer value in Naira, or None if the input is invalid.
    """
    if text is None:
        return None
    if not text.strip():
        return None

    # Strip currency symbol and whitespace, remove commas
    cleaned = text.strip().replace("₦", "").replace(",", "").strip()

    # Match: optional digits, optional decimal part, optional k/m suffix
    # Anchored with ^ and $ via fullmatch to reject partial matches
    pattern = re.compile(r"^(\d+(?:\.\d+)?)([km]?)$", re.IGNORECASE)
    match = pattern.fullmatch(cleaned)
    if not match:
        return None

    number_str = match.group(1)
    suffix = match.group(2).lower()

    try:
        value = float(number_str)
    except ValueError:
        return None

    if suffix == "k":
        value *= 1_000
    elif suffix == "m":
        value *= 1_000_000

    # Floor to integer (drop kobo)
    result = math.floor(value)

    if result < 0:
        return None

    if result > MAX_AMOUNT:
        return None

    return result
