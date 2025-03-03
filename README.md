# datapasta

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)
[![PyPI](https://img.shields.io/pypi/v/datapasta.svg)](https://pypi.org/project/datapasta)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/datapasta.svg)](https://pypi.org/project/datapasta)
[![License](https://img.shields.io/pypi/l/datapasta.svg)](https://pypi.python.org/pypi/datapasta)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/lmmx/datapasta/master.svg)](https://results.pre-commit.ci/latest/github/lmmx/datapasta/master)

A Python package inspired by the R `datapasta` package for pasting tabular data into DataFrame code. datapasta analyzes clipboard content or text input and generates Python code to recreate the data as a pandas or pandas DataFrame.

## Features

- Automatic detection of delimiters (comma, tab, pipe, semicolon, etc.)
- Smart header detection
- Type inference for columns (int, float, boolean, datetime, string)
- Generates code for both pandas and pandas DataFrames
- Command-line interface for easy integration with text editors
- Simple API for programmatic use

## Installation

```bash
# Install with pip
pip install datapasta

# With Pyperclip support (for Windows/MacOS, or if you are on Linux but not using X windows manager)
pip install datapasta[pyperclip]

# With Pandas execution support
pip install datapasta[pandas]

# With Polars execution support
pip install datapasta[polars]
# or for Polars on older CPUs
pip install datapasta[polars-lts-cpu]
```

> The `pandas` and `polars`/`polars-lts-cpu` dependencies are not included in the package by default,
> as typically you don't need to actually execute any code in those libraries. If you use the
> `--repr` CLI flag you do, hence the extras are provided for convenience.

## Command Line Usage

```
usage: datapasta [-h] [--file FILE] [--sep SEP] [--max-rows MAX_ROWS]
                 [--pandas] [--header {auto,yes,no}] [--legacy] [--repr]

Convert clipboard or text to DataFrame code

options:
  -h, --help            show this help message and exit
  --file FILE, -f FILE  Input file (if not using clipboard)
  --sep SEP, -s SEP     Separator (default: auto-detect)
  --max-rows MAX_ROWS, -m MAX_ROWS
                        Max rows to parse
  --pandas, -p          Generate pandas code (default: polars)
  --header {auto,yes,no}
                        Header detection: 'auto' to detect automatically,
                        'yes' to force header, 'no' to force no header
  --legacy              Use legacy clipboard access (don't use cliptargets)
  --repr, -r            Execute the code and print the DataFrame repr
```

### GitHub Artifacts example

If you go to the GitHub Actions results summary page you see a HTML table.
datapasta will generate the DataFrame code for you from the clipboard :magic_wand:

```
(datapasta) louis 🚶 ~/dev/datapasta $ datapasta
import polars as pl

df = pl.DataFrame({
    'Name': ['wheels-linux-aarch64', 'wheels-linux-armv7', 'wheels-linux-ppc64le',
'wheels-linux-s390x'],
    'Size': ['4.2 MB', '3.78 MB', '4.63 MB', '5.5 MB'],
})
(datapasta) louis 🚶 ~/dev/datapasta $ python -ic "$(datapasta)"
>>> print(df)
shape: (4, 2)
┌──────────────────────┬─────────┐
│ Name                 ┆ Size    │
│ ---                  ┆ ---     │
│ str                  ┆ str     │
╞══════════════════════╪═════════╡
│ wheels-linux-aarch64 ┆ 4.2 MB  │
│ wheels-linux-armv7   ┆ 3.78 MB │
│ wheels-linux-ppc64le ┆ 4.63 MB │
│ wheels-linux-s390x   ┆ 5.5 MB  │
└──────────────────────┴─────────┘
```

If that's all you want, run:

```sh
datapasta --repr
```

This will automatically execute the code and print out the result (you must have Polars installed!)

```
shape: (4, 2)
┌──────────────────────┬─────────┐
│ Name                 ┆ Size    │
│ ---                  ┆ ---     │
│ str                  ┆ str     │
╞══════════════════════╪═════════╡
│ wheels-linux-aarch64 ┆ 4.2 MB  │
│ wheels-linux-armv7   ┆ 3.78 MB │
│ wheels-linux-ppc64le ┆ 4.63 MB │
│ wheels-linux-s390x   ┆ 5.5 MB  │
└──────────────────────┴─────────┘
```

## How It Works

1. datapasta checks if the `cliptargets` package is available
2. If available, it looks for the `text/html` target in the clipboard
3. If HTML content is found, it extracts tables using a lightweight HTML parser
4. It detects headers based on HTML structure (`<thead>` or `<th>` elements)
5. If no HTML content is found or no tables are present, it falls back to the text-based parsing

This feature is particularly useful when copying tables from web applications, where the HTML structure provides more reliable information about the table's layout and headers than plain text.

Note:

- Will not use HTML if it can parse the table from text
- Will only parse up to 10,000 rows (see `max_rows` argument) unless told otherwise

## Usage

### Command Line

```bash
# Read from clipboard, generate pandas code
datapasta > dataframe_code.py

# Read from clipboard, generate polars code
datapasta > dataframe_code.py

# Read from file instead of clipboard
datapasta --file data.csv > dataframe_code.py

# Specify a separator (otherwise auto-detected)
datapasta --sep "," > dataframe_code.py
```

### Python API

```python
import datapasta

# Read from clipboard and get polars code
polars_code = datapasta.clipboard_to_polars()
print(polars_code)

# Read from clipboard and get pandas code
pandas_code = datapasta.clipboard_to_pandas()
print(pandas_code)

# Convert text directly to DataFrame code
csv_text = """name,age,city
Alice,25,New York
Bob,30,San Francisco
Charlie,35,Seattle"""

polars_code = datapasta.text_to_polars(csv_text)
print(polars_code)
```

## Controlling Header Detection

datapasta attempts to automatically detect whether your data has a header row, but you can override this behavior when needed:

### Command Line

```bash
# Auto-detect headers (default behavior)
datapasta --file data.csv

# Force using the first row as a header
datapasta --file data.csv --header yes

# Force no header (generate column names like col1, col2, etc.)
datapasta --file data.csv --header no
```

### Python API

```python
import datapasta

# Auto-detect headers (default)
code = datapasta.text_to_polars(text)

# Force using the first row as a header
code = datapasta.text_to_polars(text, has_header=True)

# Force no header
code = datapasta.text_to_polars(text, has_header=False)
```

This is particularly useful when:

- The auto-detection logic misidentifies numeric headers as data
- You want to preserve the first row as data but datapasta treats it as a header
- You need consistent column names (col1, col2, etc.) for multiple similar datasets

### Enhanced HTML Table Support

datapasta has the ability to extract tables directly from HTML content in the clipboard (as a fallback measure, experimental).

This is especially useful when copying tables from web pages, spreadsheets, or other applications that place HTML content in the clipboard.

```python
import datapasta

# Will automatically use HTML table content if available
code = datapasta.clipboard_with_targets_to_polars()
print(code)
```

## Examples

### From a CSV in the clipboard
```
name,age,city
Alice,25,New York
Bob,30,San Francisco
Charlie,35,Seattle
```

datapasta will generate:

```python
import polars as pl

df = pl.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 30, 35],
    "city": ["New York", "San Francisco", "Seattle"],
})
```

### From a TSV in the clipboard
```
name	age	city
Alice	25	New York
Bob	30	San Francisco
Charlie	35	Seattle
```

datapasta will generate similar code, automatically detecting the tab delimiter.

### Using in a Jupyter notebook

```python
import datapasta

# Assuming you've copied data to clipboard
code = datapasta.clipboard_to_polars()
print("Generated code:")
print(code)

# Execute the code to create the DataFrame
exec(code)
# Now 'df' contains your DataFrame
display(df)
```

## How It Works

datapasta works by:

1. Reading text from the clipboard or a file
2. Intelligently guessing the delimiter/separator
3. Detecting if there's a header row
4. Inferring column types (int, float, boolean, datetime, string)
5. Generating code to create a pandas or pandas DataFrame

## Project Structure

- `clipboard.py`: Functions for reading from the system clipboard
- `parser.py`: Functions for parsing text data, detecting delimiters, and headers
- `type_inference.py`: Functions for inferring column data types
- `formatter.py`: Functions for generating pandas and pandas code
- `main.py`: Main entry points and CLI functionality

## Contributing

Contributions welcome!

1. **Issues & Discussions**: Please open a GitHub issue or discussion for bugs, feature requests, or questions.
2. **Pull Requests**: PRs are welcome!
   - Install the dev extra with `pip install -e ".[dev]"`
   - Run tests with `pytest`
   - Include updates to docs or examples if relevant

## Requirements

- Python 3.10+
- **either** cliptargets (Linux X11) or pyperclip (Windows, Mac, non-X11 Linux)

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

## Credits

Inspired by the R package [datapasta](https://github.com/MilesMcBain/datapasta) by Miles McBain,
which does the same for `tibble::tribble` and `data.frame` tables (entirely separate R libraries).
