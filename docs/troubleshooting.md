# Troubleshooting

## Encoding Issues

If you see garbled characters for file names (especially with non-ASCII characters), the input files might be using a different encoding. The `cdindex` software often used `big5` or `cp950` for Traditional Chinese.

**Solution**: Use the `--encoding` option:

```bash
cdindex-parser mydisk results.csv --encoding big5
```

Or, when using the library:

```python
catalog = parse_catalog("mydisk.IDX", encoding="big5")
```

Common encodings: `utf-16` (default), `big5`, `cp950`, `cp437`.

## Line Count Mismatch

You might see a `LineCountMismatchError`. This means the `.IDX` and `.FILE` files do not have the same number of non-empty lines, which can happen if they are corrupted or incomplete.

**Solution**: The parser relies on a perfect 1:1 line correspondence between the two files. You may need to manually inspect and fix the files to ensure they have the same number of lines.

## Indent Mismatch

You might see an `IndentMismatchError`. This means a `.IDX` line and its corresponding `.FILE` line have different tab indentation levels.

**Solution**: Check that the indentation in your `.IDX` file is consistent and matches the structure expected by the `.FILE` data.

## Malformed Record

You might see a `MalformedRecordError`. This means a line in the `.IDX` or `.FILE` file does not match the expected format (`[D|F]<size>.<timestamp>` for `.FILE` lines).

**Solution**: Inspect the reported line number (included in the exception) and correct the malformed line.

## Incorrect Timestamps

If the timestamps look incorrect (e.g., a wrong year), verify you are using the latest version of the parser. The timestamp format is a 32-bit MS-DOS FAT timestamp (`dosdate`), not a standard Unix timestamp. The current version decodes this correctly.

## Missing File

You might see an `InputNotFoundError`. This means either the `.IDX` or `.FILE` file could not be found.

**Solution**: Ensure both files exist with the same base name (e.g. `mydisk.IDX` and `mydisk.FILE`), and that you passed the correct base name or path to `cdindex-parser`.
