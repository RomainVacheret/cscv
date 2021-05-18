from pycparser.c_ast import NodeVisitor, FuncDef
from pycparser.c_parser import CParser

from parsing.logger import get_logger
from parsing.vector import Vector, SyntaxToken

class FunctionOutput:
    def __init__(self, name, vector, label=None):
        self.name = name
        self.vector = vector
        self.filename = None
        self.label = label
    
    def extract_vector(self):
        return self.vector
    
    def extract_name_and_filename(self):
        return self.name, self.filename
    
    def split_context(self):
        return self.extract_vector(), self.label or self.extract_name_and_filename()
    
    @classmethod
    def split_context_list(cls, list_):
        return list(map(list, zip(*(fnc_outp.split_context() for fnc_outp in list_))))

    @classmethod
    def label_elements(self, outputs):
        counter = 0

        for output in outputs:
            output.label = f'D{counter}'
            counter += 1
        
    @classmethod
    def summarize_elements(self, outputs):
        counter = 0
        strings = []

        for output in outputs:
            strings.append(f'D{counter}\n{output.vector.summary()}')
            counter += 1
        
        return '\n'.join(strings)
    
    def __str__(self):
        return f'name: {self.name}, vector:{self.vector}'
    
    def __repr__(self):
        filename_string = f', filename: {self.filename}' if self.filename is not None else ''
        return f'name: {self.name}, vector:{self.vector}{filename_string}'


