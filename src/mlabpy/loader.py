'''
MlabPy matlab module loader.

This is the other magical piece that hooks into the Python runtime and enables
automatic loading of matlab files as Python modules.

Copyright (C) 2015, led02 <mlabpy@led-inc.eu>
'''
import ast
import os
import sys
from importlib.abc import Finder, Loader

import mlabpy
from mlabpy import conf, lexer, parser, patch #, rules # Used for 2 pass mode

class MatLabFinder(Finder):
    """
    Implements ``finder`` protocol to be added to ``sys.meta_path``.
    """
    
    def __init__(self):
        self._parser = parser.new()
    
    def find_module(self, fullname, path=None):
        """
        Load .m files from package or from ``sys.path``.
        """
        # TODO find_spec
        if path is not None:
            # path is set -> we are in a package
            modname = fullname.split('.')[-1]
        else:
            # not in package -> search cwd and sys.path
            modname = fullname
            path = ['.'] + sys.path
        
        filename = modname + '.m'
        for dirname in path:
            filepath = os.path.join(dirname, filename)
            if os.path.exists(filepath):
                if conf.DEBUG:
                    print("* Loading {0} from {1}...".format(modname, filepath))
                return MatlabLoader(self._parser, filepath)

class MatlabLoader(Loader):
    """
    Implements ``loader`` protocol to load .m files discovered by ``MatLabFinder``.
    """
    
    def __init__(self, parser, filepath):
        """
        ``parser`` is a ``ply.yacc`` parser instance. ``filename`` is the .m file to be loaded. 
        """
        self._parser = parser
        self._filepath = filepath
    
    def _get_imports(self):
        """
        Create ``ast.Import`` nodes for ``mlabpy.autoload``.
        """
        imports = []
        for modname in mlabpy.autoload:
            import_node = ast.ImportFrom(modname, [ast.alias('*', None)], 0)
            import_node.lineno = 0
            import_node.col_offset = 0
            imports.append(import_node)
        return imports

    def exec_module(self, module):
        """
        Read the source from ``_filepath``, try to parse it and finally
        compile the AST to a Python module.
        """
        module.__file__ = self._filepath
        
        buf = open(self._filepath, 'r').read()
        tree = self._get_imports() \
             + self._parser.parse(buf, lexer=lexer.new())
        
        mod = ast.Module(tree)
        patch.patcher.visit(mod)
        # Two pass mode: Pythonize matlab stuff, then optimize
#        patch.AstPatcher(rules.indices + rules.methods).visit(mod)
#        patch.AstPatcher(rules.optimization).visit(mod)

        if conf.LOADER_DUMP_TREE:
            parser.dump(mod, outfile=open(self._filepath + '.ast', 'w'))
        
        code = compile(mod, filename=self._filepath, mode="exec")
        exec(code, module.__dict__, module.__dict__)


# Stores the loader for re-use
_matlab_loader = None

def enable_matlab_import():
    """
    Enable MlibPy's automatic import support. This method should be called
    before attempting to import any matlab modules.
    """
    global _matlab_loader
    
    if _matlab_loader is None:
        _matlab_loader = MatLabFinder()
    
    if _matlab_loader not in sys.meta_path:
        sys.meta_path.append(_matlab_loader)
