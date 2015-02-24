'''
Created on 06.02.2015

@author: meinel
'''
import ast
import copy

from mlabpy import conf, rules
from mlabpy.rules.base import ref

class AstPatcher(ast.NodeTransformer):
    def __init__(self, rules=None):
        self._rules = rules or []
    
    def add_rule(self, rule):
        self._rules.append(rule)
    
    def _match_fields(self, match, node, refs):
        for field, value in ast.iter_fields(match):
            node_value = getattr(node, field, None)
            
            if isinstance(value, ast.AST):
                if not self._match(value, node_value, refs):
                    return False
            elif isinstance(value, list):
                if not all([self._match(m, n, refs) for (m, n) in zip(value, node_value)]):
                    return False
            elif value != node_value:
                return False

        return True
    
    def _match(self, match, node, refs):
        ref_name = getattr(match, 'ref', None)
        if ref_name is not None:
            refs[ref_name] = node
        
        if isinstance(node, match.__class__) \
        and self._match_fields(match, node, refs):
            return True
        
        return False
    
    def _update(self, replace, node, refs):
        if isinstance(replace, ref):
            repnode = copy.copy(refs[replace.name])
            for key, value in replace.kw.items():
                setattr(repnode, key, value)
        else:
            repnode = replace.__class__()
            ast.copy_location(repnode, node)
        
            for field, value in ast.iter_fields(replace):
                if isinstance(value, ref):
                    if value.name in refs:
                        setattr(repnode, field, refs[value.name])
                elif isinstance(value, ast.AST):
                    setattr(repnode, field, self._update(value, repnode, refs))
                elif isinstance(value, list):
                    setattr(repnode, field, [self._update(r, n, refs) for (r, n) in zip(value, getattr(replace, field))])
                else:
                    setattr(repnode, field, getattr(replace, field))
            
        ast.fix_missing_locations(repnode)
        return repnode
    
    def generic_visit(self, node):
        for rule in self._rules:
            refs = {}
            if self._match(rule.match, node, refs):
                if conf.DEBUG:
                    print(rule.__class__.__name__)
                    print(':', ast.dump(node))
                if hasattr(rule, 'replace'):
                    node = self._update(rule.replace, node, refs)
                    if conf.DEBUG:
                        print('>', ast.dump(node))
                    break
                elif hasattr(rule, 'eval'):
                    new_node = rule.eval(node, refs)
                    ast.copy_location(new_node, node)
                    node = new_node
                    if conf.DEBUG:
                        print('>', ast.dump(node))
                    break
        
        node = super(AstPatcher, self).generic_visit(node)
        return node

patcher = AstPatcher(rules.all)
