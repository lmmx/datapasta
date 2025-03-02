"""Type inference for column data."""

import re
from datetime import datetime
from typing import Any, Literal

# Define a type for our column types
ColumnType = Literal["int", "float", "bool", "datetime", "str"]


def infer_type(values: list[str | None]) -> ColumnType:
    """Infer the type of a column from its values.

    Args:
        values: List of strings representing column values

    Returns:
        One of: 'int', 'float', 'bool', 'datetime', 'str'

    """
    # Remove None/NA values for type inference
    non_empty = [
        v
        for v in values
        if v is not None
        and v.strip()
        and v.lower() not in ("na", "n/a", "none", "null", "")
    ]

    if not non_empty:
        return "str"  # Default to string for empty columns

    # Check if all values are booleans
    bool_values = {"true", "false", "t", "f", "yes", "no", "y", "n", "1", "0"}
    if all(v.lower() in bool_values for v in non_empty):
        return "bool"

    # Check if all values are integers
    if all(v.strip().lstrip("-+").isdigit() for v in non_empty):
        return "int"

    # Check if all values are floats
    float_pattern = re.compile(r"^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$")
    if all(float_pattern.match(v.strip()) for v in non_empty):
        return "float"

    # Check for datetime formats
    date_formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
    ]

    date_count = 0
    for value in non_empty:
        is_date = False
        for fmt in date_formats:
            try:
                datetime.strptime(value, fmt)
                is_date = True
                break
            except ValueError:
                continue
        if is_date:
            date_count += 1

    # If more than 80% of non-empty values are dates, consider it a datetime column
    if date_count / len(non_empty) > 0.8:
        return "datetime"

    # Default to string
    return "str"


def infer_types_for_table(parsed_table: dict[str, Any]) -> list[ColumnType]:
    """Infer types for all columns in a parsed table.

    Args:
        parsed_table: Dict with 'headers' and 'data' from parse_table

    Returns:
        List of column type strings in the same order as headers

    """
    if not parsed_table["data"]:
        return ["str"] * len(parsed_table["headers"])

    types = []
    for col_idx in range(len(parsed_table["headers"])):
        # Extract all values for this column
        col_values = []
        for row in parsed_table["data"]:
            if col_idx < len(row):
                col_values.append(row[col_idx])
            else:
                col_values.append(None)

        col_type = infer_type(col_values)
        types.append(col_type)

    return types
