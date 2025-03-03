"""HTML parsing functionality for extracting tables."""

import html.parser
import re


class HTMLTableParser(html.parser.HTMLParser):
    """Parser for extracting tables from HTML."""

    def __init__(self):
        """Initialize the HTML table parser with empty state variables.

        Sets up the internal state to track tables, rows, cells, and their content
        as the HTML is parsed.
        """
        super().__init__()
        self.tables = []
        self.current_table = None
        self.current_row = None
        self.current_cell = []
        self.in_thead = False
        self.in_tbody = False
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.current_row_has_th = False  # Track if current row has any th elements
        self.current_tags = []  # Track nested tags
        self.reset_cell_on_end = True  # Whether to reset cell content on cell end

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str]]):
        """Process HTML start tags to track table structure.

        This method updates the parser state when encountering opening tags for
        table elements (table, thead, tbody, tr, th, td). It creates new data
        structures for tables and rows as needed.

        Args:
            tag: The HTML tag name
            attrs: List of (name, value) attribute pairs

        """
        if tag == "table":
            # Start a new table
            self.in_table = True
            self.current_table = {"headers": [], "data": [], "has_header": False}

        elif tag == "thead":
            # Mark that we're in a header section
            self.in_thead = True
            self.current_table["has_header"] = True

        elif tag == "tbody":
            # Mark that we're in a body section
            self.in_tbody = True

        elif tag == "tr" and self.in_table:
            # Start a new row
            self.in_row = True
            self.current_row = []
            self.current_row_has_th = False

        elif tag == "th" and self.in_row:
            # Start a header cell
            self.in_cell = True
            self.current_cell = []
            self.current_row_has_th = True  # Mark that this row has a th

        elif tag == "td" and self.in_row:
            # Start a data cell
            self.in_cell = True
            self.current_cell = []

    def handle_endtag(self, tag: str):
        """Process HTML end tags to finalize table elements.

        This method updates the parser state when encountering closing tags.
        It handles the completion of tables, rows, and cells, adding the
        collected data to the appropriate data structures.

        Args:
            tag: The HTML tag name being closed

        """
        # Pop the last tag if it matches
        if self.current_tags and self.current_tags[-1] == tag:
            self.current_tags.pop()

        if tag == "table":
            # End of a table
            if self.current_table:
                # Only add tables that have some content
                if self.current_table["headers"] or self.current_table["data"]:
                    self.tables.append(self.current_table)
            self.in_table = False
            self.current_table = None

        elif tag == "thead":
            # End of header section
            self.in_thead = False

        elif tag == "tbody":
            # End of body section
            self.in_tbody = False

        elif tag == "tr" and self.in_row:
            # End of a row
            if self.in_thead:
                # Add to headers if we're in the thead
                if not self.current_table["headers"]:
                    self.current_table["headers"] = self.current_row
            else:
                # Check if this row should be treated as a header row based on th elements
                if not self.current_table["headers"] and self.current_row_has_th:
                    # This is the first row with th elements, use it as a header
                    self.current_table["has_header"] = True
                    self.current_table["headers"] = self.current_row
                else:
                    # Add to data if not a header row
                    if self.current_row and any(
                        cell.strip() for cell in self.current_row
                    ):
                        self.current_table["data"].append(self.current_row)

            self.in_row = False
            self.current_row = None
            self.current_row_has_th = False

        elif (tag == "th" or tag == "td") and self.in_cell:
            # End of a cell, add the accumulated cell content to the current row
            if self.current_row is not None:
                cell_text = "".join(self.current_cell).strip()
                # Clean up any excess whitespace
                cell_text = re.sub(r"\s+", " ", cell_text).strip()
                self.current_row.append(cell_text)

            self.in_cell = False
            if self.reset_cell_on_end:
                self.current_cell = []


def extract_tables_from_html(
    html: str,
) -> list[dict[str, list[str] | list[list[str]] | bool]]:
    """Extract tables from HTML content.

    Args:
        html: HTML content as string

    Returns:
        List of dictionaries with table data:
        - headers: list of column names
        - data: list of lists (rows)
        - has_header: boolean indicating if a header was detected

    """
    parser = HTMLTableParser()
    parser.feed(html)

    # Merge tables with the same header structure
    merged_tables = []
    current_merged_table = None

    for table in parser.tables:
        # Skip empty tables
        if not table["headers"] and not table["data"]:
            continue

        # If we have a current merged table with matching headers
        if (
            current_merged_table
            and current_merged_table["headers"] == table["headers"]
            and len(current_merged_table["headers"]) > 0
        ):
            # Append data rows to the current merged table
            current_merged_table["data"].extend(table["data"])
        else:
            # Start a new merged table
            if current_merged_table:
                merged_tables.append(current_merged_table)
            current_merged_table = {
                "headers": table["headers"],
                "data": table["data"].copy(),
                "has_header": table["has_header"],
            }

    # Add the last merged table if it exists
    if current_merged_table:
        merged_tables.append(current_merged_table)

    # If we have no merged tables, fall back to the original tables
    result_tables = merged_tables if merged_tables else parser.tables

    # Post-process the tables
    for table in result_tables:
        # If no headers were found but has_header is True, use the first row as headers
        if table["has_header"] and not table["headers"] and table["data"]:
            table["headers"] = table["data"][0]
            table["data"] = table["data"][1:]

        # If no headers were found, create default column names
        if not table["headers"] and table["data"]:
            num_cols = max(len(row) for row in table["data"]) if table["data"] else 0
            table["headers"] = [f"col{i + 1}" for i in range(num_cols)]

        # Clean the data by removing empty rows and ensuring consistent column counts
        if table["data"]:
            # Remove completely empty rows
            table["data"] = [
                row for row in table["data"] if any(cell.strip() for cell in row)
            ]

            # Ensure all rows have the same number of columns as the headers
            header_count = len(table["headers"])
            for i in range(len(table["data"])):
                row = table["data"][i]
                if len(row) < header_count:
                    # Pad with empty strings if row is too short
                    table["data"][i] = row + [""] * (header_count - len(row))
                elif len(row) > header_count:
                    # Truncate if row is too long
                    table["data"][i] = row[:header_count]

    return result_tables


def html_to_parsed_table(
    html: str,
) -> dict[str, list[str] | list[list[str]] | str | bool] | None:
    """Extract the first table from HTML and return it in the parsed_table format.

    Args:
        html: HTML content as string

    Returns:
        Dictionary compatible with datapasta's parse_table result, or None if no tables found

    """
    tables = extract_tables_from_html(html)

    if not tables:
        return None

    # Find the most suitable table - prefer ones with both headers and data
    best_table = None
    for table in tables:
        if table["headers"] and table["data"]:
            best_table = table
            break

    # If we didn't find a table with both headers and data, take the first one
    if best_table is None and tables:
        best_table = tables[0]

    if not best_table:
        return None

    # Convert to datapasta's parsed_table format
    return {
        "headers": best_table["headers"],
        "data": best_table["data"],
        "separator": ",",  # Arbitrary since we're not using a text separator
        "has_header": best_table["has_header"],
    }
