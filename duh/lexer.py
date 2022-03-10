"""Simple lexer for duh language"""
import string
from duh.lang import *


class Tokens:
    def __init__(self, tokens):
        self.tokens = tokens
        self.head = 0

    def next(self):
        if len(self.tokens) > self.head + 1:
            return self.tokens[self.head + 1]

    def current(self):
        if len(self.tokens) > self.head:
            return self.tokens[self.head]

    def advance(self):
        token = self.current()
        if self.head < len(self.tokens):
            self.head += 1
        return token

    def empty(self):
        return len(self.tokens) <= self.head


def lex(source):
    tokens = []
    current_token = ""

    line = 0
    char_index = 0

    current_span = Span(source, line, 0, 0)
    for char in source.text:
        char_index += 1

        if (current_token and (not compatible(current_token, char)
                               or char in string.whitespace)):
            tokens.append(create_token(current_token, current_span))
            current_span.end = char_index
            current_span = Span(source, line, char_index, char_index)
            current_token = ""

        if char == '\n':
            line += 1
        if char in string.whitespace: continue

        current_token += char

    if current_token:
        tokens.append(create_token(current_token, current_span))
    return Tokens(tokens)
