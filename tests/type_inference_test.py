"""Test type inference functionality."""

from datapasta.type_inference import infer_type, infer_types_for_table


def test_infer_type_int():
    """Test integer type inference."""
    values = ["1", "2", "3", "123", "-456"]
    assert infer_type(values) == "int"


def test_infer_type_float():
    """Test float type inference."""
    values = ["1.23", "45.6", "-78.9", "0.1", "2.0"]
    assert infer_type(values) == "float"


def test_infer_type_bool():
    """Test boolean type inference."""
    values = ["true", "false", "True", "False", "yes", "no"]
    assert infer_type(values) == "bool"


def test_infer_type_datetime():
    """Test datetime type inference."""
    values = ["2023-01-15", "2023-02-20", "2023-03-05"]
    assert infer_type(values) == "datetime"


def test_infer_type_string():
    """Test string type inference."""
    values = ["foo", "bar", "baz", "lorem ipsum"]
    assert infer_type(values) == "str"


def test_infer_type_mixed_defaults_to_string():
    """Test mixed type defaults to string."""
    values = ["foo", "123", "true", "2023-01-15"]
    assert infer_type(values) == "str"


def test_infer_type_empty():
    """Test empty list defaults to string."""
    values = []
    assert infer_type(values) == "str"


def test_infer_type_with_nulls():
    """Test type inference with null values."""
    values = ["1", "2", "", "NA", "null", "none", "3"]
    assert infer_type(values) == "int"


def test_infer_types_for_table():
    """Test inferring types for a whole table."""
    parsed_table = {
        "headers": ["name", "age", "active", "date", "note"],
        "data": [
            ["Alice", "25", "true", "2023-01-15", "First entry"],
            ["Bob", "30", "false", "2023-02-20", "Second entry"],
            ["Charlie", "35", "true", "2023-03-05", "Third entry"],
        ],
    }

    types = infer_types_for_table(parsed_table)
    assert types == ["str", "int", "bool", "datetime", "str"]


def test_infer_types_for_empty_table():
    """Test inferring types for an empty table."""
    parsed_table = {
        "headers": ["name", "age", "active"],
        "data": [],
    }

    types = infer_types_for_table(parsed_table)
    assert types == ["str", "str", "str"]
