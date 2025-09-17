"""
CPython magic- and version- independent marshal routines

This is needed when the bytecode extracted is from
a different version than the currently-running Python.

When the two are the same, you can simply use Python's built-in marshal.loads()
to produce a code object
"""

# Copyright (c) 1999 John Aycock
# Copyright (c) 2000-2002 by hartmut Goebel <h.goebel@crazy-compilers.com>
# Copyright (c) 2005 by Dan Pascu <dan@windowmaker.org>
# Copyright (c) 2015 by Rocky Bernstein

from __future__ import print_function

import sys, types
from struct import unpack

from uncompyle6.magics import PYTHON_MAGIC_INT
from uncompyle6.code import Code3

internStrings = []
internObjects = []

PYTHON3 = (sys.version_info >= (3, 0))

if PYTHON3:
    def long(n): return n

def compat_str(s):
    return s.decode('utf-8', errors='ignore') if PYTHON3 else str(s)

def load_code(fp, magic_int, code_objects={}):
    """
    marshal.load() written in Python. When the Python bytecode magic loaded is the
    same magic for the running Python interpreter, we can simply use the
    Python-supplied mashal.load().

    However we need to use this when versions are different since the internal
    code structures are different. Sigh.
    """
    global internStrings, internObjects
    internStrings = []
    internObjects = []
    seek_pos = fp.tell()
    # Do a sanity check. Is this a code type?
    b =  ord(fp.read(1))

    if (b & 0x80):
        b = b & 0x7f

    c = chr(b)
    if c != 'c':
        raise TypeError("File %s doesn't smell like Python bytecode" % fp.name)

    fp.seek(seek_pos)
    return load_code_internal(fp, magic_int, code_objects=code_objects)

