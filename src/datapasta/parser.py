"""Parser for detecting and extracting tabular data from text."""

from typing import Any


def guess_separator(lines: list[str], candidates: list[str] | None = None) -> str:
    """Guess the delimiter/separator used in the text.

    Args:
        lines: List of strings (lines from text)
        candidates: Optional list of candidate separators to try

    Returns:
        The separator that produces the most consistent columns

    """
    if candidates is None:
        candidates = [",", "\t", "|", ";", " "]

    lines_to_check = lines[:10] if len(lines) > 10 else lines
    lines_to_check = [line for line in lines_to_check if line.strip()]

    if not lines_to_check:
        return ","  # Default to comma for empty input

    best_sep = None
    best_num_cols = 0
    most_consistent = False

    for sep in candidates:
        # Try splitting each line with this separator
        splits = [line.split(sep) for line in lines_to_check]

        # Count columns in each line
        col_counts = [len(split) for split in splits]

        # Check if column counts are consistent
        consistent = max(col_counts) == min(col_counts) and max(col_counts) > 1

        # Prefer consistent column counts
        if consistent and (not most_consistent or col_counts[0] > best_num_cols):
            best_num_cols = col_counts[0]
            best_sep = sep
            most_consistent = True
        # If we haven't found any consistent separator yet, keep track of the one with most columns
        elif not most_consistent and col_counts[0] > best_num_cols:
            best_num_cols = col_counts[0]
            best_sep = sep

    # Handle fixed-width formats with multiple spaces
    if best_sep == " " and best_num_cols > 1:
        # Check if it's multiple spaces (common in fixed-width formats)
        for line in lines_to_check:
            if "  " in line:  # Two or more spaces
                return "  "  # Use double space as separator

    return best_sep or ","  # Default to comma if nothing else works


def split_lines(text: str) -> list[str]:
    """Split text into lines, handling different line endings.

    Args:
        text: The input text to split

    Returns:
        A list of lines

    """
    if not text:
        return []

    # Handle different line endings
    if "\r\n" in text:
        return text.split("\r\n")
    elif "\n" in text:
        return text.split("\n")
    elif "\r" in text:
        return text.split("\r")
    else:
        return [text]


def parse_table(
    text: str,
    sep: str | None = None,
    max_rows: int = 10_000,
    has_header: bool | None = None,
) -> dict[str, Any]:
    """Parse text into rows and columns.

    Args:
        text: String to parse
        sep: Optional separator (if None, will be guessed)
        max_rows: Maximum number of rows to parse
        has_header: If True, force first row as header. If False, force no header.
                    If None (default), auto-detect.

    Returns:
        dict with:
        - headers: list of column names
        - data: list of lists (rows)
        - separator: the separator used
        - has_header: boolean indicating if a header was detected

    """
    lines = split_lines(text)
    lines = [line for line in lines if line.strip()]  # Remove empty lines

    if not lines:
        return {"headers": [], "data": [], "separator": None, "has_header": False}

    if len(lines) > max_rows:
        lines = lines[:max_rows]

    # Guess separator if not provided
    if sep is None:
        sep = guess_separator(lines)

    # Parse into rows
    rows = []
    for line in lines:
        if line.strip():
            if sep == "\t":
                # Handle tab specially since split() with tab can behave oddly
                row = line.split("\t")
            else:
                row = line.split(sep)
            # Strip whitespace from each value
            row = [cell.strip() for cell in row]
            rows.append(row)

    if not rows:
        return {"headers": [], "data": [], "separator": sep, "has_header": False}

    # Determine if first row is a header based on parameter or auto-detection
    detected_has_header = False

    if has_header is None:  # Auto-detect
        data_rows = rows[1:] if len(rows) > 1 else []

        if data_rows:
            first_row = rows[0]

            # Function to check if a value looks numeric
            def is_numeric(val):
                try:
                    float(val)
                    return True
                except (ValueError, TypeError):
                    return False

            # Check if first row's types differ from the rest
            first_row_types = [not is_numeric(val) for val in first_row]

            # Check at least a few data rows
            check_rows = min(5, len(data_rows))
            rest_rows_types = []

            for i in range(check_rows):
                if i < len(data_rows):
                    row = data_rows[i]
                    # Make sure the row has the same length as first_row
                    if len(row) == len(first_row):
                        rest_rows_types.append(
                            [not is_numeric(val) for val in row[: len(first_row)]],
                        )

            if rest_rows_types:
                # Compare if first row looks different from data rows
                different_count = 0
                for col_idx in range(len(first_row)):
                    first_row_is_text = first_row_types[col_idx]
                    data_rows_are_text = [row[col_idx] for row in rest_rows_types]

                    # If first row is text but data rows are numeric, increment difference count
                    if first_row_is_text and not all(data_rows_are_text):
                        different_count += 1

                # If more than half the columns in first row look like headers, treat it as a header
                detected_has_header = different_count >= len(first_row) / 2
    else:
        # Use the explicitly provided value
        detected_has_header = has_header

    # Set up headers and data
    if detected_has_header:
        headers = rows[0]
        data = rows[1:]
    else:
        # Create default column names
        num_cols = len(rows[0]) if rows else 0
        headers = [f"col{i + 1}" for i in range(num_cols)]
        data = rows

    return {
        "headers": headers,
        "data": data,
        "separator": sep,
        "has_header": detected_has_header,
    }
