# API Reference

The core parsing logic is contained in the `decode_cdindex.py` script. You can import its functions to use in your own projects.

## Functions

### `parse_file_line(line)`

Parses a single line from a `.FILE` file.

- **Parameters**: `line` (str) - A single line from a `.FILE` file.
- **Returns**: A dictionary with keys `indent`, `type`, `size`, `ts`, `ts_str`.

### `parse_name_line(line)`

Parses a single line from an `.IDX` file.

- **Parameters**: `line` (str) - A single line from an `.IDX` file.
- **Returns**: A dictionary with keys `indent`, `name`.

### `match_and_dump(input_path, out_path)`

The main function that reads a pair of `.IDX` and `.FILE` files, processes them, and writes the output to a CSV file.

- **Parameters**:
    - `input_path` (str): The base path of the input files (without extension).
    - `out_path` (str): The path to the output CSV file.
