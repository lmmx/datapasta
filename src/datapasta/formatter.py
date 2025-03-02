"""
Format parsed data as Python code (pandas, polars, etc).
"""
import textwrap
from typing import Dict, List, Optional, Union, Any

from datapasta.utils import format_value_for_code

def format_as_polars(parsed_data: Dict[str, Any], indent: int = 4) -> str:
    """
    Format parsed data as Polars DataFrame constructor code.
    
    Args:
        parsed_data (dict): Parsed data from parser.parse_text()
        indent (int): Number of spaces for indentation
        
    Returns:
        str: Python code for creating a Polars DataFrame
    """
    if not parsed_data or not parsed_data.get('data'):
        return "import polars as pl\ndf = pl.DataFrame()"
    
    columns = parsed_data['columns']
    data = parsed_data['data']
    types = parsed_data['types']
    
    # Start with imports
    code_lines = ["import polars as pl", ""]
    code_lines.append("df = pl.DataFrame({")
    
    # Max column name length for alignment
    col_pad = max(len(col) for col in columns) + 2  # +2 for the quotes
    
    # Add each column definition
    for idx, col_name in enumerate(columns):
        col_type = types[idx]
        col_values = [row[idx] if idx < len(row) else None for row in data]
        
        # Format the column name
        formatted_col_name = f'"{col_name}"'
        
        # Format values according to their type
        formatted_values = [format_value_for_code(val, col_type) for val in col_values]
        
        # Join the values with commas
        if len(formatted_values) > 10:
            # For long lists, put first few and last few values with ellipsis
            values_str = ", ".join(formatted_values[:5])
            values_str += ", ..., "
            values_str += ", ".join(formatted_values[-3:])
        else:
            values_str = ", ".join(formatted_values)
        
        # Add the column to the code
        col_def = " " * indent + f'{formatted_col_name.ljust(col_pad)}: [{values_str}],'
        code_lines.append(col_def)
    
    # Close the dictionary and DataFrame constructor
    code_lines.append("})")
    
    return "\n".join(code_lines)

def format_as_pandas(parsed_data: Dict[str, Any], indent: int = 4) -> str:
    """
    Format parsed data as pandas DataFrame constructor code.
    
    Args:
        parsed_data (dict): Parsed data from parser.parse_text()
        indent (int): Number of spaces for indentation
        
    Returns:
        str: Python code for creating a pandas DataFrame
    """
    if not parsed_data or not parsed_data.get('data'):
        return "import pandas as pd\ndf = pd.DataFrame()"
    
    columns = parsed_data['columns']
    data = parsed_data['data']
    types = parsed_data['types']
    
    # Start with imports
    code_lines = ["import pandas as pd", ""]
    code_lines.append("df = pd.DataFrame({")
    
    # Max column name length for alignment
    col_pad = max(len(col) for col in columns) + 2  # +2 for the quotes
    
    # Add each column definition
    for idx, col_name in enumerate(columns):
        col_type = types[idx]
        col_values = [row[idx] if idx < len(row) else None for row in data]
        
        # Format the column name
        formatted_col_name = f'"{col_name}"'
        
        # Format values according to their type
        formatted_values = [format_value_for_code(val, col_type) for val in col_values]
        
        # Join the values with commas
        if len(formatted_values) > 10:
            # For long lists, put first few and last few values with ellipsis
            values_str = ", ".join(formatted_values[:5])
            values_str += ", ..., "
            values_str += ", ".join(formatted_values[-3:])
        else:
            values_str = ", ".join(formatted_values)
        
        # Add the column to the code
        col_def = " " * indent + f'{formatted_col_name.ljust(col_pad)}: [{values_str}],'
        code_lines.append(col_def)
    
    # Close the dictionary and DataFrame constructor
    code_lines.append("})")
    
    return "\n".join(code_lines)

def format_as_vector(parsed_data: Dict[str, Any], vertical: bool = False) -> str:
    """
    Format parsed data as a Python list.
    
    Args:
        parsed_data (dict): Parsed data from parser.parse_text()
        vertical (bool): Whether to format the list vertically
        
    Returns:
        str: Python code for creating a list
    """
    if not parsed_data or not parsed_data.get('data'):
        return "[]"
    
    # Flatten the data into a 1D array
    flattened = []
    for row in parsed_data['data']:
        flattened.extend(row)
    
    # Determine the overall type for the vector
    all_types = [parsed_data['types'][idx % len(parsed_data['types'])] 
                 for idx in range(len(flattened))]
    
    # Format each value
    formatted_values = [format_value_for_code(val, val_type) 
                       for val, val_type in zip(flattened, all_types)]
    
    if vertical:
        # Format vertically with each value on its own line
        result = "[\n    " + ",\n    ".join(formatted_values) + "\n]"
    else:
        # Format horizontally
        result = "[" + ", ".join(formatted_values) + "]"
    
    return result

def format_from_clipboard(format_type: str = 'polars', vertical: bool = False) -> str:
    """
    Read from clipboard, parse, and format as code.
    
    Args:
        format_type (str): Output format: 'polars', 'pandas', or 'list'
        vertical (bool): For vectors, format vertically if True
        
    Returns:
        str: Formatted code
    """
    from datapasta.clipboard import read_clipboard
    from datapasta.parser import parse_text
    
    clipboard_content = read_clipboard()
    if not clipboard_content:
        return ""
    
    parsed = parse_text(clipboard_content)
    
    if format_type.lower() == 'polars':
        return format_as_polars(parsed)
    elif format_type.lower() == 'pandas':
        return format_as_pandas(parsed)
    elif format_type.lower() in ('list', 'vector'):
        return format_as_vector(parsed, vertical)
    else:
        raise ValueError(f"Unknown format type: {format_type}")
