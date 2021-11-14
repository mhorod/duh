'''
Module containing basic functions compiling ast
'''

from duh.ast import *
from duh.compiler.core import *
from duh.compiler.expressions import *
from duh.compiler.conditionals import *
from duh.compiler.while_loops import *


def compile_block(node: ASTNode, compiler: Compiler) -> CompiledInstructions:
    return sum((compile_node(instr, compiler) for instr in node.instructions),
               start=CompiledInstructions())


def compile_print(node: ASTNode, compiler: Compiler) -> CompiledInstructions:
    instructions, address = evaluate_argument(node.expression, compiler)
    instructions.append(Instruction(Instruction.PRINT, address, address.mode))
    compiler.variables.tvs.pop(compiler)
    return instructions


def no_compile(node: ASTNode, compiler: Compiler):
    return CompiledInstructions()


def compile_program(program_node: ProgramNode,
                    Compiler) -> CompiledInstructions:
    variables = variables_from_node(program_node)
    compiler = Compiler(variables, node_type_to_compiler)
    instructions = compile_node(program_node, compiler)
    instructions.append(Instruction(Instruction.STOP))
    assign_addresses(instructions, variables)
    return instructions


node_type_to_compiler = {
    ProgramNode: compile_block,
    BlockNode: compile_block,
    ExpressionNode: compile_expression,
    IdentifierNode: compile_expression,
    LiteralNode: compile_expression,
    IfNode: compile_if,
    WhileNode: compile_while,
    PrintNode: compile_print,
    VarNode: no_compile,
    CellNode: no_compile,
}
