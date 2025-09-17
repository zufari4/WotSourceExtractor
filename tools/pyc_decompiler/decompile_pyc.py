#!/usr/bin/env python3
"""
PYC Decompiler Tool - Main Entry Point
Uses Python 2.7 subprocess for actual decompilation of WoT files
"""

import argparse
import sys
from pathlib import Path

# Add current directory to path for handler import
sys.path.insert(0, str(Path(__file__).parent))
from handler import DecompilerHandler


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Decompile .pyc files using Python 2.7 for WoT compatibility'
    )
    parser.add_argument(
        'directory',
        help='Directory containing .pyc files to decompile'
    )
    parser.add_argument(
        '--keep-pyc', '-k',
        action='store_true',
        help='Keep original .pyc files after decompilation'
    )
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Recursively process subdirectories'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--python2',
        help='Path to Python 2.7 executable',
        default=None
    )
    parser.add_argument(
        '--workers', '-w',
        type=int,
        help='Number of worker processes (default: all CPU cores)',
        default=None
    )
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_arguments()

    # Validate directory
    target_dir = Path(args.directory)
    if not target_dir.exists():
        print(f"Error: Directory does not exist: {target_dir}")
        sys.exit(1)

    if not target_dir.is_dir():
        print(f"Error: Not a directory: {target_dir}")
        sys.exit(1)

    print(f"Target directory: {target_dir.absolute()}")
    print(f"Recursive: {args.recursive}")
    print(f"Keep .pyc files: {args.keep_pyc}")
    print()

    try:
        # Initialize handler
        handler = DecompilerHandler(
            python2_path=args.python2,
            verbose=args.verbose,
            num_workers=args.workers
        )
    except RuntimeError as e:
        print(f"Error: {e}")
        print("\nPlease ensure Python 2.7 is installed in tools\\python2\\")
        sys.exit(1)

    # Find all .pyc files
    print("Scanning for .pyc files...")
    pyc_files = handler.find_pyc_files(target_dir, recursive=args.recursive)

    if not pyc_files:
        print("No .pyc files found.")
        sys.exit(0)

    print(f"Found {len(pyc_files)} .pyc files")
    print()

    # Decompile files
    success_count, failed_count, failed_files = handler.decompile_files(
        pyc_files,
        remove_pyc=not args.keep_pyc
    )

    # Print summary
    print(f"\n[DONE] Decompilation complete!")
    print(f"  Successfully decompiled: {success_count} files")
    if failed_count > 0:
        print(f"  Failed: {failed_count} files")

    if failed_files and args.verbose:
        print("\nFailed files:")
        for file_path, error in failed_files[:20]:  # Show first 20 failures
            print(f"  - {file_path}: {error}")
        if len(failed_files) > 20:
            print(f"  ... and {len(failed_files) - 20} more")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDecompilation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)