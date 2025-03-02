"""Parse raw text into structured data."""

import csv
import io

from datapasta.utils import (
    clean_column_name,
    guess_column_types,
    guess_has_header,
)


def guess_separator(text: str) -> str:
    """Guess the separator/delimiter in a text, similar to datapasta's approach.

    Args:
        text (str): Text to analyze for delimiter

    Returns:
        str: The detected separator character

    """
    candidate_seps = [",", "\t", "|", ";"]

    # Sample up to first 10 non-empty lines
    lines = [line for line in text.splitlines() if line.strip()][:10]
    if not lines:
        return ","  # Default to comma if no content

    best_sep = None
    best_score = 0

    for sep in candidate_seps:
        # Check if lines split with consistent column counts
        col_counts = []
        for line in lines:
            # Skip entirely empty lines or lines containing only the separator
            if not line.strip() or line.strip() == sep:
                continue

            parts = line.split(sep)
            col_counts.append(len(parts))

        # Skip if no valid lines were found with this separator
        if not col_counts:
            continue

        # If all rows have same column count, this is a good candidate
        if len(set(col_counts)) == 1:  # All rows have same column count
            # Pick the one that yields the most columns
            if col_counts[0] > best_score:
                best_score = col_counts[0]
                best_sep = sep

    if best_sep is None:
        # None of the separators gave consistent columns; default to comma
        return ","

    return best_sep


def parse_text(
    text: str, separator: str | None = None, header: bool | None = None
) -> dict:
    """Parse text into structured data, guessing separator and header row.

    Args:
        text (str): The text to parse
        separator (str, optional): Delimiter character. If None, will be guessed.
        header (bool, optional): Whether first row is a header. If None, will be guessed.

    Returns:
        dict: Parsed data with keys: 'data', 'columns', 'types'

    """
    if not text.strip():
        return {"data": [], "columns": [], "types": []}

    if separator is None:
        separator = guess_separator(text)

    # Read as CSV with the determined separator
    lines = text.strip().split("\n")
    reader = csv.reader(io.StringIO(text), delimiter=separator)
    rows = [row for row in reader if row]  # Skip empty rows

    if not rows:
        return {"data": [], "columns": [], "types": []}

    # Guess if first row is header (if not specified)
    if header is None:
        header = guess_has_header(rows)

    if header and len(rows) > 1:
        column_names = [clean_column_name(col) for col in rows[0]]
        data = rows[1:]
    else:
        # Generate column names (V1, V2, etc.)
        column_names = [f"V{i + 1}" for i in range(len(rows[0]))]
        data = rows

    # Transpose data for column-based analysis
    columns = list(zip(*data))

    # Guess data types
    column_types = [guess_column_types(col) for col in columns]

    result = {
        "data": data,
        "columns": column_names,
        "types": column_types,
    }

    return result
