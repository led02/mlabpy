'''
MlabPy core runtime.

This module defines the most basic functionality to get matlab running.
Basically it provides everything available from Python and NumPy. This also
includes wrappers for martix, struct and vector types.

Copyright (C) 2015, led02 <mlabpy@led-inc.eu>
'''
import math
import sys
import time

import numpy
from numpy import identity as eye, mean, median, prod, roots, std

import mlabpy

OCTAVE_VERSION = mlabpy.VERSION + mlabpy.VERSION_EXTRA

# Constants
###########
true = True
false = False
stdout = sys.stdout


# Simple wrappers
#################
clc = lambda: None # TODO dummy stub -> clear console window
clear = lambda *args: None # TODO dummy stub -> delete vars
disp = lambda x: print(x)
fclose = lambda fid: fid.close()
fflush = lambda fid: fid.flush()
fopen = open
fprintf = lambda fid, fmt, *v: (sys.stdout if fid == 1 else fid).write(fmt % v)
isempty = lambda x: len(x) <= 0
isfield = lambda s, n: n in s
length = len
mod = lambda x, y: x % y
strrep = str.replace
size = lambda x: x.size
sqrt = lambda x: math.sqrt(x)
version = lambda: mlabpy.RELEASE + ' ' + mlabpy.VERSION + mlabpy.VERSION_EXTRA
zeros = lambda *args: numpy.zeros(args)


# Custom functions
##################
def exist(name, kind='file'):
    if kind == 'builtin':
        return name in globals()
    elif kind == 'file':
        # TODO implement me
        return false
    return False

def getargs(defaults, updates):
    cloned = defaults.clone()
    cloned.update(updates)
    return cloned

def primes(n):
    """ Input n>=6, Returns a array of primes, 2 <= p < n """
    sieve = numpy.ones(n/3 + (n%6==2), dtype=numpy.bool)
    for i in range(1,int(n**0.5)//3+1):
        if sieve[i]:
            k=3*i+1|1
            sieve[       k*k/3     ::2*k] = False
            sieve[k*(k-2*(i&1)+4)/3::2*k] = False
    return numpy.r_[2,3,((3*numpy.nonzero(sieve)[0][1:]+1)|1)]

def _make_rand(randf):
    def _randf(*args):
        if len(args) == 1 \
        and isinstance(args[0], int):
            return randf(args[0], args[0])
        elif len(args) == 2 \
        and args[1] == 1:
            return randf(args[0])
        else:
            return randf(*args)
    return _randf

rand = _make_rand(numpy.random.rand)
randn = _make_rand(numpy.random.randn)

def tic():
    global _last_tick
    _last_tick = time.clock()

def toc(interval=None):
    return time.clock() - (interval or _last_tick)


# Custom classes
################
class _end(object):
    def __init__(self, offset=0):
        self.offset = offset
    
    def __add__(self, other):
        return _end(self.offset + other)
    
    def __sub__(self, other):
        return _end(self.offset - other)

end = _end()

class matrix(object):
    def __init__(self, data):
        if len(data) >= 1 \
        and isinstance(data[0], matrix):
            data = numpy.concatenate((data[0], data[1:]))
        self._data = numpy.array(data)
    
    def __getitem__(self, index):
        # FIXME why is that
        if isinstance(index, tuple) \
        and len(index) == 1:
            index = index[0]
        
        if isinstance(index, _end):
            if index.offset >= 0:
                raise IndexError('end+{0}'.format(index.offset))
            return self._data[index.offset]
        else:
            return self._data[index]

    def __setitem__(self, index, value):
        # TODO why is that
        if isinstance(index, tuple) \
        and len(index) == 1:
            index = index[0]
        
        if isinstance(index, _end):
            if index.offset == 0:
                self._data = numpy.concatenate((self._data, [value]))
            elif index.offset < 0:
                self._data[index.offset] = value
            else:
                raise IndexError('end+{0}'.format(index.offset))
        else:
            self._data[index] = value
    
    def __len__(self):
        return len(self._data)
    
    def __str__(self):
        return str(self._data)
    
    def __repr__(self):
        return repr(self._data)

class struct(dict):
    def __init__(self, *args):
        names = args[::2]
        values = args[1::2]
        super(struct, self).__init__(zip(names, values))
    
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError(name)
    
    def __setattr__(self, name, value):
        self[name] = value

class vector(list):
    def __getitem__(self, index):
        if isinstance(index, _end):
            if index.offset >= 0:
                raise IndexError('end+{0}'.format(index.offset))
            return self[index.offset]
        else:
            return super(vector, self).__getitem__(index)
    
    def __setitem__(self, index, value):
        if isinstance(index, _end):
            if index.offset == 0:
                self.append(value)
            elif index.offset < 0:
                self[index.offset] = value
            else:
                raise IndexError('end+{0}'.format(index.offset))
        else:
            super(vector, self).__setitem__(index, value)
