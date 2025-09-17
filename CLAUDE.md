# Instructions for Claude AI

This document contains important information about the World of Tanks Source Extractor project.

## Project Overview

This is a toolkit for extracting and decompiling Python source code from World of Tanks. The project consists of two main tools:
1. **src_extractor** - Extracts .pyc files from .pkg archives
2. **pyc_decompiler** - Decompiles .pyc files to .py source code

## Key Technical Details

### Python Version Requirements
- **Python 3.x** runs the main scripts
- **Python 2.7** is REQUIRED for decompilation (located in `tools\python2\`)
- World of Tanks uses Python 2.7 bytecode (magic number: 62211/0xf303)

### Important Implementation Notes

1. **Unicode/Encoding Issues**: Windows console has issues with Unicode characters. Use ASCII characters only:
   - Use `#` instead of `█` for progress bars
   - Use `[DONE]` instead of `✓` for success messages
   - Use `x` instead of `✗` for error messages

2. **Path Handling**: The Python 2.7 executable is hardcoded to `tools\python2\python.exe`

3. **Cross-Python Communication**: The decompiler uses JSON for communication between Python 3 wrapper and Python 2.7 worker

## Project Structure

```
wot_mods/
├── extract_wot_sources.bat    # Main batch script for users
├── res/                        # Output directory (created during extraction)
├── tools/
│   ├── python2/               # Python 2.7 installation
│   ├── src_extractor/         # Extraction tool
│   ├── pyc_decompiler/        # Decompilation tool
│   │   ├── uncompyle6/        # Custom WoT-compatible decompiler
│   │   ├── decompile_pyc.py  # Python 3 wrapper
│   │   └── worker_py2.py     # Python 2.7 worker
│   └── helper/                # Shared utilities
```

## Common Tasks

### Running the Full Pipeline
```bash
# Windows batch file
extract_wot_sources.bat

# Or manually:
python tools/src_extractor/extract_pyc.py "D:\Games\Tanki"
python tools/pyc_decompiler/decompile_pyc.py res -r
```

### Testing Decompilation
```bash
# Test on a single file
python tools/pyc_decompiler/decompile_pyc.py res/scripts/client/Account.pyc
```

## Important Files

- `tools/pyc_decompiler/uncompyle6/` - Custom version of uncompyle6, DO NOT replace with standard version
- `tools/helper/progress_display.py` - Shared progress bar implementation
- `extract_wot_sources.bat` - User-facing batch script with all checks

## Known Issues & Solutions

1. **"charmap codec can't encode"** - Replace Unicode characters with ASCII
2. **"No module named 'imp'"** - Python 3.12+ removed imp module, handled in custom uncompyle6
3. **"AST object has no attribute 'kind'"** - Fixed in custom uncompyle6
4. **Progress bar duplication** - Fixed by using carriage return and terminal width padding

## Development Guidelines

1. Always maintain Python 2/3 compatibility
2. Test extraction and decompilation after any changes
3. Keep progress displays user-friendly
4. Handle errors gracefully with clear messages
5. Preserve the original WoT directory structure in output

## Typical Workflow

1. User runs `extract_wot_sources.bat`
2. Script checks Python 3 and Python 2.7 availability
3. User enters WoT game path (e.g., "D:\Games\Tanki")
4. Extraction processes ~20 .pkg files (~9,500 .pyc files total)
5. Decompilation converts all .pyc to .py (may take 10-30 minutes)
6. Results saved in `res\` directory

## Performance Expectations

- Extraction: 1-2 minutes for ~9,500 files
- Decompilation: 10-30 minutes depending on system
- Total size: ~100-200 MB of source code

## Do NOT Modify

- The custom uncompyle6 implementation (it's specifically modified for WoT)
- The Python 2.7 requirement (WoT bytecode is Python 2.7 only)
- The JSON communication protocol between Python versions