def load_code_type(fp, magic_int, bytes_for_s=False, code_objects={}):
    # Python [1.3 .. 2.3)
    # FIXME: find out what magics were for 1.3
    v13_to_23 = magic_int in (20121, 50428, 50823, 60202, 60717)

    # Python [1.5 .. 2.3)
    v15_to_23 = magic_int in (20121, 50428, 50823, 60202, 60717)

    if v13_to_23:
        co_argcount = unpack('h', fp.read(2))[0]
    else:
        co_argcount = unpack('i', fp.read(4))[0]

    if 3020 < magic_int < 20121:
        kwonlyargcount = unpack('i', fp.read(4))[0]
    else:
        kwonlyargcount = 0

    if v13_to_23:
        co_nlocals = unpack('h', fp.read(2))[0]
    else:
        co_nlocals = unpack('i', fp.read(4))[0]

    if v15_to_23:
        co_stacksize = unpack('h', fp.read(2))[0]
    else:
        co_stacksize = unpack('i', fp.read(4))[0]

    if v13_to_23:
        co_flags = unpack('h', fp.read(2))[0]
    else:
        co_flags = unpack('i', fp.read(4))[0]

    co_code = load_code_internal(fp, magic_int, bytes_for_s=True,
                                 code_objects=code_objects)

    co_consts = load_code_internal(fp, magic_int, code_objects=code_objects)
    co_names = load_code_internal(fp, magic_int, code_objects=code_objects)
    co_varnames = load_code_internal(fp, magic_int, code_objects=code_objects)
    co_freevars = load_code_internal(fp, magic_int, code_objects=code_objects)
    co_cellvars = load_code_internal(fp, magic_int, code_objects=code_objects)
    co_filename = load_code_internal(fp, magic_int, code_objects=code_objects)
    co_name = load_code_internal(fp, magic_int)
    co_firstlineno = unpack('i', fp.read(4))[0]
    co_lnotab = load_code_internal(fp, magic_int, code_objects=code_objects)

    # The Python3 code object is different than Python2's which
    # we are reading if we get here.
    # Also various parameters which were strings are now
    # bytes (which is probably more logical).
    if PYTHON3:
        Code = types.CodeType
        # Check Python version to handle different CodeType signatures
        import sys
        if sys.version_info >= (3, 11):
            # Python 3.11+ removed co_firstlineno and co_lnotab from the constructor
            # They're now replaced with co_linetable and other parameters
            # For simplicity, we'll create a simpler code object
            # Note: This may not preserve line number information perfectly

            # Convert all parameters to proper types
            if isinstance(co_filename, bytes):
                co_filename = co_filename.decode('utf-8')
            elif not isinstance(co_filename, str):
                co_filename = str(co_filename) if co_filename else "<unknown>"

            if isinstance(co_name, bytes):
                co_name = co_name.decode('utf-8')
            elif not isinstance(co_name, str):
                co_name = str(co_name) if co_name else "<unknown>"

            # Ensure names are tuples of strings
            if co_names and len(co_names) > 0 and not isinstance(co_names[0], str):
                co_names = tuple(n.decode('utf-8') if isinstance(n, bytes) else str(n) for n in co_names)
            if co_varnames and len(co_varnames) > 0 and not isinstance(co_varnames[0], str):
                co_varnames = tuple(n.decode('utf-8') if isinstance(n, bytes) else str(n) for n in co_varnames)
            if co_freevars and len(co_freevars) > 0 and not isinstance(co_freevars[0], str):
                co_freevars = tuple(n.decode('utf-8') if isinstance(n, bytes) else str(n) for n in co_freevars)
            if co_cellvars and len(co_cellvars) > 0 and not isinstance(co_cellvars[0], str):
                co_cellvars = tuple(n.decode('utf-8') if isinstance(n, bytes) else str(n) for n in co_cellvars)

            # For Python 3.11+, we need to use replace() method to create code objects
            # First create a dummy code object
            dummy_code = compile('pass', '<dummy>', 'exec')

            # Then replace its attributes
            code = dummy_code.replace(
                co_argcount=co_argcount,
                co_posonlyargcount=0,
                co_kwonlyargcount=kwonlyargcount,
                co_nlocals=co_nlocals,
                co_stacksize=co_stacksize,
                co_flags=co_flags,
                co_code=co_code,
                co_consts=co_consts,
                co_names=co_names,
                co_varnames=co_varnames,
                co_filename=co_filename,
                co_name=co_name,
                co_firstlineno=co_firstlineno,
                co_freevars=co_freevars,
                co_cellvars=co_cellvars
            )
        elif sys.version_info >= (3, 8):
            # Python 3.8+ has co_posonlyargcount as first parameter after co_argcount

            # Convert all parameters to proper types
            if isinstance(co_filename, bytes):
                co_filename = co_filename.decode('utf-8')
            elif not isinstance(co_filename, str):
                co_filename = str(co_filename) if co_filename else "<unknown>"

            if isinstance(co_name, bytes):
                co_name = co_name.decode('utf-8')
            elif not isinstance(co_name, str):
                co_name = str(co_name) if co_name else "<unknown>"

            # Ensure names, varnames are tuples of strings
            if co_names and not isinstance(co_names[0] if co_names else "", str):
                co_names = tuple(n.decode('utf-8') if isinstance(n, bytes) else str(n) for n in co_names)
            if co_varnames and not isinstance(co_varnames[0] if co_varnames else "", str):
                co_varnames = tuple(n.decode('utf-8') if isinstance(n, bytes) else str(n) for n in co_varnames)
            if co_freevars and not isinstance(co_freevars[0] if co_freevars else "", str):
                co_freevars = tuple(n.decode('utf-8') if isinstance(n, bytes) else str(n) for n in co_freevars)
            if co_cellvars and not isinstance(co_cellvars[0] if co_cellvars else "", str):
                co_cellvars = tuple(n.decode('utf-8') if isinstance(n, bytes) else str(n) for n in co_cellvars)

            code = Code(co_argcount, 0, kwonlyargcount, co_nlocals, co_stacksize, co_flags,
                        co_code, co_consts, co_names, co_varnames, co_filename, co_name,
                        co_firstlineno, bytes(co_lnotab, encoding='utf-8'),
                        co_freevars, co_cellvars)
        elif PYTHON_MAGIC_INT > 3020:
            # In later Python3 magic_ints, there is a
            # kwonlyargcount parameter which we set to 0.
            code = Code(co_argcount, kwonlyargcount, co_nlocals, co_stacksize, co_flags,
                        co_code, co_consts, co_names, co_varnames, co_filename, co_name,
                        co_firstlineno, bytes(co_lnotab, encoding='utf-8'),
                        co_freevars, co_cellvars)
        else:
            code =  Code(co_argcount, co_nlocals, co_stacksize, co_flags,
                        co_code, co_consts, co_names, co_varnames, co_filename, co_name,
                        co_firstlineno, bytes(co_lnotab, encoding='utf-8'),
                        co_freevars, co_cellvars)
    else:
        if (3000 <= magic_int < 20121):
            # Python 3  encodes some fields as Unicode while Python2
            # requires the corresponding field to have string values
            co_consts = tuple([str(s) if isinstance(s, unicode) else s for s in co_consts])
            co_names  = tuple([str(s) if isinstance(s, unicode) else s for s in co_names])
            co_varnames  = tuple([str(s) if isinstance(s, unicode) else s for s in co_varnames])
            co_filename = str(co_filename)
            co_name = str(co_name)
        if 3020 < magic_int <= 20121:
            code =  Code3(co_argcount, kwonlyargcount,
                          co_nlocals, co_stacksize, co_flags, co_code,
                          co_consts, co_names, co_varnames, co_filename, co_name,
                          co_firstlineno, co_lnotab, co_freevars, co_cellvars)
        else:
            Code = types.CodeType
            code =  Code(co_argcount, co_nlocals, co_stacksize, co_flags, co_code,
                         co_consts, co_names, co_varnames, co_filename, co_name,
                         co_firstlineno, co_lnotab, co_freevars, co_cellvars)
            pass
        pass
    code_objects[str(code)] = code
    return code

