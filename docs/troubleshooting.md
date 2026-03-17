# Troubleshooting

### Encoding Issues

If you see garbled characters for file names (especially with non-ASCII characters), the input files might be using a different encoding. The `cdindex` software often used `big5` or `cp950` for Traditional Chinese.

**Solution**: You may need to modify the script to open files with a different encoding. In `decode_cdindex.py`, change `encoding='utf-16'` to `encoding='big5'` or `encoding='cp950'` in the `open()` calls.

### Line Count Mismatch

You might see an `AssertionError: line count mismatch`. This means the `.IDX` and `.FILE` files do not have the same number of lines, which can happen if they are corrupted or incomplete.

**Solution**: The parser relies on a perfect 1:1 line correspondence. You may need to manually inspect and fix the files to ensure they have the same number of lines.

### Incorrect Timestamps

If the timestamps look incorrect (e.g., a wrong year), ensure you are using the latest version of the script. The timestamp format is a 32-bit MS-DOS FAT timestamp, not a standard Unix timestamp. The current version of the parser handles this correctly.
