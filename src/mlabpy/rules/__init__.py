from mlabpy.rules import array, builtin

indices = [
    array.ArrayIndexEndAppend(),
    array.ArrayIndexEndAppendSlice(),
    array.ArrayIndexEndOffset(),
    array.ArrayIndexEnd(),
    array.ArrayIndexNum(),
]

methods = [
    builtin.AssertRule(),
]

optimization = [
    builtin.BinOpNums(),
]

all = indices + methods + optimization
