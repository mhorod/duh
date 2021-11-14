from duh.ast import *
from duh.lang import *


def parse_tokens(tokens):
    root = ProgramNode()
    root.instructions = parse_instructions(tokens)
    return root


def parse_instructions(tokens):
    instructions = []
    while (not tokens.empty()
           and not is_symbol(tokens.current(), Symbol.RIGHT_BRACE)):

        instructions.append(parse_instruction(tokens))
    return instructions


def parse_instruction(tokens):
    if tokens.current().group == TokenGroup.KEYWORD:
        return keyword_to_parser[tokens.current().code](tokens)
    else:
        return parse_expression(tokens)


def parse_var(tokens):
    tokens.advance()
    name = tokens.advance()
    return VarNode(name)


def parse_cell(tokens):
    tokens.advance()
    name = tokens.advance()
    address = tokens.advance()
    return CellNode(name, address)


def parse_while(tokens):
    tokens.advance()
    cond = parse_expression(tokens)
    block = parse_block(tokens)
    return WhileNode(cond, block)


def parse_if(tokens):
    tokens.advance()
    cond = parse_expression(tokens)
    block = parse_block(tokens)
    else_block = None
    if (not tokens.empty() and tokens.current().group == TokenGroup.KEYWORD
            and tokens.current().code == Keyword.ELSE):
        tokens.advance()
        else_block = parse_block(tokens)
    return IfNode(cond, block, else_block)


def parse_paren_expression(tokens):
    expect_symbol(tokens, Symbol.LEFT_PAREN)
    expr_args = []
    while (not tokens.empty()
           and not is_symbol(tokens.current(), Symbol.RIGHT_PAREN)):
        if is_symbol(tokens.current(), Symbol.LEFT_PAREN):
            arg = parse_paren_expression(tokens)
        else:
            token = tokens.advance()
            if type(token) in token_type_to_node_type:
                arg = token_type_to_node_type[type(token)](token)
            else:
                print(f"Got confused on '{token}' while parsing expression")
        expr_args.append(arg)
    expect_symbol(tokens, Symbol.RIGHT_PAREN)
    return ExpressionNode(expr_args)


def parse_expression(tokens):
    if is_symbol(tokens.current(), Symbol.LEFT_PAREN):
        expr = parse_paren_expression(tokens)
    else:
        expr = parse_non_paren_expression(tokens)
    return expr


token_type_to_node_type = {
    Operator: OperatorNode,
    Identifier: IdentifierNode,
    Literal: LiteralNode,
}


def parse_non_paren_expression(tokens):
    '''Non paren expression can be either an identifier or a literal'''
    token = tokens.advance()
    return token_type_to_node_type[type(token)](token)


def parse_block(tokens):
    if is_symbol(tokens.current(), Symbol.LEFT_BRACE):
        return parse_braced_block(tokens)
    else:
        instructions = [parse_instruction(tokens)]
        return BlockNode(instructions)


def parse_braced_block(tokens):
    expect_symbol(tokens, Symbol.LEFT_BRACE)
    instructions = parse_instructions(tokens)
    expect_symbol(tokens, Symbol.RIGHT_BRACE)
    return BlockNode(instructions)


def parse_print(tokens):
    tokens.advance()
    expression = parse_expression(tokens)
    return PrintNode(expression)


class ParsingError(Exception):
    pass


class UnexpectedToken(ParsingError):
    pass


class UnexpectedEOF(ParsingError):
    pass


def is_symbol(token, symbol):
    return token.group == TokenGroup.SYMBOL and token.code == symbol


def expect_symbol(tokens, symbol):
    if tokens.empty():
        raise UnexpectedEOF("Unexpected End Of File")
    if not is_symbol(tokens.current(), symbol):
        raise UnexpectedToken(f"Unexpected: {tokens.current().content}")
    tokens.advance()


keyword_to_parser = {
    Keyword.VAR: parse_var,
    Keyword.CELL: parse_cell,
    Keyword.WHILE: parse_while,
    Keyword.IF: parse_if,
    Keyword.PRINT: parse_print,
}
