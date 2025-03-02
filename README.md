# datapasta

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)
[![PyPI](https://img.shields.io/pypi/v/datapasta.svg)](https://pypi.org/project/datapasta)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/datapasta.svg)](https://pypi.org/project/datapasta)
[![License](https://img.shields.io/pypi/l/datapasta.svg)](https://pypi.python.org/pypi/datapasta)

A Python package inspired by the R `datapasta` package for pasting tabular data into DataFrame code. datapasta analyzes clipboard content or text input and generates Python code to recreate the data as a pandas or polars DataFrame.

## Features

- Automatic detection of delimiters (comma, tab, pipe, semicolon, etc.)
- Smart header detection
- Type inference for columns (int, float, boolean, datetime, string)
- Generates code for both pandas and polars DataFrames
- Command-line interface for easy integration with text editors
- Simple API for programmatic use

## Installation

```bash
# Install with pip
pip install datapasta

# With polars support
pip install datapasta[polars]

# For older CPUs
pip install datapasta[polars-lts-cpu]
```

> The `polars` dependency is not included in the package by default.
> It is shipped as an optional extra which can be activated by passing it in square brackets.

## Usage

### Command Line

```bash
# Read from clipboard, generate pandas code
datapasta > dataframe_code.py

# Read from clipboard, generate polars code
datapasta --polars > dataframe_code.py

# Read from file instead of clipboard
datapasta --file data.csv > dataframe_code.py

# Specify a separator (otherwise auto-detected)
datapasta --sep "," > dataframe_code.py
```

### Python API

```python
import datapasta

# Read from clipboard and get pandas code
pandas_code = datapasta.clipboard_to_pandas()
print(pandas_code)

# Read from clipboard and get polars code
polars_code = datapasta.clipboard_to_polars()
print(polars_code)

# Convert text directly to DataFrame code
csv_text = """name,age,city
Alice,25,New York
Bob,30,San Francisco
Charlie,35,Seattle"""

pandas_code = datapasta.text_to_pandas(csv_text)
print(pandas_code)
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
import pandas as pd

df = pd.DataFrame({
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
code = datapasta.clipboard_to_pandas()
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
5. Generating code to create a pandas or polars DataFrame

## Project Structure

- `clipboard.py`: Functions for reading from the system clipboard
- `parser.py`: Functions for parsing text data, detecting delimiters, and headers
- `type_inference.py`: Functions for inferring column data types
- `formatter.py`: Functions for generating pandas and polars code
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
- pyperclip (for clipboard access)

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

## Credits

Inspired by the R package [datapasta](https://github.com/MilesMcBain/datapasta) by Miles McBain.
