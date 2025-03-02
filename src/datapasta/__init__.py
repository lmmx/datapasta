"""datapasta: Paste data as code

A Python library for pasting data from clipboard as pandas/polars code definitions,
inspired by the R package of the same name.
"""

__version__ = "0.1.0"

from datapasta.clipboard import read_clipboard
from datapasta.formatter import (
    format_as_pandas,
    format_as_polars,
    format_as_vector,
)
from datapasta.parser import guess_separator, parse_text

__all__ = [
    "read_clipboard",
    "parse_text",
    "guess_separator",
    "format_as_polars",
    "format_as_pandas",
    "format_as_vector",
]
