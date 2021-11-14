# Definitions of AST nodes


class ASTPrinter:
    def __init__(self):
        self.indent = 0

    def push(self):
        self.indent += 2

    def pop(self):
        self.indent -= 2

    def print(self, text):
        print(" " * self.indent + text)


class ASTNode:
    def print(self, printer):
        pass


class ProgramNode(ASTNode):
    def __init__(self):
        self.instructions = []

    def print(self, printer):
        printer.print("Program")
        for i in self.instructions:
            printer.push()
            i.print(printer)
            printer.pop()


class IdentifierNode(ASTNode):
    def __init__(self, identifier):
        self.identifier = identifier

    def print(self, printer):
        printer.print(f"Identifier: {self.identifier}")


class LiteralNode(ASTNode):
    def __init__(self, literal):
        self.literal = literal

    def print(self, printer):
        printer.print(f"Literal: {self.literal}")


class OperatorNode(ASTNode):
    def __init__(self, operator):
        self.operator = operator

    def print(self, printer):
        printer.print(f"Operator: {self.operator}")


class VarNode(ASTNode):
    def __init__(self, name):
        self.name = name

    def print(self, printer):
        printer.print(f"Var: {self.name}")


class CellNode(ASTNode):
    def __init__(self, name, address):
        self.name = name
        self.address = address

    def print(self, printer):
        printer.print(f"Cell: {self.name} at {self.address}")


class WhileNode(ASTNode):
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block

    def print(self, printer):
        printer.print("While")
        printer.push()
        self.condition.print(printer)
        printer.pop()
        printer.push()
        self.block.print(printer)
        printer.pop()


class IfNode(ASTNode):
    def __init__(self, condition, block, else_block=None):
        self.condition = condition
        self.block = block
        self.else_block = else_block

    def print(self, printer):
        printer.print("If")
        printer.push()
        self.condition.print(printer)
        printer.pop()
        printer.push()
        self.block.print(printer)
        printer.pop()
        if self.else_block is not None:
            printer.print("Else")
            printer.push()
            self.block.print(printer)
            printer.pop()


class ExpressionNode(ASTNode):
    def __init__(self, args):
        self.args = args

    def print(self, printer):
        printer.print("Expression")
        printer.print("(")
        for arg in self.args:
            printer.push()
            arg.print(printer)
            printer.pop()
        printer.print(")")


class BlockNode(ASTNode):
    def __init__(self, instructions):
        self.instructions = instructions

    def print(self, printer):
        printer.print("Block")
        for i in self.instructions:
            printer.push()
            i.print(printer)
            printer.pop()


class PrintNode(ASTNode):
    def __init__(self, expression):
        self.expression = expression

    def print(self, printer):
        printer.print("Print")
        printer.push()
        self.expression.print(printer)
        printer.pop()
