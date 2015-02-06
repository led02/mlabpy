'''
Created on 06.02.2015

@author: meinel
'''
import ast

from mlabpy.rules.base import Rule, ref

class AssertRule(Rule):
    match = ast.Expr(value=ast.Call(func=ast.Name(id="assert"), args=[ast.expr(ref="test"), ast.Str(ref="msg")]))
    replace = ast.Assert(test=ref("test"), msg=ref("msg"))
