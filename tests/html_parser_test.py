"""Test HTML parsing functionality."""

import pytest

from datapasta.html_parser import extract_tables_from_html, html_to_parsed_table


@pytest.mark.skip()
def test_extract_tables_from_html_with_thead():
    """Test extracting tables with explicit thead element."""
    html = """
    <table>
        <thead>
            <tr><th>Name</th><th>Age</th><th>City</th></tr>
        </thead>
        <tbody>
            <tr><td>Alice</td><td>25</td><td>New York</td></tr>
            <tr><td>Bob</td><td>30</td><td>San Francisco</td></tr>
        </tbody>
    </table>
    """

    tables = extract_tables_from_html(html)

    assert len(tables) == 1
    table = tables[0]

    assert table["has_header"] is True
    assert table["headers"] == ["Name", "Age", "City"]
    assert len(table["data"]) == 2
    assert table["data"][0] == ["Alice", "25", "New York"]
    assert table["data"][1] == ["Bob", "30", "San Francisco"]


@pytest.mark.skip()
def test_extract_tables_from_html_without_thead():
    """Test extracting tables without explicit thead element."""
    html = """
    <table>
        <tr><td>Name</td><td>Age</td><td>City</td></tr>
        <tr><td>Alice</td><td>25</td><td>New York</td></tr>
        <tr><td>Bob</td><td>30</td><td>San Francisco</td></tr>
    </table>
    """

    tables = extract_tables_from_html(html)

    assert len(tables) == 1
    table = tables[0]

    # Without thead, auto-detection won't mark this as having a header
    assert table["has_header"] is False


@pytest.mark.skip()
def test_extract_tables_from_html_with_th_elements():
    """Test extracting tables with th elements but no thead."""
    html = """
    <table>
        <tr><th>Name</th><th>Age</th><th>City</th></tr>
        <tr><td>Alice</td><td>25</td><td>New York</td></tr>
        <tr><td>Bob</td><td>30</td><td>San Francisco</td></tr>
    </table>
    """

    tables = extract_tables_from_html(html)

    assert len(tables) == 1
    table = tables[0]

    # Should detect header based on th elements
    assert table["has_header"] is True
    assert table["headers"] == ["Name", "Age", "City"]
    assert len(table["data"]) == 2


@pytest.mark.skip()
def test_html_to_parsed_table():
    """Test converting HTML to parsed table format."""
    html = """
    <table>
        <thead>
            <tr><th>Name</th><th>Age</th><th>City</th></tr>
        </thead>
        <tbody>
            <tr><td>Alice</td><td>25</td><td>New York</td></tr>
            <tr><td>Bob</td><td>30</td><td>San Francisco</td></tr>
        </tbody>
    </table>
    """

    parsed = html_to_parsed_table(html)

    assert parsed is not None
    assert parsed["headers"] == ["Name", "Age", "City"]
    assert len(parsed["data"]) == 2
    assert parsed["has_header"] is True
    assert parsed["separator"] == ","


def test_html_to_parsed_table_empty():
    """Test converting HTML with no tables to parsed table format."""
    html = "<div>No tables here</div>"

    parsed = html_to_parsed_table(html)

    assert parsed is None
