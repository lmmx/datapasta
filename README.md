# Enhanced HTML Table Support

When the `cliptargets` package is installed, datapasta gains the ability to extract tables directly from HTML content in the clipboard. This is especially useful when copying tables from web pages, spreadsheets, or other applications that place HTML content in the clipboard.

## Installation with HTML Table Support

```bash
# Install with HTML table support via cliptargets
pip install "datapasta[targets]"

# For complete installation (pandas, polars, and HTML support)
pip install "datapasta[full]"
```

## Benefits of HTML Table Support

- **Improved Header Detection**: Automatically detects table headers based on HTML structure (`<thead>` or `<th>` elements)
- **Better Structure Preservation**: Extracts data directly from HTML table structure, preserving rows and columns correctly
- **No Delimiter Issues**: Avoids problems with delimiter guessing and text parsing
- **Works with Web Content**: Ideal for copying tables from websites and web applications

## Using with HTML Tables

The API remains the same - datapasta automatically detects if HTML content is available in the clipboard and uses it when appropriate:

```python
import datapasta

# Will automatically use HTML table content if available
code = datapasta.clipboard_with_targets_to_pandas()
print(code)
```

### GitHub Artifacts example

If you go to the GitHub Actions results summary page you see a HTML table.
datapasta will generate the DataFrame code for you from the clipboard :magic_wand:

```
(datapasta) louis 🚶 ~/dev/datapasta $ datapasta --polars
import polars as pl

df = pl.DataFrame({
    'Name': ['wheels-linux-aarch64', 'wheels-linux-armv7', 'wheels-linux-ppc64le',
'wheels-linux-s390x'],
    'Size': ['4.2 MB', '3.78 MB', '4.63 MB', '5.5 MB'],
})
(datapasta) louis 🚶 ~/dev/datapasta $ python -ic "$(datapasta --polars)"
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

## Command Line Usage

```bash
# Automatically uses HTML table content if available
datapasta

# Force using legacy clipboard access (no HTML support)
datapasta --legacy
```

## How It Works

1. datapasta checks if the `cliptargets` package is available
2. If available, it looks for the `text/html` target in the clipboard
3. If HTML content is found, it extracts tables using a lightweight HTML parser
4. It detects headers based on HTML structure (`<thead>` or `<th>` elements)
5. If no HTML content is found or no tables are present, it falls back to the text-based parsing

This feature is particularly useful when copying tables from web applications, where the HTML structure provides more reliable information about the table's layout and headers than plain text.
