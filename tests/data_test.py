"""Test data parsing functionality."""

import pytest

from datapasta.parser import guess_separator, parse_table, split_lines


def test_guess_separator_csv():
    """Test CSV separator detection."""
    lines = ["name,age,city", "Alice,25,New York", "Bob,30,San Francisco"]
    assert guess_separator(lines) == ","


def test_guess_separator_tsv():
    """Test TSV separator detection."""
    lines = ["name\tage\tcity", "Alice\t25\tNew York", "Bob\t30\tSan Francisco"]
    assert guess_separator(lines) == "\t"


def test_guess_separator_pipe():
    """Test pipe separator detection."""
    lines = ["name|age|city", "Alice|25|New York", "Bob|30|San Francisco"]
    assert guess_separator(lines) == "|"


def test_split_lines():
    """Test line splitting with different line endings."""
    # Unix line endings
    text = "line1\nline2\nline3"
    assert split_lines(text) == ["line1", "line2", "line3"]

    # Windows line endings
    text = "line1\r\nline2\r\nline3"
    assert split_lines(text) == ["line1", "line2", "line3"]

    # Old Mac line endings
    text = "line1\rline2\rline3"
    assert split_lines(text) == ["line1", "line2", "line3"]

    # Single line
    text = "line1"
    assert split_lines(text) == ["line1"]

    # Empty text
    text = ""
    assert split_lines(text) == []


@pytest.mark.skip()
def test_parse_table_with_header():
    """Test parsing table with header row."""
    text = "name,age,city\nAlice,25,New York\nBob,30,San Francisco"
    result = parse_table(text)

    assert result["headers"] == ["name", "age", "city"]
    assert len(result["data"]) == 2
    assert result["data"][0] == ["Alice", "25", "New York"]
    assert result["separator"] == ","
    assert result["has_header"] is True


def test_parse_table_without_header():
    """Test parsing table without header row."""
    text = "1,2,3\n4,5,6\n7,8,9"
    result = parse_table(text)

    assert result["headers"] == ["col1", "col2", "col3"]
    assert len(result["data"]) == 3
    assert result["data"][0] == ["1", "2", "3"]
    assert result["separator"] == ","
    assert result["has_header"] is False


def test_parse_table_empty():
    """Test parsing empty text."""
    text = ""
    result = parse_table(text)

    assert result["headers"] == []
    assert result["data"] == []
    assert result["separator"] is None
    assert result["has_header"] is False


def test_parse_table_max_rows():
    """Test max rows limit."""
    # Create text with 10 rows
    text = "\n".join([f"{i},{i + 1},{i + 2}" for i in range(10)])

    # Parse with max_rows=5
    result = parse_table(text, max_rows=5)

    assert len(result["data"]) == 5
