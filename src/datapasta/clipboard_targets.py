"""Integration with cliptargets for enhanced clipboard access."""

import re

from .clipboard import read_clipboard
from .formatter import generate_pandas_code, generate_polars_code
from .html_parser import html_to_parsed_table
from .parser import guess_separator, parse_table, split_lines
from .type_inference import infer_types_for_table


def is_tabular_text(text: str) -> bool:
    """Check if text appears to be in a tabular format with consistent delimiters.

    Args:
        text: Text to check

    Returns:
        True if the text appears to be a table with consistent structure

    """
    lines = split_lines(text)
    if len(lines) < 2:  # Need at least a header and one data row
        return False

    # Check if the text has consistent tab or other delimiter patterns
    sep = guess_separator(lines)
    if not sep:
        return False

    # Check if rows have consistent column counts
    split_rows = [line.split(sep) for line in lines if line.strip()]
    if not split_rows:
        return False

    col_counts = [len(row) for row in split_rows]
    # Return True if all rows have the same number of columns and it's more than 1
    return min(col_counts) == max(col_counts) and min(col_counts) > 1


def extract_table_from_github_artifacts_text(text: str) -> dict:
    r"""Extract a table from GitHub artifacts plain text.

    The GitHub artifacts plain text usually has a structure like:
    "Name \tSize \t\nartifact1\n\tsize1 \t\nartifact2\n\tsize2 \t\n..."

    Args:
        text: The plain text from clipboard

    Returns:
        Dictionary with parsed table data

    """
    # First check if it looks like GitHub artifacts format
    if not (
        "Name" in text
        and "\tSize" in text
        and any(name in text for name in ["wheels-", "artifact-", ".zip", ".tar.gz"])
    ):
        return None

    # Extract data in a more structured way
    lines = re.split(r"\r?\n", text)
    if not lines:
        return None

    # First line should contain headers
    headers = [h.strip() for h in lines[0].split("\t") if h.strip()]
    if not headers or "Name" not in headers:
        return None

    # Process the data rows, handling the special format
    data = []
    name = None
    row_data = []

    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue

        # If the line starts with a tab, it's a continuation of the previous row
        if line.startswith("\t"):
            values = [v.strip() for v in line.split("\t")]
            if values and name:
                row_data = [name] + values
                data.append(row_data)
                name = None
                row_data = []
        else:
            # This is a new name
            name = line.strip()

    # Make sure all data rows have the right number of columns
    header_count = len(headers)
    for i in range(len(data)):
        if len(data[i]) < header_count:
            data[i] = data[i] + [""] * (header_count - len(data[i]))
        elif len(data[i]) > header_count:
            data[i] = data[i][:header_count]

    return {
        "headers": headers,
        "data": data,
        "separator": "\t",
        "has_header": True,
    }


def clipboard_with_targets_to_parsed_table(
    separator: str | None = None,
    max_rows: int = 200,
    has_header: bool | None = None,
) -> dict:
    """Read clipboard content using cliptargets and parse it into a table structure.

    For GitHub artifacts and similar tab-separated tables, prioritizes the plain text
    version which is often more reliable. Falls back to HTML parsing for other cases.

    Args:
        separator: Optional separator (if None, will be guessed)
        max_rows: Maximum number of rows to parse
        has_header: If True, force first row as header. If False, force no header.
                   If None (default), auto-detect.

    Returns:
        Dictionary with parsed table data

    """
    try:
        import cliptargets

        all_targets = cliptargets.get_all_targets()

        # First try plain text targets for tabular data which is often more reliable
        text_targets = ["text/plain", "UTF8_STRING", "STRING"]
        for target in text_targets:
            text = all_targets.get(target)
            if text and is_tabular_text(text):
                # Special handling for GitHub artifacts format
                github_table = extract_table_from_github_artifacts_text(text)
                if github_table:
                    # Override has_header if explicitly set
                    if has_header is not None:
                        github_table["has_header"] = has_header
                    return github_table

                # Regular tab-separated table
                return parse_table(
                    text,
                    sep=separator,
                    max_rows=max_rows,
                    has_header=has_header,
                )

        # Next try HTML if available
        html_content = all_targets.get("text/html")
        if html_content:
            table = html_to_parsed_table(html_content)
            if table:
                # Override has_header if explicitly set
                if has_header is not None:
                    table["has_header"] = has_header
                return table

        # Fall back to any text content
        for target in text_targets:
            text = all_targets.get(target)
            if text:
                return parse_table(
                    text,
                    sep=separator,
                    max_rows=max_rows,
                    has_header=has_header,
                )

        # No suitable content found
        raise RuntimeError("No clipboard content found in recognized formats")

    except ImportError:
        # Fallback to simple clipboard if cliptargets not available
        text = read_clipboard()
        return parse_table(
            text,
            sep=separator,
            max_rows=max_rows,
            has_header=has_header,
        )


def clipboard_with_targets_to_pandas(
    separator: str | None = None,
    max_rows: int = 200,
    has_header: bool | None = None,
) -> str:
    """Read clipboard content using cliptargets and convert to pandas DataFrame code.

    Args:
        separator: Optional separator (if None, will be guessed)
        max_rows: Maximum number of rows to parse
        has_header: If True, force first row as header. If False, force no header.
                   If None (default), auto-detect.

    Returns:
        Python code string to create a pandas DataFrame

    """
    parsed_table = clipboard_with_targets_to_parsed_table(
        separator=separator,
        max_rows=max_rows,
        has_header=has_header,
    )

    types = infer_types_for_table(parsed_table)
    return generate_pandas_code(parsed_table, types)


def clipboard_with_targets_to_polars(
    separator: str | None = None,
    max_rows: int = 200,
    has_header: bool | None = None,
) -> str:
    """Read clipboard content using cliptargets and convert to polars DataFrame code.

    Args:
        separator: Optional separator (if None, will be guessed)
        max_rows: Maximum number of rows to parse
        has_header: If True, force first row as header. If False, force no header.
                   If None (default), auto-detect.

    Returns:
        Python code string to create a polars DataFrame

    """
    parsed_table = clipboard_with_targets_to_parsed_table(
        separator=separator,
        max_rows=max_rows,
        has_header=has_header,
    )

    types = infer_types_for_table(parsed_table)
    return generate_polars_code(parsed_table, types)
