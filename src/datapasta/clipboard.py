"""Clipboard interaction functionality."""


def read_clipboard() -> str:
    """Read text from system clipboard.

    Returns:
        The text content from the clipboard

    Raises:
        ImportError: If pyperclip is not installed
        RuntimeError: If clipboard access fails

    """
    try:
        import pyperclip

        return pyperclip.paste()
    except ImportError:
        raise ImportError("Please install pyperclip: pip install pyperclip")
    except Exception as e:
        raise RuntimeError(f"Failed to read from clipboard: {str(e)}")
