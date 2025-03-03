"""Test parsing GitHub artifacts tables."""

import json
import os

from datapasta.clipboard_targets import extract_table_from_github_artifacts_text


def test_extract_table_from_github_artifacts_text():
    """Test extraction of table from GitHub artifacts plain text format."""
    # Load the test data
    test_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(test_dir, "fixtures", "github_artifacts.json")) as f:
        data = json.load(f)
        text_content = data.get("UTF8_STRING", "")

    assert text_content, "Test text content should not be empty"

    parsed = extract_table_from_github_artifacts_text(text_content)

    # Validate the parsed table
    assert parsed is not None, "Should return a parsed table"
    assert parsed["has_header"] is True, "Should detect header"

    # Check headers
    assert "Name" in parsed["headers"], "Should include 'Name' in headers"
    assert "Size" in parsed["headers"], "Should include 'Size' in headers"

    # Check data content
    assert len(parsed["data"]) >= 3, "Should extract multiple rows"

    # Check for specific artifacts
    artifact_names = [row[0] for row in parsed["data"]]
    assert "wheels-linux-aarch64" in artifact_names, "Should extract aarch64 artifact"
    assert "wheels-linux-armv7" in artifact_names, "Should extract armv7 artifact"
    assert "wheels-linux-ppc64le" in artifact_names, "Should extract ppc64le artifact"

    # Check for specific sizes
    size_by_artifact = {row[0]: row[1] for row in parsed["data"]}
    assert "4.2 MB" in size_by_artifact["wheels-linux-aarch64"], (
        "Should have correct size for aarch64"
    )
    assert "3.78 MB" in size_by_artifact["wheels-linux-armv7"], (
        "Should have correct size for armv7"
    )
    assert "4.63 MB" in size_by_artifact["wheels-linux-ppc64le"], (
        "Should have correct size for ppc64le"
    )


def test_full_github_artifacts_workflow():
    """Test the full workflow for GitHub artifacts using clipboard targets data."""
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

        # Check for specific artifacts
        artifact_names = [row[0] for row in parsed["data"]]
        assert len(artifact_names) >= 3, "Should extract multiple artifacts"
        assert "wheels-linux-aarch64" in artifact_names, (
            "Should extract aarch64 artifact"
        )
        assert "wheels-linux-armv7" in artifact_names, "Should extract armv7 artifact"

    finally:
        # Restore the original import function
        builtins.__import__ = original_import
