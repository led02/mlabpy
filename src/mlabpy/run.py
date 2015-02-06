'''
MlabPy command line tool.

Copyright (C) 2015, led02 <mlabpy@led-inc.eu>
'''
import argparse
import os

import mlabpy
from mlabpy import conf, interactive, loader, parser
from traceback import print_tb

argp = argparse.ArgumentParser(
    description="MlabPy runtime",
    epilog="If no files are passed, an interactive console will be presented."
)
argp.add_argument(
    '-d', '--debug', action='store_true',
    help="Enable debug output.",
)
argp.add_argument(
    '-i', '--install', action='store_true',
    help="Install import handler.",
)
argp.add_argument(
    '-a', '--autoload', action='append',
    help="Auto load given Python modules. (from foo import *)",
)
argp.add_argument(
    'files', nargs='*', metavar="FILE",
    help="Files to be executed.",
)

def main():
    args = argp.parse_args()
    
    if args.debug is not None:
        conf.DEBUG = args.debug
    
    if not args.files:
        print("{0} interactive console ({1})".format(mlabpy.RELEASE, mlabpy.VERSION + mlabpy.VERSION_EXTRA))
        if conf.DEBUG:
            print("* Starting...")
    
    for autoload_arg in (args.autoload or []):
        mlabpy.autoload.extend(autoload_arg.split(','))
    
    if args.install:
        loader.enable_matlab_import()
    
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
                if conf.DEBUG:
                    print_tb(e.__traceback__)

    else:
        interactive.MlabInterpreter().cmdloop()

if __name__ == '__main__':
    main()
