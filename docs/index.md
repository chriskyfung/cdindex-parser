# Welcome to CD Index 2 Parser Documentation

**CD Index 2 Parser** is a tool to convert legacy `*.IDX` (file tree) and `*.FILE` (properties) files from the CD Index 2 (光碟索引大師) software into modern, usable formats like CSV or JSON.

This documentation will guide you through installation, usage, and provide details about the file format and API.

## Features

- Parses tab-indented tree structures from `.IDX` files.
- Decodes file and directory properties from `.FILE` files.
- Correctly interprets the 32-bit FAT (MS-DOS) timestamps.
- Reconstructs full file paths from the original indented structure.
- Supports encodings like Big5 for Traditional Chinese file names.
- Can output to CSV and JSON.
