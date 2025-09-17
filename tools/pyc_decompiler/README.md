# PYC Decompiler Tool for World of Tanks

This tool decompiles World of Tanks `.pyc` (Python compiled) files to `.py` source files using a custom version of uncompyle6.

## Requirements

- Python 3.x (for running the main script)
- Python 2.7 (must be located in `d:\wot_mods\tools\python2\`)

## Usage

Basic usage - decompile all .pyc files in a directory:
```bash
python tools/pyc_decompiler/decompile_pyc.py <directory>
```

Example - decompile the extracted WoT files:
```bash
python tools/pyc_decompiler/decompile_pyc.py "D:\wot_mods\res"
```

## Options

- `--recursive`, `-r` : Recursively process all subdirectories (recommended)
- `--keep-pyc`, `-k` : Keep original .pyc files after decompilation (by default they are removed)
- `--verbose`, `-v` : Show detailed output including failed files
- `--workers`, `-w` : Number of worker processes (default: CPU cores - 2)
- `--python2` : Specify custom path to Python 2.7 executable (default: `tools\python2\python.exe`)

## Examples

Recursively decompile all .pyc files and remove originals:
```bash
python tools/pyc_decompiler/decompile_pyc.py "D:\wot_mods\res" -r
```

Decompile keeping the original .pyc files:
```bash
python tools/pyc_decompiler/decompile_pyc.py "D:\wot_mods\res" -r -k
```

Decompile with verbose output:
```bash
python tools/pyc_decompiler/decompile_pyc.py "D:\wot_mods\res" -r -v
```

Decompile with 8 worker processes:
```bash
python tools/pyc_decompiler/decompile_pyc.py "D:\wot_mods\res" -r -w 8
```

## How it Works

1. Scans the target directory for `.pyc` files
2. Uses parallel processing with multiple worker processes
3. Each worker uses Python 2.7 subprocess with custom uncompyle6
4. Decompiles each `.pyc` file to a `.py` file in the same location
5. Removes the original `.pyc` file (unless `--keep-pyc` is specified)
6. Shows real-time progress with percentage completion

## File Structure

- `decompile_pyc.py` - Main entry point script
- `handler.py` - DecompilerHandler class for managing decompilation
- `worker.py` - Worker function for parallel processing
- `worker_py2.py` - Python 2.7 worker script for actual decompilation
- `uncompyle6/` - Custom uncompyle6 module modified for WoT bytecode

## Notes

- World of Tanks uses Python 2.7 bytecode (magic number 62211/0xf303)
- The tool uses parallel processing for faster decompilation
- Each file has a 30-second timeout to prevent hanging on problematic files
- Failed files are tracked and can be viewed with the `--verbose` flag
- The decompiled `.py` files are saved in the same directory as the original `.pyc` files

## Troubleshooting

If decompilation fails for some files:
1. Ensure Python 2.7 is installed in `tools\python2\` directory
2. Use `-v` flag to see detailed error messages
3. Some heavily modified or corrupted files may not be decompilable