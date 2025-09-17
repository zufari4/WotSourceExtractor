#!/usr/bin/env python3
"""
PYC Decompiler Tool - Python 3 Wrapper
Uses Python 2.7 subprocess for actual decompilation of WoT files
"""

import argparse
import sys
import os
import subprocess
import json
from pathlib import Path
from typing import List, Tuple

# Add parent directory to path to import helper
sys.path.insert(0, str(Path(__file__).parent.parent))
from helper import ProgressDisplay, SimpleProgress


class DecompilerHandler:
    """Handles PYC file decompilation using Python 2.7 subprocess"""

    def __init__(self, python2_path: str = None, verbose: bool = False):
        self.verbose = verbose

        # Use Python 2.7 from tools/python2 folder
        if python2_path and os.path.exists(python2_path):
            self.python2_exe = python2_path
        else:
            # Use Python 2 from tools/python2 directory
            tools_dir = Path(__file__).parent.parent
            self.python2_exe = str(tools_dir / "python2" / "python.exe")

            if not os.path.exists(self.python2_exe):
                raise RuntimeError(f"Python 2.7 not found at {self.python2_exe}")

        if self.verbose:
            print(f"Using Python 2.7: {self.python2_exe}")


    def find_pyc_files(self, directory: Path, recursive: bool = False) -> List[Path]:
        """Find all .pyc files in the directory"""
        if recursive:
            pyc_files = list(directory.rglob("*.pyc"))
        else:
            pyc_files = list(directory.glob("*.pyc"))

        # Sort for consistent processing order
        pyc_files.sort()
        return pyc_files

    def decompile_single_file(self, pyc_file: Path) -> Tuple[bool, str]:
        """Decompile a single .pyc file using Python 2.7"""

        # Create the Python 2 decompilation script
        decompile_script = Path(__file__).parent / "worker_py2.py"

        # Prepare the command
        cmd = [
            self.python2_exe,
            str(decompile_script),
            str(pyc_file)
        ]

        try:
            # Run Python 2.7 to decompile
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(Path(__file__).parent)
            )

            if result.returncode == 0:
                # Parse the JSON result
                try:
                    response = json.loads(result.stdout)
                    if response["success"]:
                        return True, response["output_file"]
                    else:
                        return False, response.get("error", "Unknown error")
                except json.JSONDecodeError:
                    # Fallback: check if .py file was created
                    py_file = pyc_file.with_suffix('.py')
                    if py_file.exists():
                        return True, str(py_file)
                    return False, "Failed to parse response"
            else:
                error_msg = result.stderr.strip() if result.stderr else "Decompilation failed"
                return False, error_msg

        except subprocess.TimeoutExpired:
            return False, "Decompilation timed out"
        except Exception as e:
            return False, str(e)

    def decompile_files(self, pyc_files: List[Path], remove_pyc: bool = True) -> Tuple[int, int, List]:
        """Decompile multiple .pyc files"""

        success_count = 0
        failed_count = 0
        failed_files = []

        total = len(pyc_files)

        # Initialize progress display
        progress_display = ProgressDisplay(total) if not self.verbose else SimpleProgress(total)

        for pyc_file in pyc_files:
            # Get relative path for display
            rel_path = pyc_file.name
            try:
                rel_path = pyc_file.relative_to(Path.cwd())
            except:
                pass

            # Decompile the file
            success, result = self.decompile_single_file(pyc_file)

            if success:
                success_count += 1
                # Update progress
                progress_display.update(str(rel_path))

                # Remove original .pyc file if requested
                if remove_pyc:
                    try:
                        pyc_file.unlink()
                    except Exception as e:
                        if self.verbose:
                            print(f"\n  ✗ Could not remove {pyc_file}: {e}")
            else:
                failed_count += 1
                failed_files.append((str(rel_path), result))
                progress_display.update(f"{rel_path} (failed)")
                if self.verbose:
                    print(f"\n  ✗ Failed: {rel_path} - {result}")

        # Finish progress display
        progress_display.finish()

        return success_count, failed_count, failed_files


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

    try:
        # Initialize handler
        handler = DecompilerHandler(
            python2_path=args.python2,
            verbose=args.verbose
        )
    except RuntimeError as e:
        print(f"Error: {e}")
        print("\nPlease specify Python 2.7 path with --python2 option")
        print("Example: --python2 d:\\wot_mods\\tools\\python2\\python.exe")
        sys.exit(1)

    print()

    # Find all .pyc files
    print("Scanning for .pyc files...")
    pyc_files = handler.find_pyc_files(target_dir, recursive=args.recursive)

    if not pyc_files:
        print("No .pyc files found.")
        sys.exit(0)

    print(f"Found {len(pyc_files)} .pyc files")
    print()

    # Decompile files
    print("Starting decompilation...")
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
        for file_path, error in failed_files:
            print(f"  - {file_path}: {error}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDecompilation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)