class ASTVisitor(NodeVisitor):
    def __init__(self, logging=False):
        self.logger = get_logger(__name__)
        self.stack_id = 0
        self._get_type_name = lambda node_: type(node_).__name__
        self.logging = logging

    def visit(self, node):
        if self.logging:
            stack_id = self.stack_id 
            self.stack_id += 1
            self.logger.debug(f'Visiting {self._get_type_name(node)} - {stack_id}')

        result = super().visit(node)

        if self.logging:
            self.logger.debug(f'Result type: {self._get_type_name(result)} - {stack_id}')

        return result

    def visit_FileAST(self, node):
        func_def = [self.visit(child) for child in node.ext if isinstance(child, FuncDef)]

        if self.logging:
            for func in func_def:
                self.logger.debug(f'{func.name}: \n{func.vector.summary()}')
        
        return func_def

    def visit_FuncDef(self, node):
        params = node.decl.type.args
        params_vector = self.visit(params) if params else Vector()

        body_vector = self.visit(node.body) or Vector()
        vector = Vector.merge(params_vector, body_vector) 
        
        return FunctionOutput(node.decl.name, vector)
    
    def visit_Compound(self, node):
        items = [self.visit(item) for item in node.block_items] \
            if node.block_items is not None else [Vector()]

        vector = Vector.merge(*items)
        return vector
    
    def visit_ParamList(self, node):
        get_param = lambda decl: decl.type
        params = []
        for param in node.params:
            p = self.visit(param)
            params.append(p)

        return Vector.merge(*params)
    
    def visit_Cast(self, node):
        vector = Vector()
        vector.incremente_token(SyntaxToken.CAST)

        expr_vector = self.visit(node.expr) or Vector()
        type_vector = self.visit(node.to_type) or Vector()

        vector = Vector.merge(vector, expr_vector, type_vector)
        return vector
    
    def visit_Decl(self, node):
        return self.visit(node.type) or Vector()
    
    def visit_TypeDecl(self, node):
        vector = Vector()
        vector.incremente_token(SyntaxToken.TYPE_DECL)
        return vector
    
    def visit_PtrDecl(self, node):
        vector = Vector()
        vector.incremente_token(SyntaxToken.PTR_DECL)

        type_vector = self.visit(node.type)
        vector = Vector.merge(vector, type_vector)
        return vector

    def visit_ArrayDecl(self, node):
        vector = Vector()
        vector.incremente_token(SyntaxToken.ARR_DECL)

        type_vector = self.visit(node.type) or Vector()
        dim_vector = self.visit(node.dim) or Vector()

        vector = Vector.merge(vector, type_vector, dim_vector)
        return vector

    def visit_ArrayRef(self, node):
        name_result = self.visit(node.name)
        name_vector = name_result if isinstance(name_result, Vector) else Vector()
        subscript_vector = self.visit(node.subscript)

        vector = Vector.merge(name_vector, subscript_vector)
        return vector
    
    def visit_StructRef(self, node):
        vector = Vector()
        vector.incremente_token_from_op(node.type)
        
        field_result = self.visit(node.field)
        field_vector = field_result if isinstance(field_result, Vector) else Vector()

        vector = Vector.merge(vector, field_vector)
        return vector
    
    def visit_IdentifierType(self, node):
        # list of strings
        return node.names
    
    def visit_BinaryOp(self, node):
        vector = Vector()
        # print(node.op)
        vector.incremente_token_from_op(node.op)

        left_vector = self.visit(node.left) or Vector()
        right_vector = self.visit(node.right) or Vector()
        
        vector = Vector.merge(vector, left_vector, right_vector)
        return vector

    def visit_Assignment(self, node):
        vector = Vector()
        vector.incremente_token_from_op(node.op)

        left_result = self.visit(node.lvalue)
        left_vector = left_result if isinstance(left_result, Vector) else Vector()
        right_vector = self.visit(node.rvalue) or Vector()

        vector = Vector.merge(vector, left_vector, right_vector)
        return vector

    def visit_UnaryOp(self, node):
        vector = Vector()
        vector.incremente_token_from_op(node.op)
        expr_vector = self.visit(node.expr) or Vector()

        vector = Vector.merge(vector, expr_vector)
        return vector

    def visit_Return(self, node):
        result = self.visit(node.expr) if node.expr is not None else Vector()
        return result if isinstance(result, Vector) else Vector()
    
    def visit_ID(self, node):
        return node.name
    
    def visit_FuncCall(self, node):
        vector = Vector()
        vector.incremente_token(SyntaxToken.FUNC_CALL)

        args_vector = Vector.merge(*[self.visit(arg) for arg in node.args]) or Vector()
        vector = Vector.merge(vector, args_vector)

        return vector
    
    def visit_If(self, node):
        vector = Vector()
        vector.incremente_token(SyntaxToken.IF)

        cond_vector = self.visit(node.cond) or Vector()
        iftrue_vector = self.visit(node.iftrue) or Vector()
        iffalse_vector = self.visit(node.iffalse) if node.iffalse is not None else Vector()
        
        vector = Vector.merge(vector, cond_vector, iftrue_vector, iffalse_vector)

        if node.iffalse is not None:
            vector.incremente_token(SyntaxToken.ELSE)

        return vector
    
    def visit_DeclList(self, node):
        decls = [self.visit(decl) for decl in node.decls]
        return Vector.merge(*decls)
    
    def visit_For(self, node):
        init_vector = self.visit(node.init) or Vector()

        cond_vector = self.visit(node.cond) or Vector()
        next_vector = self.visit(node.next) or Vector()
        statement_vector = self.visit(node.stmt) or Vector()

        vector = Vector.merge(init_vector, cond_vector, next_vector, statement_vector)
        vector.incremente_token(SyntaxToken.FOR)

        return vector
    
    def visit_While(self, node):
        cond_vector = self.visit(node.cond) or Vector()
        statement_vector = self.visit(node.stmt) or Vector()

        vector = Vector.merge(cond_vector, statement_vector)
        vector.incremente_token(SyntaxToken.WHILE)

        return vector

    def visit_DoWhile(self, node):
        cond_vector = self.visit(node.cond) or Vector()
        statement_vector = self.visit(node.stmt) or Vector()

        vector = Vector.merge(cond_vector, statement_vector)
        vector.incremente_token(SyntaxToken.DO_WHILE)

        return vector  