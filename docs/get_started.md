---
title: "Get Started"
icon: material/human-greeting
---

# Getting Started

## 1. Installation

`datapasta` is [on PyPI](https://pypi.org/project/datapasta). Install with:

```bash
pip install datapasta
```

!!! info "Using `uv` (optional)"
    If you set up [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended for a smoother developer experience), you can install with:
    ```bash
    uv pip install datapasta
    ```
    or set up a project (e.g., `uv init --app --package`, `uv venv`, then activate the venv), and add `datapasta`:
    ```bash
    uv add datapasta
    ```

If you use Windows/MacOS (or a non-X11 clipboard on Linux) you will need the pyperclip extra when installing:

```sh
pip install datapasta[pyperclip]
```

## 2. Usage

`datapasta` provides a CLI tool called `datapasta`. To convert clipboard table data to Python code:

```bash
datapasta
```

To generate pandas code instead of polars, add the `--pandas` flag:

```bash
datapasta --pandas
```

This will generate Polars DataFrame code for the table data in your clipboard.

(Note: you do not need to actually have Pandas or Polars installed to run this!)

### More CLI Examples

- **Read from a file instead of clipboard**:
  ```bash
  datapasta --file data.csv
  ```
- **Specify a separator (otherwise auto-detected)**:
  ```bash
  datapasta --file data.tsv --sep "\t"
  ```
- **Force header detection**:
  ```bash
  datapasta --header yes
  ```

For advanced usage like limiting rows, see the [CLI reference](index.md).

## 3. Local Development

1. **Clone the Repo**:
   ```bash
   git clone https://github.com/lmmx/datapasta.git
   ```
2. **Install Dependencies**:
   - If you're using [pdm](https://pdm.fming.dev/latest/):
     ```bash
     pdm install
     ```
   - Otherwise, standard pip:
     ```bash
     pip install -e .
     ```
3. **Optional: Pre-commit Hooks**:
   ```bash
   pre-commit install
   ```
   This automatically runs lint checks (e.g., ruff, black) before each commit.

4. **Run Tests** (if applicable):
   ```bash
   pytest
   ```
5. **Build/Serve Docs** (if included):
   ```bash
   mkdocs serve
   ```
   Then visit the local server link. Use `mkdocs gh-deploy` to publish on GitHub Pages.

## 4. Example Workflow

1. **Copy a table from a website**:
   - Go to a website with tabular data
   - Select and copy the table

2. **Generate the DataFrame code**:
   ```bash
   datapasta > table_code.py
   ```

3. **Use the generated code in your project**:
   ```py
   import table_code
   ```

4. **Work with the data programmatically**:
   ```bash
   datapasta | python -c "exec(open(0).read()); print(df.filter(pl.col('Size').str.contains('MB')).head(2))"
   ```
   This pipes the generated code directly to Python and filters rows containing "MB".

## 5. Configuration

`datapasta` primarily relies on:
- **Clipboard access**: Works with system clipboard (handled by pyperclip)
- **HTML parsing**: Automatically extracts tables from HTML content when available
- **CLI Flags**: Control parsing, output format, and header detection:
  - `--pandas`: Generate pandas code instead of Polars
  - `--max-rows`: Limit maximum rows to parse (default: 10,000)
  - `--header`: Control header detection (`auto`, `yes`, `no`)
  - `--sep`: Specify delimiter/separator (auto-detected by default)
  - `--legacy`: Use legacy clipboard access (no HTML support)

For further details, consult the [API Reference](api/index.md) or the help text:

```bash
datapasta --help
```
