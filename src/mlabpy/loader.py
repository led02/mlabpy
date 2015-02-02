'''
MlabPy matlab module loader.

This is the other magical piece that hooks into the Python runtime and enables
automatic loading of matlab files as Python modules.

Copyright (C) 2015, led02 <mlabpy@led-inc.eu>
'''
import ast
import os
from importlib.abc import Finder, Loader

import mlabpy
from mlabpy import lexer, parser

OUTPUT_TREE = False

class MatLabFinder(Finder):
    def __init__(self):
        self._parser = parser.new()
        
    def find_module(self, fullname, path=None):
        if path is not None:
            modname = fullname.split('.')
            filepath = os.path.join(path[0], modname[-1] + '.m')
            if os.path.exists(filepath):
                return MatlabLoader(self._parser, filepath)

class MatlabLoader(Loader):
    def __init__(self, parser, filepath):
        self._parser = parser
        self._filepath = filepath
    
    def _get_imports(self):
        imports = []
        for modname in mlabpy.autoload:
            import_node = ast.ImportFrom(modname, [ast.alias('*', None)], 0)
            import_node.lineno = 0
            import_node.col_offset = 0
            imports.append(import_node)
        return imports

    def exec_module(self, module):
        module.__file__ = self._filepath
        
        buf = open(self._filepath, 'r').read()
        tree = self._get_imports() \
             + self._parser.parse(buf, lexer=lexer.new())
        
        mod = ast.Module(tree)
        if OUTPUT_TREE:
            parser.dump(mod, outfile=open(self._filepath + '.ast', 'w'))
        
        code = compile(mod, filename=self._filepath, mode="exec")
        exec(code, module.__dict__, module.__dict__)

_matlab_loader = None

def enable_matlab_import():
    import sys
    global _matlab_loader
    
    if _matlab_loader is None:
        _matlab_loader = MatLabFinder()
    
    if _matlab_loader not in sys.meta_path:
        sys.meta_path.append(_matlab_loader)
