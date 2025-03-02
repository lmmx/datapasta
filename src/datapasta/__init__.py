"""Paste data as Python DataFrame definitions.

PyPasta is a Python package that provides functionality similar to the R package datapasta,
allowing you to easily convert clipboard content to DataFrame code.
"""

from .main import clipboard_to_pandas, clipboard_to_polars, text_to_pandas, text_to_polars

__version__ = "0.1.0"
__all__ = ["clipboard_to_pandas", "clipboard_to_polars", "text_to_pandas", "text_to_polars"]