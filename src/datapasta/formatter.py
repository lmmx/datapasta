"""Code generation for various DataFrame formats."""

from typing import Any

from .type_inference import ColumnType


def format_value(value: str | None, col_type: ColumnType) -> str:
    """Format a value according to its inferred type.

    Args:
        value: The string value to format
        col_type: The inferred type ('int', 'float', 'bool', 'datetime', 'str')

    Returns:
        A string representation suitable for Python code

    """
    if (
        value is None
        or value.strip() == ""
        or value.lower() in ("na", "n/a", "none", "null")
    ):
        return "None"

    if col_type == "int":
        return value.strip()

    elif col_type == "float":
        return value.strip()

    elif col_type == "bool":
        value = value.lower().strip()
        if value in ("true", "t", "yes", "y", "1"):
            return "True"
        else:
            return "False"

    elif col_type == "datetime":
        # Return as string for now, we'll let pandas/polars parse it
        return repr(value)

    else:  # Default to string
        return repr(value)


def generate_pandas_code(parsed_table: dict[str, Any], types: list[ColumnType]) -> str:
    """Generate pandas DataFrame creation code.

    Args:
        parsed_table: Dict with 'headers' and 'data' from parse_table
        types: List of type strings for each column

    Returns:
        Python code string to create a pandas DataFrame

    """
    headers = parsed_table["headers"]
    data = parsed_table["data"]

    if not headers or not data:
        return "import pandas as pd\ndf = pd.DataFrame()"

    code_lines = ["import pandas as pd", ""]
    code_lines.append("df = pd.DataFrame({")

    for col_idx, (col_name, col_type) in enumerate(zip(headers, types)):
        col_values = []
        for row in data:
            value = row[col_idx] if col_idx < len(row) else None
            col_values.append(format_value(value, col_type))

        # Format as a Python list
        code_lines.append(f"    {repr(col_name)}: [{', '.join(col_values)}],")

    code_lines.append("})")

    return "\n".join(code_lines)


def generate_polars_code(parsed_table: dict[str, Any], types: list[ColumnType]) -> str:
    """Generate polars DataFrame creation code.

    Args:
        parsed_table: Dict with 'headers' and 'data' from parse_table
        types: List of type strings for each column

    Returns:
        Python code string to create a polars DataFrame

    """
    headers = parsed_table["headers"]
    data = parsed_table["data"]

    if not headers or not data:
        return "import polars as pl\ndf = pl.DataFrame()"

    code_lines = ["import polars as pl", ""]
    code_lines.append("df = pl.DataFrame({")

    for col_idx, (col_name, col_type) in enumerate(zip(headers, types)):
        col_values = []
        for row in data:
            value = row[col_idx] if col_idx < len(row) else None
            col_values.append(format_value(value, col_type))

        # Format as a Python list
        code_lines.append(f"    {repr(col_name)}: [{', '.join(col_values)}],")

    code_lines.append("})")

    return "\n".join(code_lines)