def load_code_internal(fp, magic_int, bytes_for_s=False,
                       code_objects={}, marshalType=None):
    global internStrings, internObjects

    if marshalType is None:
        b1 = ord(fp.read(1))
        if b1 & 0x80:
            b1 = b1 &0x7f
            code = load_code_internal(fp, magic_int, bytes_for_s=False,
                                      code_objects=code_objects,
                                      marshalType=chr(b1))
            internObjects.append(code)
            return code
        marshalType = chr(b1)

    # print(marshalType) # debug
    if marshalType == '0':
        # Null
        return None
    elif marshalType == 'N':
        return None
    elif marshalType == 'F':
        return False
    elif marshalType == 'T':
        return True
    elif marshalType == 'S':
        return StopIteration
    elif marshalType == '.':
        return Ellipsis
    elif marshalType == 'i':
        # int
        return int(unpack('i', fp.read(4))[0])
    elif marshalType == 'I':
        # int64
        return unpack('q', fp.read(8))[0]
    elif marshalType == 'f':
        # float
        n = fp.read(1)
        return float(unpack('d', fp.read(n))[0])
    elif marshalType == 'g':
        # binary float
        return float(unpack('d', fp.read(8))[0])
    elif marshalType == 'x':
        # complex
        raise KeyError(marshalType)
    elif marshalType == 'y':
        # binary complex
        real = unpack('d', fp.read(8))[0]
        imag = unpack('d', fp.read(8))[0]
        return complex(real, imag)
    elif marshalType == 'l':
        # long
        n = unpack('i', fp.read(4))[0]
        if n == 0:
            return long(0)
        size = abs(n)
        d = long(0)
        for j in range(0, size):
            md = int(unpack('h', fp.read(2))[0])
            d += md << j*15
        if n < 0:
            return long(d*-1)
        return d
    elif marshalType == 's':
        # string
        # Note: could mean bytes in Python3 processing Python2 bytecode
        strsize = unpack('i', fp.read(4))[0]
        s = fp.read(strsize)
        if not bytes_for_s:
            s = compat_str(s)
        return s
    elif marshalType == 't':
        # interned
        strsize = unpack('i', fp.read(4))[0]
        interned = compat_str(fp.read(strsize))
        internStrings.append(interned)
        return interned
    elif marshalType == 'R':
        # string reference
        refnum = unpack('i', fp.read(4))[0]
        return internStrings[refnum]
    elif marshalType == 'r':
        # object reference - new in Python3
        refnum = unpack('i', fp.read(4))[0]
        return internObjects[refnum-1]
    elif marshalType == '(':
        tuplesize = unpack('i', fp.read(4))[0]
        ret = tuple()
        while tuplesize > 0:
            ret += load_code_internal(fp, magic_int, code_objects=code_objects),
            tuplesize -= 1
        return ret
    elif marshalType == '[':
        raise KeyError(marshalType)
    elif marshalType == '{':
        # dictionary
        raise KeyError(marshalType)
    elif marshalType == 'c':
        return load_code_type(fp, magic_int, bytes_for_s=False,
                              code_objects=code_objects)
    elif marshalType == 'C':
        # code type used in Python 1.0 - 1.2
        raise KeyError("C code is Python 1.0 - 1.2; can't handle yet")
    elif marshalType == 'u':
        strsize = unpack('i', fp.read(4))[0]
        unicodestring = fp.read(strsize)
        return unicodestring.decode('utf-8')
    elif marshalType == '?':
        # unknown
        raise KeyError(marshalType)
    elif marshalType in ['<', '>']:
        # set and frozenset
        setsize = unpack('i', fp.read(4))[0]
        ret = tuple()
        while setsize > 0:
            ret += load_code_internal(fp, magic_int, code_objects=code_objects),
            setsize -= 1
        if marshalType == '>':
            return frozenset(ret)
        else:
            return set(ret)
    elif marshalType == 'a':
        # ascii
        # FIXME check
        strsize = unpack('i', fp.read(4))[0]
        s = fp.read(strsize)
        s = compat_str(s)
        return s
    elif marshalType == 'A':
        # ascii interned - since Python3
        # FIXME: check
        strsize = unpack('i', fp.read(4))[0]
        interned = compat_str(fp.read(strsize))
        internStrings.append(interned)
        return interned
    elif marshalType == ')':
        # small tuple - since Python3
        tuplesize = unpack('B', fp.read(1))[0]
        ret = tuple()
        while tuplesize > 0:
            ret += load_code_internal(fp, magic_int, code_objects=code_objects),
            tuplesize -= 1
        return ret
    elif marshalType == 'z':
        # short ascii - since Python3
        strsize = unpack('B', fp.read(1))[0]
        return compat_str(fp.read(strsize))
    elif marshalType == 'Z':
        # short ascii interned - since Python3
        # FIXME: check
        strsize = unpack('B', fp.read(1))[0]
        interned = compat_str(fp.read(strsize))
        internStrings.append(interned)
        return interned
    else:
        sys.stderr.write("Unknown type %i (hex %x) %c\n" %
                         (ord(marshalType), ord(marshalType), ord(marshalType)))
    return
