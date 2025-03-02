# Datapasta

A Python utility for pasting tabular data as formatted Python code, inspired by the R package of the same name.

## Installation

```bash
# From PyPI (not yet available)
pip install datapasta

# From source
git clone https://github.com/yourusername/datapasta.git
cd datapasta
pip install -e .

# Development installation
pip install -e ".[dev]"
```

## Features

- Read data from the clipboard or manual input
- Automatically guess separators in tabular data
- Detect column data types
- Format data as Polars or pandas DataFrame definitions
- Format as Python lists (horizontal or vertical)

## Usage

### Command Line

```bash
# Read from clipboard and output Polars code
datapasta

# Read from clipboard and output pandas code
datapasta --format pandas

# Read from clipboard and output as a Python list
datapasta --format vector

# Read from clipboard and output as a vertical Python list
datapasta --format vector-vertical

# Read from manual input instead of clipboard
datapasta --editor

# Copy output to clipboard instead of printing
datapasta --output clipboard
```

### Python API

```python
import datapasta

# Read and parse from clipboard
text = datapasta.read_clipboard()
parsed = datapasta.parse_text(text)

# Format as Polars code
polars_code = datapasta.format_as_polars(parsed)
print(polars_code)

# Format as pandas code
pandas_code = datapasta.format_as_pandas(parsed)
print(pandas_code)

# Format as Python list
vector_code = datapasta.format_as_vector(parsed)
print(vector_code)
```

## Example

Starting with clipboard content:

```
Name,Age,City
John,32,New York
Jane,28,San Francisco
Bob,45,Chicago
```

Running `datapasta` will produce:

```python
import polars as pl

df = pl.DataFrame({
    "Name": ["John", "Jane", "Bob"],
    "Age":  [32, 28, 45],
    "City": ["New York", "San Francisco", "Chicago"],
})
```

## License

MIT