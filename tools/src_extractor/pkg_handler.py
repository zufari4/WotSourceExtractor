"""
PKG Handler Module
Handles scanning and extracting .pyc files from World of Tanks .pkg files
"""

import os
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Set


class PKGHandler:
    """Handles PKG file operations"""

    def __init__(self, packages_dir: Path, output_dir: Path, verbose: bool = False):
        self.packages_dir = packages_dir
        self.output_dir = output_dir
        self.verbose = verbose

    def find_pkg_with_pyc(self) -> List[Path]:
        """Find all PKG files that contain .pyc files"""
        pkg_files_with_pyc = []

        # Get all .pkg files
        pkg_files = list(self.packages_dir.glob("*.pkg"))

        if self.verbose:
            print(f"Found {len(pkg_files)} PKG files total")

        for pkg_file in pkg_files:
            try:
                # PKG files are ZIP archives
                with zipfile.ZipFile(pkg_file, 'r') as zf:
                    # Check if it contains any .pyc files
                    pyc_files = [f for f in zf.namelist() if f.endswith('.pyc')]
                    if pyc_files:
                        pkg_files_with_pyc.append(pkg_file)
                        if self.verbose:
                            print(f"  + {pkg_file.name}: {len(pyc_files)} .pyc files")
            except zipfile.BadZipFile:
                if self.verbose:
                    print(f"  x {pkg_file.name}: Not a valid ZIP file")
            except Exception as e:
                if self.verbose:
                    print(f"  x {pkg_file.name}: Error - {e}")

        return pkg_files_with_pyc

    def get_all_pyc_files(self, pkg_files: List[Path]) -> Dict[Path, List[str]]:
        """Get a complete list of all .pyc files in the given PKG files"""
        pyc_files_map = {}

        for pkg_file in pkg_files:
            try:
                with zipfile.ZipFile(pkg_file, 'r') as zf:
                    pyc_files = [f for f in zf.namelist() if f.endswith('.pyc')]
                    pyc_files_map[pkg_file] = pyc_files
            except Exception as e:
                if self.verbose:
                    print(f"Error reading {pkg_file.name}: {e}")
                pyc_files_map[pkg_file] = []

        return pyc_files_map

    def extract_pyc_files(self, pkg_files: List[Path], progress) -> int:
        """Extract only .pyc files from the PKG files"""
        total_extracted = 0

        for pkg_file in pkg_files:
            pkg_name = pkg_file.stem  # Get filename without extension
            progress.update_current_pkg(pkg_file.name)

            try:
                with zipfile.ZipFile(pkg_file, 'r') as zf:
                    # Get list of .pyc files
                    pyc_files = [f for f in zf.namelist() if f.endswith('.pyc')]

                    for pyc_file in pyc_files:
                        # For scripts.pkg, extract as-is
                        # For all other packages, skip the first folder (package name)
                        if pkg_name == "scripts":
                            # Keep original path for scripts.pkg
                            clean_path = pyc_file
                        else:
                            # Skip first folder for other packages
                            path_parts = pyc_file.replace('\\', '/').split('/')
                            if len(path_parts) > 1:
                                clean_path = '/'.join(path_parts[1:])
                            else:
                                clean_path = pyc_file

                        # Create output path
                        output_path = self.output_dir / clean_path.replace('/', os.sep)
                        output_path.parent.mkdir(parents=True, exist_ok=True)

                        # Extract the file
                        try:
                            with zf.open(pyc_file) as source:
                                with open(output_path, 'wb') as target:
                                    shutil.copyfileobj(source, target)

                            total_extracted += 1
                            progress.update(clean_path)

                        except Exception as e:
                            if self.verbose:
                                print(f"\nError extracting {pyc_file}: {e}")

            except Exception as e:
                if self.verbose:
                    print(f"\nError processing {pkg_file.name}: {e}")

        progress.finish()
        return total_extracted

    def extract_all_then_filter(self, pkg_files: List[Path], progress) -> int:
        """Alternative method: Extract all files then delete non-.pyc files"""
        total_extracted = 0

        for pkg_file in pkg_files:
            pkg_name = pkg_file.stem
            pkg_output_dir = self.output_dir / pkg_name
            progress.update_current_pkg(pkg_file.name)

            try:
                # Extract all files to temp directory first
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)

                    with zipfile.ZipFile(pkg_file, 'r') as zf:
                        # Get list of .pyc files for progress tracking
                        pyc_files = [f for f in zf.namelist() if f.endswith('.pyc')]

                        # Extract all
                        zf.extractall(temp_path)

                        # Move only .pyc files to final destination
                        for root, dirs, files in temp_path.walk():
                            for file in files:
                                if file.endswith('.pyc'):
                                    source_file = root / file
                                    rel_path = source_file.relative_to(temp_path)
                                    dest_file = pkg_output_dir / rel_path

                                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                                    shutil.move(str(source_file), str(dest_file))

                                    total_extracted += 1
                                    progress.update(str(rel_path))

            except Exception as e:
                if self.verbose:
                    print(f"\nError processing {pkg_file.name}: {e}")

        progress.finish()
        return total_extracted