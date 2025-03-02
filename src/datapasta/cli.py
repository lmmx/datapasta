"""
Command-line interface for datapasta.
"""
import argparse
import sys

from datapasta.clipboard import read_clipboard, write_clipboard, read_from_editor
from datapasta.parser import parse_text
from datapasta.formatter import (
    format_as_polars, 
    format_as_pandas,
    format_as_vector
)

def main():
    """
    Main CLI entry point.
    """
    parser = argparse.ArgumentParser(
        description="Convert clipboard data to Python DataFrame definitions"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["polars", "pandas", "vector", "vector-vertical"],
        default="polars",
        help="Output format (default: polars)"
    )
    
    parser.add_argument(
        "--output", "-o", 
        choices=["clipboard", "print"],
        default="print",
        help="Where to output the result (default: print to stdout)"
    )
    
    parser.add_argument(
        "--editor", "-e",
        action="store_true",
        help="Read from editor instead of clipboard"
    )
    
    args = parser.parse_args()
    
    # Get data from clipboard or editor
    if args.editor:
        data = read_from_editor()
    else:
        data = read_clipboard()
        if not data:
            print("No data found in clipboard. Use --editor to paste manually.", file=sys.stderr)
            return 1
    
    # Parse the data
    parsed = parse_text(data)
    
    # Format according to selected format
    if args.format == "polars":
        result = format_as_polars(parsed)
    elif args.format == "pandas":
        result = format_as_pandas(parsed)
    elif args.format == "vector":
        result = format_as_vector(parsed, vertical=False)
    elif args.format == "vector-vertical":
        result = format_as_vector(parsed, vertical=True)
    
    # Output the result
    if args.output == "clipboard":
        success = write_clipboard(result)
        if success:
            print("Result copied to clipboard.")
        else:
            print("Failed to copy to clipboard.", file=sys.stderr)
            return 1
    else:  # print
        print(result)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
