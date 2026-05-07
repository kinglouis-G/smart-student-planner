from __future__ import annotations

"""
Validation helpers for Smart Student Planner.

This module contains simple, reusable validation functions for user
inputs such as task titles and dates.
"""

from datetime import datetime
from typing import Tuple


def validate_non_empty(value: str, field_name: str) -> Tuple[bool, str]:
    """
    Ensure that a string value is not empty or whitespace.

    Args:
        value: The input string.
        field_name: Friendly name of the field (for error messages).

    Returns:
        Tuple (is_valid, error_message). error_message is empty if valid.
    """
    if not value or not value.strip():
        return False, f"{field_name} cannot be empty."
    return True, ""


def validate_date(value: str) -> Tuple[bool, str]:
    """
    Validate that a date string is in the format YYYY-MM-DD.

    Args:
        value: Date string from user input.

    Returns:
        Tuple (is_valid, error_message).
    """
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True, ""
    except ValueError:
        return False, "Date must be in format YYYY-MM-DD."


def validate_priority(value: str) -> Tuple[bool, str]:
    """
    Validate that the priority is one of the expected values.

    Args:
        value: Priority string.

    Returns:
        Tuple (is_valid, error_message).
    """
    allowed = {"Low", "Medium", "High"}
    if value not in allowed:
        return False, "Priority must be Low, Medium, or High."
    return True, ""

