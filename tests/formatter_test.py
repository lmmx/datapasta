"""Test code generation functionality."""

from datapasta.formatter import format_value, generate_pandas_code, generate_polars_code


def test_format_value_int():
    """Test formatting integer values."""
    assert format_value("123", "int") == "123"
    assert format_value("-456", "int") == "-456"


def test_format_value_float():
    """Test formatting float values."""
    assert format_value("123.45", "float") == "123.45"
    assert format_value("-456.78", "float") == "-456.78"


def test_format_value_bool():
    """Test formatting boolean values."""
    assert format_value("true", "bool") == "True"
    assert format_value("false", "bool") == "False"
    assert format_value("yes", "bool") == "True"
    assert format_value("no", "bool") == "False"
    assert format_value("1", "bool") == "True"
    assert format_value("0", "bool") == "False"


def test_format_value_datetime():
    """Test formatting datetime values."""
    assert format_value("2023-01-15", "datetime") == "'2023-01-15'"


def test_format_value_string():
    """Test formatting string values."""
    assert format_value("hello", "str") == "'hello'"
    assert format_value('with "quotes"', "str") == r"""'with "quotes"'"""


def test_format_value_null():
    """Test formatting null values."""
    assert format_value(None, "int") == "None"
    assert format_value("", "int") == "None"
    assert format_value("NA", "int") == "None"
    assert format_value("N/A", "int") == "None"
    assert format_value("null", "int") == "None"
    assert format_value("None", "int") == "None"


def test_generate_pandas_code():
    """Test generating pandas DataFrame code."""
    parsed_table = {
        "headers": ["name", "age", "active"],
        "data": [
            ["Alice", "25", "true"],
            ["Bob", "30", "false"],
        ],
    }
    types = ["str", "int", "bool"]

    code = generate_pandas_code(parsed_table, types)

    assert "import pandas as pd" in code
    assert "df = pd.DataFrame({" in code
    assert "'name': ['Alice', 'Bob']," in code
    assert "'age': [25, 30]," in code
    assert "'active': [True, False]," in code


def test_generate_pandas_code_empty():
    """Test generating pandas DataFrame code for empty data."""
    parsed_table = {
        "headers": [],
        "data": [],
    }
    types = []

    code = generate_pandas_code(parsed_table, types)

    assert code == "import pandas as pd\ndf = pd.DataFrame()"


def test_generate_polars_code():
    """Test generating polars DataFrame code."""
    parsed_table = {
        "headers": ["name", "age", "active"],
        "data": [
            ["Alice", "25", "true"],
            ["Bob", "30", "false"],
        ],
    }
    types = ["str", "int", "bool"]

    code = generate_polars_code(parsed_table, types)

    assert "import polars as pl" in code
    assert "df = pl.DataFrame({" in code
    assert "'name': ['Alice', 'Bob']," in code
    assert "'age': [25, 30]," in code
    assert "'active': [True, False]," in code


def test_generate_polars_code_empty():
    """Test generating polars DataFrame code for empty data."""
    parsed_table = {
        "headers": [],
        "data": [],
    }
    types = []

    code = generate_polars_code(parsed_table, types)

    assert code == "import polars as pl\ndf = pl.DataFrame()"
