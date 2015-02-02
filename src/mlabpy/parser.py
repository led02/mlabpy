'''
MlabPy parser.

The parser produces Python AST nodes ... this is where the magic happens.

Copyright (C) 2015, led02 <mlabpy@led-inc.eu>

Heavy based on 'smop'. Copyright 2011-2014 Victor Leikehman.
'''
import ast
import sys
from ply import yacc

from mlabpy import lexer
from builtins import isinstance
import io

class Parser(object):
    class Error(Exception):
        pass

    class SyntaxError(Error):
        pass

    tokens = lexer.tokens

    precedence = (
        ("right","DOTDIVEQ","DOTMULEQ","EQ","EXPEQ","MULEQ","MINUSEQ","DIVEQ","PLUSEQ","OREQ","ANDEQ"),
        ("nonassoc","HANDLE"),
        ("left", "COMMA"),
        ("left", "COLON"),
        ("left", "ANDAND", "OROR"),
        ("left", "EQEQ", "NE", "GE", "LE", "GT", "LT"),
        ("left", "OR", "AND"),
        ("left", "PLUS", "MINUS"),
        ("left", "MUL","DIV","DOTMUL","DOTDIV","BACKSLASH"),
        ("right","UMINUS","NEG"),
        ("right","TRANSPOSE"),
        ("right","EXP", "DOTEXP"),
        ("nonassoc","LPAREN","RPAREN","RBRACE","LBRACE"),
        ("left", "FIELD","DOT","PLUSPLUS","MINUSMINUS"),
    )

    def __init__(self):
        self._use_nargin = None
        self._use_varargin = None
        self._ret_expr = None
    
    def p_top(self, p):
        '''
        top :
            | stmt_list
            | top func_decl stmt_list_opt
            | top func_decl END_STMT semi_opt
            | top func_decl stmt_list END_STMT semi_opt
        '''
        if len(p) == 1:
            p[0] = []
        elif len(p) == 2:
            p[0] = p[1]
        else:
            if p[3]:
                p[2].body.extend(p[3])
            
            try:
                if not p[2].body \
                or p[2].body[-1].__class__ is not ast.Return:
                    ret = self._new_node(p, ast.Return, self._ret_expr)
                    ret.lineno = p.lexer.lineno
                    ret.col_offset = 0
                    p[2].body.append(ret)
                    self._ret_expr = None
            except:
                raise Parser.SyntaxError(p)
            
            p[0] = p[1]
            p[0].append(p[2])
    
    def p_semi_opt(self, p):
        """
        semi_opt :
                 | semi_opt SEMI
                 | semi_opt COMMA
        """
        pass
    
    def p_stmt(self, p):
        """
        stmt : continue_stmt
             | break_stmt
             | expr_stmt
             | global_stmt
             | persistent_stmt
             | command
             | for_stmt
             | if_stmt
             | null_stmt
             | return_stmt
             | switch_stmt
             | try_catch
             | while_stmt
             | unwind
        """
        # END_STMT is intentionally left out
        p[0] = p[1]
    
    def p_unwind(self, p):
        """
        unwind : UNWIND_PROTECT stmt_list UNWIND_PROTECT_CLEANUP stmt_list END_UNWIND_PROTECT
        """
        p[0] = self._new_node(p, ast.Try, p[2], [], [], p[4])
    
    def p_arg1_str(self, p):
        """
        arg1 : STRING
        """
        p[0] = self._new_node(p, ast.Str, p[1])
    
    def p_arg1_number(self, p):
        """
        arg1 : NUMBER
        """
        p[0] = self._new_node(p, ast.Num, p[1])
    
    def p_arg1_other(self, p):
        """
        arg1 : IDENT
             | GLOBAL
        """
        p[0] = self._new_name(p, p[1])
    
    def p_args(self, p):
        """
        args : arg1
             | args arg1
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1]
            p[0].append(p[2])
    
    def p_command(self, p):
        """
        command : ident args SEMI
        """
        p[0] = self._new_node(p, ast.Expr, self._new_call(p, p[1], *p[2]))
    
    def p_global_list(self, p):
        """global_list : IDENT
                       | global_list IDENT
        """
        if len(p) == 2:
            p[0] = [p[1]]
        elif len(p) == 3:
            p[0] = p[1]
            p[0].append(p[2])
    
    def p_global_stmt(self, p):
        """
        global_stmt : GLOBAL global_list SEMI
                    | GLOBAL IDENT EQ expr SEMI
        """
        p[0] = self._new_node(p, ast.Global, p[2])
    
    #def p_foo_stmt(p):
    #    "foo_stmt : expr OROR expr SEMI"
        #expr1 = p[1][1][0]
        #expr2 = p[3][1][0]
        #ident = expr1.ret
        #args1 = expr1.args
        #args2 = expr2.args
        #p[0] = node.let(ret=ident,
        #                args=node.expr("or",node.expr_list([args1,args2])))
        # TODO firgure out semantics... (node.let)
    #    raise NotImplementedError('foo statement')
    
    def p_persistent_stmt(self, p):
        """
        persistent_stmt :  PERSISTENT global_list SEMI
                        |  PERSISTENT ident EQ expr SEMI
        """
        # TODO figure out semantics
        raise NotImplementedError('persistent statement')
    
    def p_return_stmt(self, p):
        "return_stmt : RETURN SEMI"
        p[0] = self._new_node(p, ast.Return, self._ret_expr)
    
    def p_continue_stmt(self, p):
        "continue_stmt : CONTINUE SEMI"
        p[0] = self._new_node(p, ast.Continue)
    
    def p_break_stmt(self, p):
        "break_stmt : BREAK SEMI"
        p[0] = self._new_node(p, ast.Break)
    
    def p_switch_stmt(self, p):
        """
        switch_stmt : SWITCH expr semi_opt case_list END_STMT
        """
        def backpatch(expr, stmt):
            if isinstance(stmt, ast.If):
                stmt.test.comparators.append(expr)
                backpatch(expr, stmt.orelse)
        backpatch(p[2], p[4])
        p[0] = p[4]
    
    def p_case_list(self, p):
        """
        case_list :
                  | CASE expr sep stmt_list_opt case_list
                  | CASE expr error stmt_list_opt case_list
                  | OTHERWISE stmt_list
        """
        if len(p) == 1:
            p[0] = []
        elif len(p) == 3:
            p[0] = p[2]
        elif len(p) == 6:
            p[0] = self._new_node(p, ast.If, self._new_node(p, ast.Compare, p[2], [ast.Eq()], []), p[4], p[5])
    
    def p_try_catch(self, p):
        """
        try_catch : TRY stmt_list CATCH stmt_list END_STMT
                  | TRY stmt_list END_STMT
        """
        handler = self._new_node(p, ast.ExceptHandler, self._new_name(p, 'Exception'), 'lasterror', [])
        if len(p) == 6:
            handler.body = p[4]
        p[0] = self._new_node(p, ast.Try, p[2], [handler], [], [])
    
    def p_null_stmt(self, p):
        """
        null_stmt : SEMI
                  | COMMA
        """
        p[0] = None
    
    def p_func_decl(self, p):
        """func_decl : FUNCTION IDENT args_opt SEMI 
                     | FUNCTION ret EQ IDENT args_opt SEMI 
        """
        if len(p) == 5:
            p[0] = self._new_node(p, ast.FunctionDef, p[2], p[3], [], [], None)
            self._ret_expr = None
        elif len(p) == 7:
            p[0] = self._new_node(p, ast.FunctionDef, p[4], p[5], [], [], None)
            self._ret_expr = p[2]
            if isinstance(self._ret_expr, ast.Name):
                name_node = self._new_name(p, self._ret_expr.id)
                name_node.ctx = ast.Store()
                p[0].body.append(self._new_node(p, ast.Assign,
                    [name_node], self._new_call(p, self._new_name(p, 'struct'))
                ))
    
    def p_args_opt(self, p):
        """
        args_opt :
                 | LPAREN RPAREN
                 | LPAREN arg_list RPAREN
        """
        if len(p) == 1 \
        or len(p) == 3:
            p[0] = self._new_arguments(p)
        elif len(p) == 4:
            p[0] = p[2]
    
    def p_arg_list(self, p):
        """
        arg_list : IDENT
                 | arg_list COMMA IDENT
        """
        if len(p) == 2:
            if p[1] in ('varargin', 'nargin'):
                if p[1] == "varargin":
                    self._use_varargin = self._new_arg(p, 'varargin')
                elif p[1] == "nargin":
                    self._use_nargin = self._new_arg(p, 'nargin')
                p[0] = self._new_arguments(p, [])
            else:
                p[0] = self._new_arguments(p, [self._new_arg(p, p[1])])
        elif len(p) == 4:
            p[0] = p[1]
            if p[3] == "varargin":
                self._use_varargin = self._new_arg(p, 'varargin')
            elif p[3] == "nargin":
                self._use_nargin = self._new_arg(p, 'nargin')
            else:
                p[0].args.append(self._new_arg(p, p[3]))
    
    def p_ret(self, p):
        """
        ret : ident
            | LBRACKET RBRACKET
            | LBRACKET expr_list RBRACKET
        """
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = self._new_list(p)
        elif len(p) == 4:
            p[0] = self._new_list(p, p[2])
    
    def p_stmt_list_opt(self, p):
        """
        stmt_list_opt :
                      | stmt_list
        """
        if len(p) == 1:
            p[0] = []
        else:
            p[0] = p[1]
    
    def p_stmt_list(self, p):
        """
        stmt_list : stmt
                  | stmt_list stmt
        """
        if len(p) == 2:
            p[0] = [p[1]] if p[1] else []
        elif len(p) == 3:
            p[0] = p[1]
            if p[2]:
                p[0].append(p[2])
    
    def p_concat_list_1(self, p):
        """
        concat_list : expr_list SEMI expr_list
        """
        p[0] = [self._new_list(p, p[1]), self._new_list(p, p[3])]
    
    def p_concat_list_2(self, p):
        """
        concat_list : concat_list SEMI expr_list
        """
        p[0] = p[1]
        p[0].append(self._new_list(p, p[3]))
    
    def p_expr_list(self, p):
        """
        expr_list : exprs
                  | exprs COMMA
        """
        p[0] = p[1]
    
    def p_exprs(self, p):
        """
        exprs : expr
              | exprs COMMA expr
        """
        if len(p) == 2:
            p[0] = [p[1]]
        elif len(p) == 4:
            p[0] = p[1]
            p[0].append(p[3])
    
    def p_expr_stmt(self, p):
        """
        expr_stmt : expr_list SEMI
        """
        if len(p[1]) == 1:
            p[0] = p[1][0]
            if isinstance(p[0], ast.expr):
                p[0] = self._new_node(p, ast.Expr, p[0])
        else:
            p[0] = self._new_node(p, ast.Expr, self._new_node(p, ast.Tuple, p[1], ast.Load()))
    
    def p_while_stmt(self, p):
        """
        while_stmt : WHILE expr SEMI stmt_list END_STMT
        """
        p[0] = self._new_node(p, ast.While, p[2], p[4], [])
    
    def p_separator(self, p):
        """
        sep : COMMA
            | SEMI
        """
        p[0] = p[1]
    
    def p_if_stmt(self, p):
        """
        if_stmt : IF expr sep stmt_list_opt elseif_stmt END_STMT
                | IF expr error stmt_list_opt elseif_stmt END_STMT
        """
        p[0] = self._new_node(p, ast.If, p[2], p[4], p[5])
    
    def p_elseif_stmt(self, p):
        """
        elseif_stmt :
                    | ELSE stmt_list_opt
                    | ELSEIF expr sep stmt_list_opt elseif_stmt
        """
        if len(p) == 1:
            p[0] = []
        elif len(p) == 3:
            p[0] = p[2]
        elif len(p) == 6:
            p[0] = [self._new_node(p, ast.If, p[2], p[4], p[5])]
    
    def p_for_stmt(self, p):
        """
        for_stmt : FOR ident EQ expr SEMI stmt_list END_STMT
                 | FOR LPAREN ident EQ expr RPAREN SEMI stmt_list END_STMT
                 | FOR matrix EQ expr SEMI stmt_list END_STMT
        """
        if len(p) == 7:
            raise NotImplementedError('matrix for loop')
        elif len(p) == 8:
            p[2].ctx = ast.Store()
            p[0] = self._new_node(p, ast.For, p[2], p[4], p[6], [])
        elif len(p) == 10:
            raise NotImplementedError('for loop ???')
    
    def p_expr(self, p):
        """
        expr : ident
             | end
             | number
             | string
             | colon
             | NEG
             | matrix
             | cellarray
             | expr2
             | expr1
             | lambda_expr
             | expr PLUSPLUS
             | expr MINUSMINUS
        """
        if p[1] == "~":
            p[0] = self._new_name(p, '__')
        else:
            p[0] = p[1]
    
    def p_lambda_args(self, p):
        """
        lambda_args : LPAREN RPAREN
                    | LPAREN arg_list RPAREN
        """
        p[0] = self._new_arguments(p) if len(p) == 3 else p[2]
    
    def p_lambda_expr(self, p):
        """
        lambda_expr : HANDLE lambda_args expr
        """
        p[0] = self._new_node(p, ast.Lambda, p[2], p[3])
    
    def p_expr_ident(self, p):
        """
        ident : IDENT
        """
        p[0] = self._new_name(p, p[1])
    
    def p_expr_number(self, p):
        """
        number : NUMBER
        """
        p[0] = self._new_node(p, ast.Num, p[1])
    
    def p_expr_end(self, p):
        """
        end : END_EXPR
        """
        p[0] = self._new_name(p, p[1])
    
    def p_expr_string(self, p):
        """
        string : STRING
        """
        p[0] = self._new_node(p, ast.Str, p[1])
    
    def p_expr_colon(self, p):
        """
        colon : COLON
        """
        p[0] = self._new_node(p, ast.Slice, None, None, None)
    
    UNARY_OPS = {
        '+': ast.UAdd,
        '-': ast.USub,
        '~': ast.Invert,
    }
    
    def p_expr1(self, p):
        """
        expr1 : MINUS expr %prec UMINUS
              | PLUS expr %prec UMINUS
              | NEG expr
              | HANDLE ident
              | PLUSPLUS ident
              | MINUSMINUS ident
        """
        if p[1] == '@':
            p[0] = p[2]
        elif p[1] == '++':
            p[2].ctx = ast.Store()
            p[0] = self._new_node(p, ast.AugAssign, p[2], ast.Add(), self._new_node(p, ast.Num, 1))
        elif p[1] == '--':
            p[2].ctx = ast.Store()
            p[0] = self._new_node(p, ast.AugAssign, p[2], ast.Sub(), self._new_node(p, ast.Num, 1))
        else:
            p[0] = self._new_node(p, ast.UnaryOp, Parser.UNARY_OPS[p[1]](), p[2])
    
    def p_cellarray(self, p):
        """
        cellarray : LBRACE RBRACE
                  | LBRACE expr_list RBRACE
                  | LBRACE concat_list RBRACE
                  | LBRACE concat_list SEMI RBRACE
        """
        # TODO clarify
        if len(p) == 3:
            p[0] = self._new_list(p)
        else:
            p[0] = self._new_list(p, p[2])
    
    def p_matrix(self, p):
        """
        matrix : LBRACKET RBRACKET
               | LBRACKET concat_list RBRACKET
               | LBRACKET concat_list SEMI RBRACKET
               | LBRACKET expr_list RBRACKET
               | LBRACKET expr_list SEMI RBRACKET
        """
        # TODO matrix
        if len(p) == 3:
            data = self._new_list(p)
        else:
            data = self._new_list(p, p[2])
        p[0] = self._new_call(p, self._new_name(p, 'matrix'), data)
    
    def p_paren_expr(self, p):
        """
        expr : LPAREN expr RPAREN
        """
        p[0] = p[2]
    
    def p_field_expr(self, p):
        """
        expr : expr FIELD
        """
        p[0] = self._new_node(p, ast.Attribute, p[1], p[2], ast.Load())
    
    def p_transpose_expr(self, p):
        """
        expr : expr TRANSPOSE
        """
        # TODO transpose
        p[0] = p[1]
    
    def p_cellarrayref(self, p):
        """
        expr : expr LBRACE expr_list RBRACE
             | expr LBRACE RBRACE
        """
        if len(p) == 4:
            p[0] = self._new_subscript(p, p[1], ast.Slice(None, None, None))
        elif len(p[3]) == 1:
            p[0] = self._new_subscript(p, p[1], ast.Index(p[3][0]))
        else:
            p[0] = self._new_subscript(p, p[1], ast.ExtSlice([
                ast.Index(i) if not isinstance(i, ast.Slice) else i for i in p[3]
            ]))
    
    def p_funcall_expr(self, p):
        """
        expr : expr LPAREN expr_list RPAREN
             | expr LPAREN RPAREN
        """
        args = [] if len(p) == 4 else p[3]
        if len(args) >= 1 \
        and isinstance(args[0], ast.Slice):
            p[0] = self._new_subscript(p, p[1], args[0])
        else:
            p[0] = self._new_call(p, p[1], *args)
    
    BINARY_OPS = {
        '&': ast.BitAnd,
        # TODO BACKSLASH
        '/': ast.Div,
        '.*': ast.Mult,
        '^': ast.Pow,
        '-': ast.Sub,
        '*': ast.Mult,
        '|': ast.BitOr,
        '+': ast.Add,
    }
    
    ASSIGN_OPS = {
        '*=': ast.Mult,
        '/=': ast.Div,
        '-=': ast.Sub,
        '+=': ast.Add,
        '^=': ast.Pow,
    }
    
    LOGIC_OPS = {
        '&&': ast.And,
        '||': ast.Or,
    }
    
    COMPARE_OPS = {
        '==': ast.Eq,
        '~=': ast.NotEq,
        '!=': ast.NotEq,
        '>=': ast.GtE,
        '>': ast.Gt,
        '<=': ast.LtE,
        '<': ast.Lt,
    }
    
    def p_expr2(self, p):
        """
        expr2 : expr AND expr
              | expr ANDAND expr
              | expr BACKSLASH expr
              | expr COLON expr
              | expr DIV expr
              | expr DOT expr
              | expr DOTDIV expr
              | expr DOTDIVEQ expr
              | expr DOTEXP expr
              | expr DOTMUL expr
              | expr DOTMULEQ expr
              | expr EQEQ expr
              | expr EXP expr
              | expr EXPEQ expr
              | expr GE expr
              | expr GT expr 
              | expr LE expr
              | expr LT expr
              | expr MINUS expr
              | expr MUL expr
              | expr NE expr
              | expr OR expr
              | expr OROR expr
              | expr PLUS expr
              | expr EQ expr
              | expr MULEQ expr
              | expr DIVEQ expr
              | expr MINUSEQ expr
              | expr PLUSEQ expr
              | expr OREQ expr
              | expr ANDEQ expr
        """
        if p[2] == "=":
            if isinstance(p[1], ast.Call):
                subs = self._new_subscript(p, p[1].func, ast.ExtSlice(list(map(ast.Index, p[1].args))))
                p[1] = [subs]
            elif not isinstance(p[1], list):
                p[1] = [p[1]]
            
            for target in p[1]:
                target.ctx = ast.Store()
    
            p[0] = self._new_node(p, ast.Assign, p[1], p[3])
        elif p[2] == ':':
            p[0] = self._new_call(p, self._new_name(p, 'range'), p[1],
                                  self._new_node(p, ast.BinOp, p[3], ast.Add(),
                                                 self._new_node(p, ast.Num, 1)))
        elif p[2] == '.':
            if isinstance(p[3], ast.Subscript):
                p[0] = self._new_subscript(p, p[1], ast.Index(p[3]))
            else:
                p[0] = self._new_node(p, ast.Attribute, p[1], p[3], ast.Load())
        elif p[2] in Parser.COMPARE_OPS:
            p[0] = self._new_node(p, ast.Compare, p[1], [Parser.COMPARE_OPS[p[2]]()], [p[3]])
        elif p[2] in Parser.LOGIC_OPS:
            p[0] = self._new_node(p, ast.BoolOp, Parser.LOGIC_OPS[p[2]](), [p[1], p[3]])
        elif p[2] in Parser.BINARY_OPS:
            p[0] = self._new_node(p, ast.BinOp, p[1], Parser.BINARY_OPS[p[2]](), p[3])
        elif p[2] in Parser.ASSIGN_OPS:
            p[1].ctx = ast.Store()
            p[0] = self._new_node(p, ast.AugAssign, p[1], Parser.ASSIGN_OPS[p[2]](), p[3])
        else:
            raise NotImplementedError(p[2])
    
    def p_error(self, p):
        raise Parser.SyntaxError(p)
    
    def _new_node(self, p, kind, *args, **kw):
        node = kind(*args, **kw)
        node.lineno = p.lexer.lineno
        node.col_offset = 0
        return node
    
    def _new_arg(self, p, name, ann=None):
        return self._new_node(p, ast.arg, name, ann)
    
    def _new_name(self, p, name):
        return self._new_node(p, ast.Name, name, ast.Load())
    
    def _patch_index(self, p, index):
        if isinstance(index, ast.Index):
            if isinstance(index.value, ast.Num): index.value.n -= 1
            else: index.value = self._new_node(p, ast.BinOp, index.value, ast.Sub(), self._new_node(p, ast.Num, 1))
        elif isinstance(index, ast.Slice):
            if isinstance(index.lower, ast.Num): index.lower.n -= 1
            elif index.lower is not None: index.lower = self._new_node(p, ast.BinOp, index.lower, ast.Sub(), self._new_node(p, ast.Num, 1))
            if isinstance(index.upper, ast.Num): index.upper.n -= 1
            elif index.upper is not None: index.upper = self._new_node(p, ast.BinOp, index.upper, ast.Sub(), self._new_node(p, ast.Num, 1))
        elif isinstance(index, ast.ExtSlice):
            for dim in index.dims:
                self._patch_index(p, dim)
    
    def _new_subscript(self, p, target, index):
        self._patch_index(p, index)
        return self._new_node(p, ast.Subscript, target, index, ast.Load())

    def _new_list(self, p, data=None):
        return self._new_call(p,
            self._new_name(p, 'vector'),
            self._new_node(p, ast.List, data or [], ast.Load())
        )
    
    def _new_arguments(self, p, args=None):
        return self._new_node(p, ast.arguments, args or [], self._use_nargin, [], [], self._use_varargin, [])
    
    def _new_call(self, p, target, *args):
        return self._new_node(p, ast.Call, target, list(args), [], None, None)

_p = Parser()
_parsers = {}

def new(start='top'):
    if start not in _parsers:
        muted_stderr, sys.stderr = sys.stderr, io.StringIO()
        _parsers[start] = yacc.yacc(start=start, module=_p, debug=0, tabmodule='mlab_' + start)
        sys.stderr = muted_stderr
    
    return _parsers[start]

def parse(buf, filename=""):
    parser = new()
    l = lexer.new()
    p = parser.parse(buf, tracking=1, debug=0, lexer=l)
    return p

def dump(node, p='', outfile=sys.stdout):
    if isinstance(node, (ast.expr, ast.stmt)):
        print(p + node.__class__.__name__, node.lineno, file=outfile)
    else:
        print(p + node.__class__.__name__, file=outfile)
    for key, value in ast.iter_fields(node):
        if key == 'body' \
        or (isinstance(value, list) and not value) \
        or (key in ('starargs', 'kwargs') and value is None):
            continue
        print(p + '+ {0}={1}'.format(key, value), file=outfile)
    for child in ast.iter_child_nodes(node):
        dump(child, p + '  ', outfile)

if __name__ == '__main__':
    import os
    import types
    
    if len(sys.argv) < 2:
        print("Usage: {0} file.m ...".format(sys.argv[0]))
        sys.exit()
    
    for filename in sys.argv[1:]:
        print("Parsing", filename)
        try:
            buf = open(filename, 'r').read()
            p = parse(buf)
            m = ast.Module(body=p)
    
            dump(m, outfile=open(filename + '.tree', 'w'))
    
            d = compile(m, filename=filename, mode="exec")
            modname, _ = os.path.splitext(os.path.basename(filename))
            mod = types.ModuleType(modname, '')
            sys.modules[modname] = mod
            exec(d, mod.__dict__, mod.__dict__)
            setattr(mod, 'mod', lambda p, q: p % q)
            func = getattr(mod, 'r8_random')
            print(func(1, 2, 3))
        except Exception as e:
            print("Error:", e)

