#!/usr/bin/env python3
"""
Handler module for decompilation process
"""

import os
import sys
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import List, Tuple

# Add parent directory to path to import helper
sys.path.insert(0, str(Path(__file__).parent.parent))
from helper import ProgressDisplay, SimpleProgress

# Add current directory to path for worker import
sys.path.insert(0, str(Path(__file__).parent))
from worker import decompile_worker


class DecompilerHandler:
    """Handles PYC file decompilation using Python 2.7 subprocess"""

    def __init__(self, python2_path: str = None, verbose: bool = False, num_workers: int = None):
        self.verbose = verbose

        # Set number of worker processes
        if num_workers is None:
            # Default: Use all CPU cores
            self.num_workers = multiprocessing.cpu_count()
        else:
            self.num_workers = max(1, num_workers)

        # Use Python 2.7 from tools/python2 folder
        if python2_path and os.path.exists(python2_path):
            self.python2_exe = python2_path
        else:
            # Use Python 2 from tools/python2 directory
            tools_dir = Path(__file__).parent.parent
            self.python2_exe = str(tools_dir / "python2" / "python.exe")

            if not os.path.exists(self.python2_exe):
                raise RuntimeError(f"Python 2.7 not found at {self.python2_exe}")

        print(f"Using Python 2.7: {self.python2_exe}")
        print(f"Using {self.num_workers} worker processes")

    def find_pyc_files(self, directory: Path, recursive: bool = False) -> List[Path]:
        """Find all .pyc files in the directory"""
        if recursive:
            pyc_files = list(directory.rglob("*.pyc"))
        else:
            pyc_files = list(directory.glob("*.pyc"))

        # Sort for consistent processing order
        pyc_files.sort()
        return pyc_files

    def decompile_files(self, pyc_files: List[Path], remove_pyc: bool = True) -> Tuple[int, int, List]:
        """Decompile multiple .pyc files using multiprocessing"""

        success_count = 0
        failed_count = 0
        failed_files = []

        total = len(pyc_files)

        # Initialize progress display
        progress_display = ProgressDisplay(total) if not self.verbose else SimpleProgress(total)

        print(f"Decompiling {total} files with {self.num_workers} workers...")

        # Prepare arguments for workers
        worker_args = [(self.python2_exe, str(pyc_file)) for pyc_file in pyc_files]

        # Use ProcessPoolExecutor for parallel processing
        with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
            # Submit all decompilation tasks
            future_to_file = {
                executor.submit(decompile_worker, args): Path(args[1])
                for args in worker_args
            }

            # Process completed tasks
            for future in as_completed(future_to_file):
                pyc_file = future_to_file[future]

                # Get relative path for display
                rel_path = pyc_file.name
                try:
                    rel_path = pyc_file.relative_to(Path.cwd())
                except:
                    pass

                try:
                    pyc_file_path, success, result = future.result()
                    pyc_file = Path(pyc_file_path)

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
                                    print(f"\n  x Could not remove {pyc_file}: {e}")
                    else:
                        failed_count += 1
                        failed_files.append((str(rel_path), result))
                        progress_display.update(f"{rel_path} (failed)")
                        if self.verbose:
                            print(f"\n  x Failed: {rel_path} - {result}")

                except Exception as e:
                    failed_count += 1
                    failed_files.append((str(rel_path), str(e)))
                    progress_display.update(f"{rel_path} (error)")
                    if self.verbose:
                        print(f"\n  x Error processing {rel_path}: {e}")

        # Finish progress display
        progress_display.finish()

        return success_count, failed_count, failed_files