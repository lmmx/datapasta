"""Utility functions for datapasta."""

import re
from collections import Counter
from typing import Any


def clean_column_name(name: str) -> str:
    """Clean a column name to make it a valid Python identifier.

    Args:
        name (str): Original column name

    Returns:
        str: Cleaned column name

    """
    # Replace non-alphanumeric chars with underscores
    clean_name = re.sub(r"[^\w]", "_", str(name).strip())

    # Ensure it doesn't start with a digit
    if clean_name and clean_name[0].isdigit():
        clean_name = "col_" + clean_name

    # Remove multiple consecutive underscores
    clean_name = re.sub(r"_+", "_", clean_name)

    # Remove trailing underscore
    clean_name = clean_name.rstrip("_")

    # If empty, use default
    if not clean_name:
        clean_name = "unnamed_col"

    return clean_name


def is_integer(s: str) -> bool:
    """Check if string can be converted to an integer."""
    try:
        int(s)
        return True
    except (ValueError, TypeError):
        return False


def is_float(s: str) -> bool:
    """Check if string can be converted to a float."""
    if isinstance(s, str) and s.strip().lower() in ("inf", "-inf", "nan"):
        return True

    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False


def is_boolean(s: str) -> bool:
    """Check if string represents a boolean value."""
    if isinstance(s, str):
        lower_s = s.strip().lower()
        return lower_s in ("true", "false", "yes", "no", "t", "f", "y", "n", "1", "0")
    return False


def is_date(s: str) -> bool:
    """Check if string can be parsed as a date."""
    if not isinstance(s, str):
        return False

    # Common date formats
    date_patterns = [
        r"^\d{4}-\d{2}-\d{2}$",  # YYYY-MM-DD
        r"^\d{1,2}/\d{1,2}/\d{4}$",  # MM/DD/YYYY
        r"^\d{1,2}/\d{1,2}/\d{2}$",  # MM/DD/YY
        r"^\d{1,2}-\d{1,2}-\d{4}$",  # DD-MM-YYYY
        r"^\d{4}/\d{1,2}/\d{1,2}$",  # YYYY/MM/DD
        r"^\d{1,2}\s+[a-zA-Z]{3,}\s+\d{4}$",  # DD Month YYYY
        r"^[a-zA-Z]{3,}\s+\d{1,2},\s+\d{4}$",  # Month DD, YYYY
    ]

    return any(re.match(pattern, s.strip()) for pattern in date_patterns)


def guess_column_types(values: list[str]) -> str:
    """Guess data type for a column of values.

    Args:
        values (list): List of string values

    Returns:
        str: One of 'integer', 'float', 'boolean', 'date', 'string'

    """
    # Remove empty/None values for type detection
    non_empty = [v for v in values if v and str(v).strip()]

    if not non_empty:
        return "string"  # Default for empty columns

    # Count how many values match each type
    type_counts = Counter()

    for val in non_empty:
        val_str = str(val).strip()

        if val_str.lower() in ("na", "n/a", "none", "null", ""):
            continue  # Skip NA values for type detection
        elif is_integer(val_str):
            type_counts["integer"] += 1
        elif is_float(val_str):
            type_counts["float"] += 1
        elif is_boolean(val_str):
            type_counts["boolean"] += 1
        elif is_date(val_str):
            type_counts["date"] += 1
        else:
            type_counts["string"] += 1

    # If every non-empty value is of the same type, use that type
    if len(type_counts) == 1:
        return list(type_counts.keys())[0]

    # If more than 90% of values are of one type, use that type
    most_common_type, most_common_count = type_counts.most_common(1)[0]
    if most_common_count / sum(type_counts.values()) > 0.9:
        return most_common_type

    # Handle mixed numeric types (int and float) - use float
    if set(type_counts.keys()).issubset({"integer", "float"}):
        return "float"

    # When in doubt, use string
    return "string"


def guess_has_header(rows: list[list[str]]) -> bool:
    """Determine if the first row is likely a header.

    Args:
        rows (list): List of data rows

    Returns:
        bool: True if first row is likely a header, False otherwise

    """
    if len(rows) < 2:
        return False  # Need at least 2 rows to determine

    # If there's only one row, assume it's data not header
    if len(rows) < 2:
        return False

    first_row = rows[0]
    second_row = rows[1]

    # First row has different types than the rest
    first_row_types = [guess_column_types([val]) for val in first_row]
    second_row_types = [guess_column_types([val]) for val in second_row]

    # If all types in first row are string and second row has non-strings,
    # first row is likely header
    if all(t == "string" for t in first_row_types) and any(
        t != "string" for t in second_row_types
    ):
        return True

    # If first row contains text that looks like column names
    # (no spaces, shorter than data)
    header_pattern = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
    if all(header_pattern.match(str(val)) for val in first_row):
        return True

    # If column names are shorter than average data
    if len(rows) > 2:
        avg_data_length = sum(len(str(cell)) for row in rows[1:] for cell in row) / (
            len(rows[1:]) * len(rows[0])
        )
        first_row_avg = sum(len(str(cell)) for cell in first_row) / len(first_row)

        if first_row_avg < avg_data_length * 0.6:
            return True

    return False


def format_value_for_code(val: Any, val_type: str) -> str:
    """Format a value for inclusion in Python code based on its type.

    Args:
        val: The value to format
        val_type: Type of the value ('integer', 'float', etc.)

    Returns:
        str: Formatted value ready for code inclusion

    """
    if val is None or (
        isinstance(val, str)
        and val.strip().lower() in ("na", "n/a", "none", "null", "")
    ):
        return "None"

    val_str = str(val).strip()

    if val_type == "integer":
        try:
            return str(int(val_str))
        except (ValueError, TypeError):
            return "None"

    elif val_type == "float":
        try:
            return str(float(val_str))
        except (ValueError, TypeError):
            return "None"

    elif val_type == "boolean":
        val_lower = val_str.lower()
        if val_lower in ("true", "yes", "y", "t", "1"):
            return "True"
        elif val_lower in ("false", "no", "n", "f", "0"):
            return "False"
        return "None"

    elif val_type == "date":
        # Simply quote the date string, let pandas/polars handle parsing
        return f'"{val_str}"'

    else:  # string and other types
        return f'"{val_str}"'
