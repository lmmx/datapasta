"""Main functionality and CLI entry point."""

import argparse
import sys

from .clipboard import read_clipboard
from .formatter import generate_pandas_code, generate_polars_code
from .parser import parse_table
from .type_inference import infer_types_for_table


def text_to_pandas(
    text: str,
    separator: str | None = None,
    max_rows: int = 10_000,
    has_header: bool | None = None,
) -> str:
    """Convert text to pandas DataFrame creation code.

    Args:
        text: Text to parse
        separator: Optional separator (if None, will be guessed)
        max_rows: Maximum number of rows to parse
        has_header: If True, force first row as header. If False, force no header.
                   If None (default), auto-detect.

    Returns:
        Python code string to create a pandas DataFrame

    """
    parsed = parse_table(text, sep=separator, max_rows=max_rows, has_header=has_header)
    types = infer_types_for_table(parsed)
    return generate_pandas_code(parsed, types)


def text_to_polars(
    text: str,
    separator: str | None = None,
    max_rows: int = 10_000,
    has_header: bool | None = None,
) -> str:
    """Convert text to polars DataFrame creation code.

    Args:
        text: Text to parse
        separator: Optional separator (if None, will be guessed)
        max_rows: Maximum number of rows to parse
        has_header: If True, force first row as header. If False, force no header.
                   If None (default), auto-detect.

    Returns:
        Python code string to create a polars DataFrame

    """
    parsed = parse_table(text, sep=separator, max_rows=max_rows, has_header=has_header)
    types = infer_types_for_table(parsed)
    return generate_polars_code(parsed, types)


def clipboard_to_pandas(
    separator: str | None = None,
    max_rows: int = 10_000,
    has_header: bool | None = None,
) -> str:
    """Read text from clipboard and convert to pandas DataFrame creation code.

    Args:
        separator: Optional separator (if None, will be guessed)
        max_rows: Maximum number of rows to parse
        has_header: If True, force first row as header. If False, force no header.
                   If None (default), auto-detect.

    Returns:
        Python code string to create a pandas DataFrame

    """
    text = read_clipboard()
    return text_to_pandas(
        text,
        separator=separator,
        max_rows=max_rows,
        has_header=has_header,
    )


def clipboard_to_polars(
    separator: str | None = None,
    max_rows: int = 10_000,
    has_header: bool | None = None,
) -> str:
    """Read text from clipboard and convert to polars DataFrame creation code.

    Args:
        separator: Optional separator (if None, will be guessed)
        max_rows: Maximum number of rows to parse
        has_header: If True, force first row as header. If False, force no header.
                   If None (default), auto-detect.

    Returns:
        Python code string to create a polars DataFrame

    """
    text = read_clipboard()
    return text_to_polars(
        text,
        separator=separator,
        max_rows=max_rows,
        has_header=has_header,
    )


def main() -> None:
    """Command line interface for the package."""
    parser = argparse.ArgumentParser(
        description="Convert clipboard or text to DataFrame code",
    )
    parser.add_argument("--file", "-f", help="Input file (if not using clipboard)")
    parser.add_argument("--sep", "-s", help="Separator (default: auto-detect)")
    parser.add_argument(
        "--max-rows",
        "-m",
        type=int,
        default=10_000,
        help="Max rows to parse",
    )
    parser.add_argument(
        "--polars",
        "-p",
        action="store_true",
        help="Generate polars code (default: pandas)",
    )
    parser.add_argument(
        "--header",
        choices=["auto", "yes", "no"],
        default="auto",
        help="Header detection: 'auto' to detect automatically, 'yes' to force header, 'no' to force no header",
    )
    parser.add_argument(
        "--legacy",
        action="store_true",
        help="Use legacy clipboard access (don't use cliptargets)",
    )
    parser.add_argument(
        "--repr",
        "-r",
        action="store_true",
        help="Execute the code and print the DataFrame repr",
    )

    args = parser.parse_args()

    # Convert header argument to appropriate value
    has_header = None if args.header == "auto" else (args.header == "yes")

    try:
        # File input takes precedence
        if args.file:
            with open(args.file, encoding="utf-8") as f:
                text = f.read()

            if args.polars:
                code = text_to_polars(
                    text,
                    separator=args.sep,
                    max_rows=args.max_rows,
                    has_header=has_header,
                )
            else:
                code = text_to_pandas(
                    text,
                    separator=args.sep,
                    max_rows=args.max_rows,
                    has_header=has_header,
                )
        else:
            # Determine which clipboard access method to use
            if args.legacy:
                # Legacy clipboard access
                if args.polars:
                    code = clipboard_to_polars(
                        separator=args.sep,
                        max_rows=args.max_rows,
                        has_header=has_header,
                    )
                else:
                    code = clipboard_to_pandas(
                        separator=args.sep,
                        max_rows=args.max_rows,
                        has_header=has_header,
                    )
            else:
                # Enhanced clipboard access with targets
                try:
                    if args.polars:
                        from .clipboard_targets import clipboard_with_targets_to_polars

                        code = clipboard_with_targets_to_polars(
                            separator=args.sep,
                            max_rows=args.max_rows,
                            has_header=has_header,
                        )
                    else:
                        from .clipboard_targets import clipboard_with_targets_to_pandas

                        code = clipboard_with_targets_to_pandas(
                            separator=args.sep,
                            max_rows=args.max_rows,
                            has_header=has_header,
                        )
                except ImportError as e:
                    print(
                        f"Warning: {e}. Falling back to legacy clipboard access.",
                        file=sys.stderr,
                    )
                    if args.polars:
                        code = clipboard_to_polars(
                            separator=args.sep,
                            max_rows=args.max_rows,
                            has_header=has_header,
                        )
                    else:
                        code = clipboard_to_pandas(
                            separator=args.sep,
                            max_rows=args.max_rows,
                            has_header=has_header,
                        )

        if args.repr:
            if args.polars:
                row_cfg = "cfg.set_tbl_rows(-1)"
                col_cfg = "cfg.set_tbl_cols(-1)"
                cfg = f"cfg=pl.Config()\n{row_cfg}\n{col_cfg}"
            else:
                row_cfg = "pd.set_option('display.max_rows', None)"
                col_cfg = "pd.set_option('display.max_columns', None)"
                cfg = f"{row_cfg}\n{col_cfg}"
            exec(code + f"\n{cfg}\nprint(df)")
        else:
            print(code)

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
