#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Python 2.7 Worker Script
Called by Python 3 wrapper to decompile .pyc files
"""

from __future__ import print_function
import sys
import os
import json

# Add the current directory to path to use the local custom uncompyle6
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def decompile_file(pyc_file):
    """Decompile a single .pyc file and return JSON result"""

    result = {
        "success": False,
        "output_file": None,
        "error": None
    }

    try:
        from uncompyle6.main import uncompyle_file

        # Determine output file
        output_file = pyc_file[:-1] if pyc_file.endswith('.pyc') else pyc_file + '.py'

        # Decompile
        with open(output_file, 'w') as f:
            uncompyle_file(pyc_file, f)

        # Verify file was created
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            result["success"] = True
            result["output_file"] = output_file
        else:
            result["error"] = "Output file is empty or not created"

    except Exception as e:
        result["error"] = str(e)

        # Clean up failed file
        try:
            if 'output_file' in locals() and os.path.exists(output_file):
                os.remove(output_file)
        except:
            pass

    return result


def main():
    """Main entry point"""

    if len(sys.argv) < 2:
        result = {
            "success": False,
            "error": "No input file specified"
        }
        print(json.dumps(result))
        sys.exit(1)

    pyc_file = sys.argv[1]

    if not os.path.exists(pyc_file):
        result = {
            "success": False,
            "error": "File not found: {}".format(pyc_file)
        }
        print(json.dumps(result))
        sys.exit(1)

    # Decompile the file
    result = decompile_file(pyc_file)

    # Output JSON result
    print(json.dumps(result))
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()