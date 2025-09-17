#  Copyright (c) 2015-2016 by Rocky Bernstein
"""
Python 3.4 bytecode scanner/deparser

This sets up opcodes Python's 3.4 and calls a generalized
scanner routine for Python 3.
"""

from __future__ import print_function

import uncompyle6

# bytecode verification, verify(), uses JUMP_OPs from here
from uncompyle6.opcodes.opcode_34 import JUMP_OPs

from uncompyle6.scanners.scanner3 import Scanner3
class Scanner34(Scanner3):

    def __init__(self):
        super(Scanner3, self).__init__(3.4)
        self.showast = False

    def disassemble(self, co, classname=None, code_objects={}, showast=False):
        return self.disassemble3(co, classname, code_objects)

    def disassemble_native(self, co, classname=None, code_objects={}):
        return self.disassemble3_native(co, classname, code_objects)

if __name__ == "__main__":
    from uncompyle6 import PYTHON_VERSION
    if PYTHON_VERSION >= 3.2:
        import inspect
        co = inspect.currentframe().f_code
        tokens, customize = Scanner34().disassemble(co)
        for t in tokens:
            print(t)
        pass
    else:
        print("Need to be Python 3.2 or greater to demo; I am %s." %
              PYTHON_VERSION)
