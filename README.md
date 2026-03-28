# BAF Archive Tools

This repository contains Python scripts for extracting and packing BAF.

## Scripts

### BafExtract.py
Extracts DDS (DirectDraw Surface) texture files from a BAF archive.

**Usage:**
```
python BafExtract.py <input_baf_file> <output_folder>
```

- `<input_baf_file>`: Path to the BAF file to extract from.
- `<output_folder>`: Directory where extracted DDS files will be saved.

**Example:**
```
python BafExtract.py AcidBubble.baf output
```
This extracts all DDS files from `AcidBubble.baf` into the `output/` folder, naming them `_1.dds`, `_2.dds`, etc.

### BafPack.py
Packs DDS files back into a BAF archive. Requires the original BAF file for structure reference.

**Usage:**
```
python BafPack.py <input_baf_file> <dds_folder>
```

- `<input_baf_file>`: Path to the original BAF file (used for structure).
- `<dds_folder>`: Directory containing the DDS files to pack (named `_1.dds`, `_2.dds`, etc.).

**Example:**
```
python BafPack.py AcidBubble.baf output
```
This packs the DDS files from `output/` back into a new BAF file named `AcidBubble_new.baf`.

## Requirements

- Python 3.x
- No external dependencies (uses built-in `struct`, `zlib`, `os`, `sys`)

## Notes

- Keep the edited DDS files the same size as the OG ones
- The scripts assume DDS files are named sequentially starting from `_1.dds`.
- The packing script preserves the original archive structure and replaces file data.
- If DDS file sizes don't match the expected sizes, a warning will be printed.
- The output BAF file from packing will have the same compression and structure as the original.

## Troubleshooting

- Ensure the input BAF file exists and is not corrupted.
- Make sure the output folder exists or can be created.
- For packing, ensure all required DDS files are present in the specified folder.
- If you encounter permission errors, run the script with appropriate permissions or in a writable directory.

## License

These scripts are provided as-is for educational and archival purposes.
