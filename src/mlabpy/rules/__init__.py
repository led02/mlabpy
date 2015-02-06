from mlabpy.rules import array, builtin

all = [
    array.ArrayIndexEndAppend(),
    array.ArrayIndexEndOffset(),
    array.ArrayIndexEnd(),
    array.ArrayIndexNum(),
    
    builtin.AssertRule(),
]
