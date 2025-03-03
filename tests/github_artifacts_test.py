"""Test parsing multiline tables."""

import json
import os

from datapasta.clipboard_targets import parse_multiline_table


def test_parse_multiline_table():
    """Test extraction of tables with multiline row format."""
    # Load the test data
    test_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(test_dir, "fixtures", "github_artifacts.json")) as f:
        data = json.load(f)
        text_content = data.get("UTF8_STRING", "")

    assert text_content, "Test text content should not be empty"

    parsed = parse_multiline_table(text_content)

    # Validate the parsed table
    assert parsed is not None, "Should return a parsed table"
    assert parsed["has_header"] is True, "Should detect header"

    # Check headers
    assert "Name" in parsed["headers"], "Should include 'Name' in headers"
    assert "Size" in parsed["headers"], "Should include 'Size' in headers"

    # Check data content
    assert len(parsed["data"]) >= 3, "Should extract multiple rows"

    # Check for specific row contents (using the same test data)
    artifact_names = [row[0] for row in parsed["data"]]
    assert "wheels-linux-aarch64" in artifact_names, (
        "Should extract first column value correctly"
    )
    assert "wheels-linux-armv7" in artifact_names, (
        "Should extract first column value correctly"
    )
    assert "wheels-linux-ppc64le" in artifact_names, (
        "Should extract first column value correctly"
    )

    # Check for specific values in the second column
    size_by_artifact = {row[0]: row[1] for row in parsed["data"]}
    assert "4.2 MB" in size_by_artifact["wheels-linux-aarch64"], (
        "Should extract second column value correctly"
    )
    assert "3.78 MB" in size_by_artifact["wheels-linux-armv7"], (
        "Should extract second column value correctly"
    )
    assert "4.63 MB" in size_by_artifact["wheels-linux-ppc64le"], (
        "Should extract second column value correctly"
    )


def test_full_multiline_table_workflow():
    """Test the full workflow for multiline tables using clipboard targets data."""
    from datapasta.clipboard_targets import clipboard_with_targets_to_parsed_table

    # Mock the cliptargets module
    class MockCliptargets:
        @staticmethod
        def get_all_targets():
            test_dir = os.path.dirname(os.path.abspath(__file__))
            with open(os.path.join(test_dir, "fixtures", "github_artifacts.json")) as f:
                return json.load(f)

    # Store the original import function
    original_import = __import__

    # Define a mock import function
    def mock_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "cliptargets":
            return MockCliptargets
        return original_import(name, globals, locals, fromlist, level)

    # Replace the built-in import function
    import builtins

    builtins.__import__ = mock_import

    try:
        # Call the function to be tested
        parsed = clipboard_with_targets_to_parsed_table()

        # Verify the results
        assert parsed is not None, "Should return a parsed table"
        assert parsed["has_header"] is True, "Should detect header"
        assert "Name" in parsed["headers"], "Should include 'Name' in headers"
        assert "Size" in parsed["headers"], "Should include 'Size' in headers"

        # Check for specific data content
        artifact_names = [row[0] for row in parsed["data"]]
        assert len(artifact_names) >= 3, "Should extract multiple rows"
        assert "wheels-linux-aarch64" in artifact_names, (
            "Should extract first column value correctly"
        )
        assert "wheels-linux-armv7" in artifact_names, (
            "Should extract first column value correctly"
        )

        # Check if we have the correct number of columns (should be exactly 2: Name and Size)
        assert len(parsed["headers"]) == 2, "Should extract exactly 2 columns"
        assert all(len(row) == 2 for row in parsed["data"]), (
            "All rows should have exactly 2 values"
        )

    finally:
        # Restore the original import function
        builtins.__import__ = original_import
