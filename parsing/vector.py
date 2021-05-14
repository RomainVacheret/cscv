import enum


class SyntaxToken(enum.Enum):
    OP_PLS, \
    OP_MIN, \
    OP_MUL, \
    OP_DIV, \
    OP_MOD, \
    OP_XPP, \
    OP_PPX, \
    OP_XMM, \
    OP_MMX, \
    OP_EGL, \
    OP_EEGL, \
    OP_DIF, \
    OP_AND, \
    OP_OR, \
    OP_NOT, \
    OP_INF, \
    OP_INFE, \
    OP_SUP, \
    OP_SUPE, \
    OP_ADDR, \
    REF_DOT, \
    REF_ARROW, \
    FOR, \
    WHILE, \
    DO_WHILE, \
    IF, \
    ELSE, \
    FUNC_CALL, \
    PTR_DECL, \
    TYPE_DECL, \
    ARR_DECL, \
    CAST = range(32)

class Vector:
    syntax_map = {
        '+': SyntaxToken.OP_PLS,
        '-': SyntaxToken.OP_MIN,
        '*': SyntaxToken.OP_MUL,
        '/': SyntaxToken.OP_DIV,
        '%': SyntaxToken.OP_MOD,
        'p++': SyntaxToken.OP_XPP,
        '++': SyntaxToken.OP_PPX,
        'p--': SyntaxToken.OP_XMM,
        '--': SyntaxToken.OP_MMX,
        '=': SyntaxToken.OP_EGL,
        '==': SyntaxToken.OP_EEGL,
        '!=': SyntaxToken.OP_DIF,
        '&&': SyntaxToken.OP_AND,
        '||': SyntaxToken.OP_OR,
        '!': SyntaxToken.OP_NOT,
        '.': SyntaxToken.REF_DOT,
        '->': SyntaxToken.REF_ARROW,
        '<': SyntaxToken.OP_INF,
        '<=': SyntaxToken.OP_INFE,
        '>': SyntaxToken.OP_SUP,
        '>=': SyntaxToken.OP_SUPE,
        'sizeof': SyntaxToken.FUNC_CALL,
        '&': SyntaxToken.OP_ADDR
    }

    def __init__(self, values=None):
        if values is None:
            self.values = [0 for _ in range(len(SyntaxToken))]
        else:
            self.values = values 
    
    def incremente_token(self, token, value=1):
        self.values[token.value] += value
    
    def get_token_from_op(self, value):
        try:
            return Vector.syntax_map[value]
        except KeyError:
            return None
        
    def incremente_token_from_op(self, op):
        op_token = self.get_token_from_op(op)
        self.incremente_token(op_token)
    
    def to_list(self):
        return self.values
    
    def summary(self):
        string = []
        delimiter = '+-----------------------+---+'

        string.append(delimiter)
        for idx, val in enumerate(self.values):
            if val:
                string.append(f'|{SyntaxToken(idx)}\t| {val} |')
        string.append(delimiter)

        return '\n'.join(string)
    
    @classmethod
    def filter_vectors(cls, *iterable):
        return list(filter(lambda x: isinstance(x, Vector), iterable))

    @classmethod
    def merge(cls, *vectors):
        if len(vectors) < 3 :
            vectors = [*vectors, Vector()]
        
        vectors = Vector.filter_vectors(*vectors)
        lists = (vector.values for vector in vectors)

        return Vector([sum(values) for values in zip(*lists)])
    
    @classmethod
    def vector_list_to_list_of_list(cls, vector_list):
        return [vector.to_list() for vector in vector_list]
    
    def __str__(self):
        return str(self.values)
    
    def __repr__(self):
        return str(self.values)     