"""PyPasta Examples.

This file demonstrates various ways to use the PyPasta package.
Run this file to see examples of PyPasta in action.
"""

import datapasta

# Example 1: Basic usage - converting clipboard data to pandas DataFrame code
print("\n=== Example 1: Clipboard to Pandas ===")
try:
    pandas_code = datapasta.clipboard_to_pandas()
    print(pandas_code)
except Exception as e:
    print(f"Error: {e}")

# Example 2: Converting text directly to DataFrame code
print("\n=== Example 2: Text to Pandas ===")
sample_csv = """name,age,city
Alice,25,New York
Bob,30,San Francisco
Charlie,35,Seattle"""

pandas_code = datapasta.text_to_pandas(sample_csv)
print(pandas_code)

# Example 3: Converting text to polars DataFrame code
print("\n=== Example 3: Text to Polars ===")
polars_code = datapasta.text_to_polars(sample_csv)
print(polars_code)

# Example 4: Handling different separators
print("\n=== Example 4: Tab-separated data ===")
sample_tsv = """name\tage\tcity
Alice\t25\tNew York
Bob\t30\tSan Francisco
Charlie\t35\tSeattle"""

# Let the package auto-detect the separator
pandas_code = datapasta.text_to_pandas(sample_tsv)
print(pandas_code)

# Example 5: Mixed data types
print("\n=== Example 5: Mixed data types ===")
mixed_data = """product,price,in_stock,last_updated
Laptop,1299.99,true,2023-01-15
Phone,799.00,true,2023-02-20
Headphones,149.95,false,2023-03-05"""

pandas_code = datapasta.text_to_pandas(mixed_data)
print(pandas_code)

# Example 6: Pipe-separated data
print("\n=== Example 6: Pipe-separated data ===")
pipe_data = """name|department|salary|hire_date
John Smith|Engineering|85000|2020-05-12
Sarah Jones|Marketing|75000|2021-03-15
Michael Brown|Finance|95000|2019-10-01"""

pandas_code = datapasta.text_to_pandas(pipe_data)
print(pandas_code)

# Example 7: Data without headers
print("\n=== Example 7: Data without headers ===")
no_header_data = """1,Red,Small,5.99
2,Blue,Medium,6.99
3,Green,Large,7.99
4,Yellow,X-Large,8.99"""

pandas_code = datapasta.text_to_pandas(no_header_data)
print(pandas_code)

# Example 8: Using with specific separator
print("\n=== Example 8: Forcing a specific separator ===")
pandas_code = datapasta.text_to_pandas(pipe_data, separator="|")
print(pandas_code)
