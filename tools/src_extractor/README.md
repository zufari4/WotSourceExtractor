# World of Tanks PYC Extractor

This tool extracts `.pyc` (Python compiled) files from World of Tanks `.pkg` files.

## Usage

```bash
python extract_pyc.py <path_to_wot_game>
```

Example:
```bash
python extract_pyc.py "D:\Games\Tanki"
```

## Options

- `--verbose`, `-v` : Enable verbose output to see detailed processing information

## How it Works

The script will:
1. Scan the `\res\packages` directory for `.pkg` files
2. Identify which `.pkg` files contain `.pyc` files
3. Extract only the `.pyc` files to a `res` folder at the root level (`d:\wot_mods\res\`)
4. Show a progress bar with current status, elapsed time, and ETA

## Extraction Logic

- For `scripts.pkg`: Files are extracted with their original paths (e.g., `scripts/client/...`)
- For all other packages: The first folder (package name) is stripped
  - `abc_tester/scripts/...` → `scripts/...`
  - `armory_yard/scripts/...` → `scripts/...`
- This creates a unified file structure matching the game's expected layout

## File Structure

- `extract_pyc.py` - Main script entry point
- `pkg_handler.py` - Handles PKG file operations (scanning and extraction)
- `progress_display.py` - Progress bar and status display

## Notes

- `.pkg` files in World of Tanks are ZIP archives
- The script will clear the output `res` directory if it already exists
- Press Ctrl+C to cancel the extraction at any time
- The extraction preserves the game's directory structure for proper module imports