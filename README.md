# World of Tanks Source Extractor

A toolkit for extracting and decompiling Python source code from World of Tanks game files.

## Overview

This project provides tools to:
1. Extract `.pyc` (compiled Python) files from World of Tanks `.pkg` archives
2. Decompile `.pyc` files back to readable `.py` source code

## Requirements

- **Python 3.x** - For running the main tools
- **Python 2.7** - Required for decompilation (must be placed in `tools\python2\`)
- **World of Tanks** - Game installation to extract files from

## Quick Start

### Easy Method (Windows)

Simply run the batch file:
```batch
extract_wot_sources.bat
```

The script will:
1. Check for Python installations
2. Ask for your World of Tanks game path
3. Extract all `.pyc` files from game packages
4. Decompile them to `.py` source files
5. Save everything to the `res\` folder

### Manual Method

#### Step 1: Extract .pyc files
```bash
python tools/src_extractor/extract_pyc.py "D:\Games\Tanki"
```

#### Step 2: Decompile to .py files
```bash
python tools/pyc_decompiler/decompile_pyc.py res -r
```

## Project Structure

```
wot_mods/
├── extract_wot_sources.bat    # One-click extraction script
├── res/                        # Output directory for extracted files
├── tools/
│   ├── python2/               # Python 2.7 installation (required)
│   │   └── python.exe
│   ├── src_extractor/         # PKG extraction tool
│   │   ├── extract_pyc.py    # Main extractor script
│   │   └── pkg_handler.py    # PKG file handler
│   ├── pyc_decompiler/        # PYC decompilation tool
│   │   ├── decompile_pyc.py  # Main decompiler script
│   │   ├── handler.py        # Multiprocessing handler
│   │   ├── worker.py         # Worker process manager
│   │   ├── worker_py2.py     # Python 2.7 worker
│   │   └── uncompyle6/        # Custom WoT decompiler
│   └── helper/                # Shared utilities
│       └── progress_display.py
└── README.md
```

## Tools Documentation

### Source Extractor (`tools/src_extractor`)

Extracts `.pyc` files from World of Tanks `.pkg` archives (ZIP format).

**Usage:**
```bash
python tools/src_extractor/extract_pyc.py <game_path> [-v]
```

**Options:**
- `game_path` - Path to World of Tanks installation
- `-v, --verbose` - Enable verbose output

### PYC Decompiler (`tools/pyc_decompiler`)

Decompiles Python 2.7 bytecode files to source code using a custom uncompyle6 version with multiprocessing support for faster decompilation.

**Usage:**
```bash
python tools/pyc_decompiler/decompile_pyc.py <directory> [options]
```

**Options:**
- `-r, --recursive` - Process subdirectories
- `-k, --keep-pyc` - Keep original .pyc files
- `-v, --verbose` - Show detailed output
- `-w, --workers` - Number of worker processes (default: CPU cores - 2)
- `--python2` - Custom Python 2.7 path

## Technical Details

- World of Tanks uses **Python 2.7** bytecode (magic number: 62211/0xf303)
- `.pkg` files are standard ZIP archives containing compiled Python code
- The decompiler uses a modified uncompyle6 for WoT-specific bytecode
- Cross-Python compatibility achieved through subprocess communication
- **Multiprocessing support** for parallel decompilation (significant speed improvement)
- Default workers: CPU cores - 2 for optimal performance

## Troubleshooting

### "Python 3 is not installed"
Install Python 3 from https://www.python.org/ and add to PATH.

### "Python 2.7 not found at tools\python2\python.exe"
Download Python 2.7 and extract/install to `tools\python2\` directory.

### "Not a valid World of Tanks directory"
Ensure the path points to the game's root directory containing `res\packages`.

### Decompilation failures
Some files may fail due to obfuscation or corruption. Use `-v` flag for details.

## Notes

- Extraction typically processes ~9,500 files
- Decompilation time significantly reduced with multiprocessing (from hours to minutes)
- Uses parallel workers for faster processing of large file sets
- Output preserves the original game's directory structure
- All extracted files are saved to the `res\` directory

## License

This tool is for educational and modding purposes only. Respect Wargaming's Terms of Service.