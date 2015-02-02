'''
MlapPy SciPy bindings.

Copyright (C) 2015, led02 <mlabpy@led-inc.eu>
'''
import numpy
from scipy import interpolate, sparse as sparsemat

sparse = sparsemat.csr_matrix

def interp2(Z, k, kind):
    Z_shape = Z.shape
    X = numpy.array(range(Z_shape[0]))
    Y = numpy.array(range(Z_shape[1]))
    return interpolate.interp2d(X, Y, Z)
        