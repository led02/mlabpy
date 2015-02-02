'''
MlabPy command line tool.

Copyright (C) 2015, led02 <mlabpy@led-inc.eu>
'''
import argparse
import os

import mlabpy
from mlabpy import interactive, loader, parser

argp = argparse.ArgumentParser(
    description="MlabPy runtime",
    epilog="If no files are passed, an interactive console will be presented."
)
argp.add_argument(
    '-u', '--use', action='append',
    help="Import given Python modules. (from foo import *)",
)
argp.add_argument(
    'files', nargs='*', metavar="FILE",
    help="Files to be executed.",
)

def main():
    args = argp.parse_args()
    
    for use_arg in (args.use or []):
        mlabpy.autoload.extend(use_arg.split(','))
    
    if args.files:
        mparser = parser.new()
        for filename in args.files:
            modname, _ = os.path.splitext(os.path.basename(filename))
            try:
                mloader = loader.MatlabLoader(mparser, filename)
                mod = mloader.load_module(modname)
                
                # Look for a main routine called like the module and call it
                if hasattr(mod, 'main'):
                    ret = getattr(mod, 'main')()
                    if ret is not None:
                        print(ret)
            except Exception as e:
                print("Error.", e)

    else:
        interactive.MlabInterpreter().cmdloop()

if __name__ == '__main__':
    main()
