"""Integration with cliptargets for enhanced clipboard access."""

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


def parse_multiline_table(text: str) -> dict | None:
    """Parse tables where rows are split across multiple lines.

    Handles cases where a logical row spans multiple physical lines,
    typically with the first line containing the first column value
    and subsequent indented/tab-prefixed lines containing other column values.

    Args:
        text: The text to parse

    Returns:
        Dictionary with parsed table data or None if not a multi-line format

    """
    lines = split_lines(text)
    lines = [line for line in lines if line.strip() or line.startswith("\t")]

    if len(lines) < 3:  # Need header + at least one full row (2 lines)
        return None

    # Detect alternating non-tab and tab-prefixed lines pattern
    has_multiline_format = False
    tab_pattern = []

    for i in range(1, min(7, len(lines))):  # Check first few lines
        tab_pattern.append(lines[i].startswith("\t"))

    if len(tab_pattern) >= 2:
        alternating = True
        for i in range(len(tab_pattern) - 1):
            if tab_pattern[i] == tab_pattern[i + 1]:
                alternating = False
                break
        has_multiline_format = (
            alternating and not tab_pattern[0]
        )  # First data line shouldn't be tab-prefixed

    if not has_multiline_format:
        return None

    # Parse the header from the first line
    header_line = lines[0]
    headers = [h.strip() for h in header_line.split("\t") if h.strip()]

    if not headers:
        return None

    # Process the data rows (each logical row spans multiple physical lines)
    data = []
    i = 1

    while i < len(lines):
        # Look for a pair of lines: non-tab line followed by tab line
        if (
            i + 1 < len(lines)
            and not lines[i].startswith("\t")
            and lines[i + 1].startswith("\t")
        ):
            # First line has the first column value
            main_value = lines[i].strip()

            # Second line has remaining column values (remove leading tab)
            tab_line = lines[i + 1].lstrip("\t")
            tab_values = [v.strip() for v in tab_line.split("\t")]

            # Combine into a single row
            row = [main_value] + tab_values

            # Ensure row has correct number of columns
            if len(row) < len(headers):
                row.extend([""] * (len(headers) - len(row)))
            elif len(row) > len(headers):
                row = row[: len(headers)]

            data.append(row)
            i += 2  # Skip to next row pair
        else:
            i += 1  # Skip malformed lines

    # Only return if we parsed some data
    if data:
        return {
            "headers": headers,
            "data": data,
            "separator": "\t",
            "has_header": True,  # This format always has headers
        }

    return None


def clipboard_with_targets_to_parsed_table(
    separator: str | None = None,
    max_rows: int = 10_000,
    has_header: bool | None = None,
) -> dict:
    """Read clipboard content using cliptargets and parse it into a table structure.

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
            if not text:
                continue

            # First try multi-line table format
            multiline_table = parse_multiline_table(text)
            if multiline_table:
                if has_header is not None:
                    multiline_table["has_header"] = has_header
                return multiline_table

            # Then try standard table format
            if is_tabular_text(text):
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
    max_rows: int = 10_000,
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
    max_rows: int = 10_000,
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
