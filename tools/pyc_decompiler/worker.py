#!/usr/bin/env python3
"""
Worker module for parallel decompilation
"""

import subprocess
import json
from pathlib import Path
from typing import Tuple


def decompile_worker(args: Tuple[str, str]) -> Tuple[str, bool, str]:
    """
    Worker function for decompiling a single file

    Args:
        args: Tuple of (python2_exe, pyc_file_path)

    Returns:
        Tuple of (pyc_file_path, success, result_message)
    """
    import os
    python2_exe, pyc_file_path = args
    pyc_file = Path(pyc_file_path)

    # Create the Python 2 decompilation script
    # Use absolute path for the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    decompile_script = os.path.join(script_dir, "worker_py2.py")

    # Prepare the command - use absolute paths
    cmd = [python2_exe, decompile_script, str(pyc_file.absolute())]

    try:
        # Run Python 2.7 to decompile
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=script_dir
        )

        if result.returncode == 0:
            # Parse the JSON result
            try:
                response = json.loads(result.stdout)
                if response["success"]:
                    return pyc_file_path, True, response["output_file"]
                else:
                    return pyc_file_path, False, response.get("error", "Unknown error")
            except json.JSONDecodeError:
                # Fallback: check if .py file was created
                py_file = pyc_file.with_suffix('.py')
                if py_file.exists():
                    return pyc_file_path, True, str(py_file)
                return pyc_file_path, False, "Failed to parse response"
        else:
            error_msg = result.stderr.strip() if result.stderr else "Decompilation failed"
            return pyc_file_path, False, error_msg

    except subprocess.TimeoutExpired:
        return pyc_file_path, False, "Decompilation timed out"
    except Exception as e:
        return pyc_file_path, False, str(e)