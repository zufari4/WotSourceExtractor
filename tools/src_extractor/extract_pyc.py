#!/usr/bin/env python3
"""
World of Tanks PKG Extractor
Extracts .pyc files from WoT .pkg files (which are ZIP archives)
"""

import argparse
import os
import sys
import shutil
from pathlib import Path

# Add parent directory to path to import helper
sys.path.insert(0, str(Path(__file__).parent.parent))
from helper import ProgressDisplay

from pkg_handler import PKGHandler


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Extract .pyc files from World of Tanks .pkg files'
    )
    parser.add_argument(
        'game_path',
        help='Path to the World of Tanks game directory'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    return parser.parse_args()


def prepare_output_directory():
    """Prepare the res output directory next to tools folder"""
    script_dir = Path(__file__).parent.parent.parent  # Go up to wot_mods
    res_dir = script_dir / 'res'

    if res_dir.exists():
        print(f"Clearing existing res directory: {res_dir}")
        shutil.rmtree(res_dir)

    res_dir.mkdir(exist_ok=True)
    print(f"Output directory ready: {res_dir}")
    return res_dir


def main():
    """Main entry point"""
    args = parse_arguments()

    # Validate game path
    game_path = Path(args.game_path)
    if not game_path.exists():
        print(f"Error: Game path does not exist: {game_path}")
        sys.exit(1)

    packages_dir = game_path / 'res' / 'packages'
    if not packages_dir.exists():
        print(f"Error: Packages directory not found: {packages_dir}")
        sys.exit(1)

    # Prepare output directory
    output_dir = prepare_output_directory()

    # Initialize handler
    handler = PKGHandler(packages_dir, output_dir, verbose=args.verbose)

    # Find PKG files with pyc content
    print("\nScanning for PKG files containing .pyc files...")
    pkg_files = handler.find_pkg_with_pyc()

    if not pkg_files:
        print("No PKG files with .pyc content found.")
        sys.exit(0)

    print(f"Found {len(pkg_files)} PKG files with .pyc content")

    # Get full list of pyc files for progress tracking
    print("\nAnalyzing PKG contents...")
    pyc_files = handler.get_all_pyc_files(pkg_files)
    total_pyc_count = sum(len(files) for files in pyc_files.values())
    print(f"Total .pyc files to extract: {total_pyc_count}")

    # Initialize progress display
    progress = ProgressDisplay(total_pyc_count)

    # Extract pyc files
    print("\nStarting extraction...")
    extracted_count = handler.extract_pyc_files(pkg_files, progress)

    print(f"\n[DONE] Extraction complete!")
    print(f"  Extracted {extracted_count} .pyc files to: {output_dir}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExtraction cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)