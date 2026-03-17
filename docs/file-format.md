# CD Index File Format

The CD Index 2 software uses a pair of files with the same base name to store the index: `*.IDX` and `*.FILE`.

## `*.IDX` (Names & Structure)

This file contains the names of files and directories, with their hierarchy represented by tab indentation.

**Example**:
```plaintext
Root Folder
    File 1-1.txt
    File 1-2.txt
    Sub Folder 1
        File 2-1.txt
```

## `*.FILE` (Properties)

This file stores properties for each corresponding line in the `.IDX` file. Each line follows the format `[D|F]<size>.<timestamp>`.

- `D`: Indicates a directory.
- `F`: Indicates a file.
- `<size>`: The size of the file in bytes. For directories, this is usually 0.
- `<timestamp>`: A 32-bit integer representing the file's modification time.

**Example**:
```plaintext
D0.1334278694
    F226.1334278694
    F528.1334278694
```

### Timestamp Format

The timestamp is a 32-bit integer in the **MS-DOS FAT timestamp** format (`dosdate`). This format stores the date and time as bit fields, relative to an epoch of **1980-01-01**.

The 32-bit integer is composed of two 16-bit parts:
- **Time (lower 16 bits)**
- **Date (upper 16 bits)**

#### Decoding the Timestamp

Here is how the date and time components are extracted from the integer:

```python
# ts is the 32-bit integer timestamp
dos_time = ts & 0xFFFF
dos_date = ts >> 16

# Time decoding
sec = (dos_time & 0x1F) * 2  # 5 bits for seconds (in 2-second intervals)
minute = (dos_time >> 5) & 0x3F # 6 bits for minutes
hour = dos_time >> 11          # 5 bits for hours

# Date decoding
day = dos_date & 0x1F          # 5 bits for day
month = (dos_date >> 5) & 0xF    # 4 bits for month
year = (dos_date >> 9) + 1980  # 7 bits for year (offset from 1980)
```

For example, the timestamp `1130591439` is decoded as `2013-11-03 14:38:30`.
