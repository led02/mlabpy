'''
Created on 06.02.2015

@author: meinel
'''
import ast

from mlabpy.rules.base import Rule, ref

class AssertRule(Rule):
    match = ast.Expr(value=ast.Call(func=ast.Name(id="assert"), args=[ast.expr(ref="test"), ast.Str(ref="msg")]))
    replace = ast.Assert(test=ref("test"), msg=ref("msg"))

class BinOpNums(Rule):
    match = ast.BinOp(left=ast.Num(ref="left"), right=ast.Num(ref="right"))

    def eval(self, node, refs):
        if isinstance(node.op, ast.Add):
            return ast.Num(refs["left"].n + refs["right"].n)
        elif isinstance(node.op, ast.Sub):
            return ast.Num(refs["left"].n - refs["right"].n)
        elif isinstance(node.op, ast.Mult):
            return ast.Num(refs["left"].n * refs["right"].n)
        elif isinstance(node.op, ast.Div):
            return ast.Num(refs["left"].n / refs["right"].n)
        else:
            return node
