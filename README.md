# CD Index 2 Parser

**CD Index 2 Parser** converts legacy `*.IDX` and `*.FILE` files from CD Index 2 (光碟索引大師) into a modern CSV format, preserving the full file tree structure, sizes, and modification timestamps.

This tool is for anyone who has old CD/DVD index catalogs from this popular legacy software and wants to access them with modern tools.

**➡️ For detailed information, please read the [Full Documentation](docs/index.md).**

## Features

- Parses file and directory structures from `.IDX` and `.FILE` pairs.
- Correctly decodes the 32-bit MS-DOS FAT timestamps.
- Reconstructs full file paths.
- Outputs a clean, usable CSV file.

## Quick Start

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/chriskyfung/cdindex-parser.git
    cd cdindex-parser
    ```

2.  **Run the parser:**
    Place your `.IDX` and `.FILE` files in the directory (e.g., `mydisk.IDX`, `mydisk.FILE`). Then run the script:
    ```bash
    python decode_cdindex.py mydisk results.csv
    ```

This will generate `results.csv` containing the parsed data.

## File Format Overview

The parser processes two files:

-   **`*.IDX`**: Contains file/directory names and structure (via indentation).
-   **`*.FILE`**: Contains properties for each item, in the format `[D|F]<size>.<timestamp>`.

The timestamp is a 32-bit **MS-DOS FAT timestamp (`dosdate`)**, which is handled correctly by the parser.

## License

MIT License. See [LICENSE](LICENSE) for details.
