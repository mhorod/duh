# Definitions of language objects

import string
KEYWORD_CHARS = string.ascii_letters

NAME_CHARS = string.ascii_letters + string.digits + ':' + '_' + "\'"
LITERAL_CHARS = string.digits + '-xbo'
OPERATOR_CHARS = '<=>+-/&|^~!@'


def compatible(token, char):
    """Determine if char can be appended to token"""
    if token == '-' and char in string.digits:
        return True
    if is_literal(token + char): return True
    return is_valid_name(token + char) or is_valid_operator(token + char)


def is_valid_name(name):
    return all(c in NAME_CHARS for c in name)


def is_valid_operator(operator):
    return operator in str_to_operator


class TokenGroup:
    KEYWORD, SYMBOL, OPERATOR, NAME, LITERAL = range(5)


class Source:
    def __init__(self, filename, text):
        self.filename = filename
        self.text = text


class Span:
    def __init__(self, source, line, begin, end):
        self.source = source
        self.line = line
        self.begin = begin
        self.end = end


class Token:
    def __init__(self, content, span, group=None, code=None):
        self.content = content
        self.group = group
        self.code = code
        self.span = span

    def __str__(self):
        return f"token: {self.content}"


class Keyword(Token):
    (VAR, CELL, WHILE, IF, ELSE, RETURN, GOTO, PRINT) = range(8)

    def __init__(self, code, span):
        super().__init__(keyword_to_str[code], span, TokenGroup.KEYWORD, code)

    def __str__(self):
        return f"keyword: {self.content}"


str_to_keyword = {
    "var": Keyword.VAR,
    "cell": Keyword.CELL,
    "while": Keyword.WHILE,
    "if": Keyword.IF,
    "else": Keyword.ELSE,
    "return": Keyword.RETURN,
    "goto": Keyword.GOTO,
    "print": Keyword.PRINT,
}

keyword_to_str = {keyword: s for s, keyword in str_to_keyword.items()}


class Operator(Token):
    (ASSIGN, EQ, NEQ, LT, LEQ, GT, GEQ, ADD, SUB, SHL, SHR, AND, OR, XOR, NOT,
     AT, INC, DEC) = range(18)

    def __init__(self, code, span):
        super().__init__(opetator_to_str[code], span, TokenGroup.OPERATOR,
                         code)

    def __str__(self):
        return f"operator: {self.content}"


str_to_operator = {
    "=": Operator.ASSIGN,
    "==": Operator.EQ,
    "!=": Operator.NEQ,
    "<": Operator.LT,
    "<=": Operator.LEQ,
    '>': Operator.GT,
    '>=': Operator.GEQ,
    '+': Operator.ADD,
    '-': Operator.SUB,
    '>>': Operator.SHR,
    '<<': Operator.SHL,
    "&": Operator.AND,
    "|": Operator.OR,
    "^": Operator.XOR,
    "~": Operator.NOT,
    "@": Operator.AT,
    '++': Operator.INC,
    '--': Operator.DEC,
}

opetator_to_str = {op: s for s, op in str_to_operator.items()}


class Symbol(Token):
    LEFT_BRACE, RIGHT_BRACE, LEFT_PAREN, RIGHT_PAREN, SEMICOLON, HASH, COLON = range(
        7)

    def __init__(self, code, span):
        super().__init__(symbol_to_str[code], span, TokenGroup.SYMBOL, code)

    def __str__(self):
        return f"symbol: {self.content}"


str_to_symbol = {
    "{": Symbol.LEFT_BRACE,
    "}": Symbol.RIGHT_BRACE,
    "(": Symbol.LEFT_PAREN,
    ")": Symbol.RIGHT_PAREN,
    ";": Symbol.SEMICOLON,
    "#": Symbol.HASH,
    ":": Symbol.COLON,
}

symbol_to_str = {symbol: s for s, symbol in str_to_symbol.items()}


class Identifier(Token):
    def __init__(self, content, span):
        super().__init__(content, span, TokenGroup.NAME)

    def __str__(self):
        return f"identifier: {self.content}"


class Literal(Token):
    def __init__(self, content, span):
        super().__init__(content, span, TokenGroup.LITERAL)
        self.value = literal_to_value(content)

    def __str__(self):
        return f"literal: {self.content} ({self.value})"


def create_token(content, span):
    for key, Class in str_to_token_dicts:
        if content in key: return Class(key[content], span)

    if is_literal(content):
        return Literal(content, span)
    else:
        return Identifier(content, span)


str_to_token_dicts = [
    (str_to_symbol, Symbol),
    (str_to_keyword, Keyword),
    (str_to_operator, Operator),
]


def is_literal(content):
    return literal_to_value(content) is not None


def literal_to_value(content):
    '''Convert text into literal'''
    bases = [10, 2, 8, 16]
    prefixes = ['', '0b', '0o', '0x']
    for b, p in zip(bases, prefixes):
        if not content.startswith(p):
            continue
        try:
            return int(content, b)
        except:
            pass


def is_unary(op):
    return op.code in [Operator.NOT, Operator.AT, Operator.INC, Operator.DEC]
