'''
Created on 05.02.2015

@author: meinel
'''
import ast

from mlabpy.rules.base import Rule, ref

class ArrayIndexNum(Rule):
    match = ast.Index(value=ast.expr(ref="value"))
    replace = ast.Index(value=ast.BinOp(left=ref("value"), op=ast.Sub(), right=ast.Num(1)))

class ArrayIndexEnd(Rule):
    match = ast.Index(value=ast.Name(id="end"))
    replace = ast.Index(value=ast.Num(n=-1))

class ArrayIndexEndOffset(Rule):
    match = ast.BinOp(left=ast.Name(id="end"), op=ast.Sub(), right=ast.expr(ref="right"))
    replace = ast.UnaryOp(op=ast.USub(), operand=ast.BinOp(left=ref("right"), op=ast.Add(), right=ast.Num(1)))

class ArrayIndexEndAppend(Rule):
    match = ast.Assign(targets=[ast.Subscript(value=ast.Name(ref="target"), slice=ast.Index(value=ast.BinOp(left=ast.Name(id="end"), op=ast.Add(), right=ast.Num(1))))], value=ast.expr(ref="value"))
    replace = ast.Assign(targets=[ref("target", ctx=ast.Store())], value=ast.Call(func=ast.Attribute(value=ast.Name(id="numpy", ctx=ast.Load()), attr="concatenate", ctx=ast.Load()), args=[ast.Tuple(elts=[ref("target"), ast.List(elts=[ref("value")], ctx=ast.Load())], ctx=ast.Load())], keywords=[]))
