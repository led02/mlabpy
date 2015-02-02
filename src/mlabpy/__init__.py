"""
MlabPy main package.

autoload : List of packages that should be automatically imported for every
           matlab file processed.

This package contains some magic to extend the autoload list with values from
the environment variable ``MLABPY_AUTOLOAD``.

Copyright (C) 2025, led02 <mlabpy@led-inc.eu>
"""
import os

autoload = ['mlabpy.runtime.core', 'mlabpy.runtime.scipy']
_env_autoload = os.getenv("MLABPY_AUTOLOAD")
if _env_autoload:
    autoload.extend(map(str.strip, _env_autoload.split(',')))
