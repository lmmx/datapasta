"""Paste data as Python DataFrame definitions.

PyPasta is a Python package that provides functionality similar to the R package datapasta,
allowing you to easily convert clipboard content to DataFrame code.
"""

from .main import (
    clipboard_to_pandas,
    clipboard_to_polars,
    text_to_pandas,
    text_to_polars,
)

# Import enhanced clipboard functions if cliptargets is available
try:
    from .clipboard_targets import (
        clipboard_with_targets_to_pandas,
        clipboard_with_targets_to_polars,
    )

    HAS_TARGETS = True
except ImportError:
    HAS_TARGETS = False

__version__ = "0.1.2"

if HAS_TARGETS:
    __all__ = [
        "clipboard_to_pandas",
        "clipboard_to_polars",
        "clipboard_with_targets_to_pandas",
        "clipboard_with_targets_to_polars",
        "text_to_pandas",
        "text_to_polars",
        "HAS_TARGETS",
    ]
else:
    __all__ = [
        "clipboard_to_pandas",
        "clipboard_to_polars",
        "text_to_pandas",
        "text_to_polars",
        "HAS_TARGETS",
    ]
