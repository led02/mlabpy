'''
MlabPy interactive console.

Very shaky developer tool.

Copyright (C) 2015, led02 <mlabpy@led-inc.eu>
'''
import ast
import cmd
import importlib
import traceback
import types

import mlabpy
from mlabpy import conf, lexer, loader, parser, patch

class MlabInterpreter(cmd.Cmd):
    def __init__(self):
        super(MlabInterpreter, self).__init__()
        self.prompt = '=> '

        self._stop = False
        self._echo = False
        
        self._lexer = lexer.new()
        self._parser = parser.new(start='stmt')
        self._modparser = None
        
        self._mod = types.ModuleType('__mlabpy__', 'Interpreter loop container')
        self._mod.exit = self._exit
        self._mod.load = self._load
        self._mod.opt = self._opt
        
        for modname in mlabpy.autoload:
            self._import_mod(importlib.import_module(modname))
    
    def _import_mod(self, mod):
        for name, value in mod.__dict__.items():
            if name.startswith('_'):
                continue
            setattr(self._mod, name, value)

    def _exit(self):
        self._stop = True
    
    def _load(self, filepath):
        if self._modparser is None:
            self._modparser = parser.new()

        print("Loading {0}".format(filepath), file=self.stdout)
        mloader = loader.MatlabLoader(self._modparser, filepath)
        self._import_mod(mloader.load_module('__mlabpy__'))
    
    def _opt(self, name, value):
        if name == 'echo':
            self._echo = value
        elif name == 'dump':
            conf.LOADER_DUMP_TREE = value
    
    def onecmd(self, line):
        if line == 'EOF':
            self._stop = True
        
        else:
            if not line.endswith(';'):
                line += ';'
            
            buf = line.strip()
            while True:
                try:
                    tree = self._parser.parse(buf, lexer=self._lexer)
                    if self._echo:
                        parser.dump(tree)
                    node = ast.Interactive([tree])
                    patch.patcher.visit(node)
                    code = compile(node, filename='<mlapby>', mode='single')
                    res = exec(code, self._mod.__dict__)
                    if res is not None:
                        print(res, file=self.stdout)
                except parser.Parser.SyntaxError as e:
                    if e.args[0] is None:
                        self.stdout.write('...> ')
                        self.stdout.flush()
                        line = self.stdin.readline()
                        buf += ';' + line.strip()
                        continue
                    else:
                        print('Syntax error:', e, file=self.stdout)
                except Exception as e:
                    print("Error({0}):".format(e.__class__.__name__), e, file=self.stdout)
                    traceback.print_tb(e.__traceback__)

                break

        if self._stop:
            self.stdout.write("Bye!\n")
            return True
        
        return False
