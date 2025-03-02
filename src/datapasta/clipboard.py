"""Handle clipboard operations to read/write text."""

import sys


def read_clipboard():
    """Read data from the clipboard.

    Returns:
        str: Text content from clipboard or empty string if unavailable

    """
    try:
        import pyperclip

        return pyperclip.paste()
    except ImportError:
        print(
            "pyperclip not installed. Install with: pip install pyperclip",
            file=sys.stderr,
        )
        return ""
    except Exception as e:
        print(f"Error reading clipboard: {e}", file=sys.stderr)
        return ""


def write_clipboard(text):
    """Write data to the clipboard.

    Args:
        text (str): Text to copy to clipboard

    Returns:
        bool: True if successful, False otherwise

    """
    try:
        import pyperclip

        pyperclip.copy(text)
        return True
    except ImportError:
        print(
            "pyperclip not installed. Install with: pip install pyperclip",
            file=sys.stderr,
        )
        return False
    except Exception as e:
        print(f"Error writing to clipboard: {e}", file=sys.stderr)
        return False


def read_from_editor():
    """Read text from a temporary editor (fallback if clipboard not available)

    Returns:
        str: Text entered by user

    """
    print("Paste your text below (Ctrl+D or Ctrl+Z on empty line to finish):")
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    return "\n".join(lines)
