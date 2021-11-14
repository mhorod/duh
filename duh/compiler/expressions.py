# Compilation of expressions

from duh.compiler.core import *
from duh.lang import *
from duh.ast import *


def store_in_memory(node: ASTNode,
                    compiler: CompiledInstructions,
                    address=None) -> (CompiledInstructions, Address):
    '''Evaluate expression and save the result in memory.
    Function returns instructions and Address where the result is stored
    '''
    if isinstance(node, IdentifierNode):
        # If the node is already a variable then there's nothing to do
        return CompiledInstructions(), identifier_address(node, compiler)
    else:
        if isinstance(node, ExpressionNode) and len(node.args) == 1:
            return store_in_memory(node.args[0], compiler)
        instructions = compile_expression(node, compiler)
        if address is None:
            address = compiler.variables.tvs.push()
        instructions.append(
            Instruction(Instruction.STORE, address, Address.IMMEDIATE))
        return instructions, address


def compile_expression(node: ASTNode,
                       compiler: Compiler) -> CompiledInstructions:
    '''Evaluate expression and leave the result in AC'''
    if isinstance(node, IdentifierNode):
        address = identifier_address(node, compiler)
        return CompiledInstructions([LoadInstruction(address)])
    elif isinstance(node, LiteralNode):
        address = Address(node.literal.value)
        return CompiledInstructions([LoadLiteralInstruction(address)])
    elif len(node.args) == 1:
        return compile_expression(node.args[0], compiler)
    else:
        op = node.args[0].operator
        if op.code in operator_to_compiler:
            return operator_to_compiler[op.code](node, compiler)
        elif is_unary(op):
            return store_in_ac_unary(node, compiler)
        else:
            return store_in_ac_binary(node, compiler)


def store_in_ac_unary(expression, compiler):
    """Evaluate expression assuming it's operation is unary"""
    op = expression.args[0].operator
    if op.code in operator_to_compiler:
        return operator_to_compiler[op.code](expression, compiler)

    code = operator_to_instruction_code(op)
    arg = expression.args[1]
    instructions = evaluate_argument(arg, compiler)
    instructions.append(Instruction(code))
    return instructions


def store_in_ac_binary(expression: ExpressionNode, compiler: Compiler):
    """Evaluate expression assuming it's operation is binary"""

    op = expression.args[0].operator
    code = operator_to_instruction_code(op)

    args = expression.args[1:]
    store_in_mem_args = args[1:]
    store_in_ac_arg = args[0]

    arg_results = [
        evaluate_argument(arg, compiler) for arg in store_in_mem_args
    ]
    instructions, addresses = list(zip(*arg_results))
    instructions = sum(instructions, start=CompiledInstructions())
    instructions += compile_expression(store_in_ac_arg, compiler)
    for address in addresses:
        instructions.append(Instruction(code, address, address.mode))
        compiler.variables.tvs.pop(address)

    return instructions


def evaluate_argument(node: ASTNode, compiler: Compiler):
    '''Evaluates node and stores value in memory in case of expressions.
    In case of literals just returns the address'''
    if isinstance(node, LiteralNode):
        return CompiledInstructions(), literal_address(node)
    else:
        return store_in_memory(node, compiler)


def compile_assignment(node: ASTNode,
                       compiler: Compiler) -> CompiledInstructions:
    '''Compiles assignment.
    Only identifiers and references can be assigned to.
    '''
    arg = node.args[1]

    instructions = CompiledInstructions()

    address = None
    if isinstance(arg, IdentifierNode):
        address = identifier_address(arg, compiler)
        address_mode = Address.IMMEDIATE
    else:
        ref_instructions, address = compile_reference(arg, compiler)
        address_mode = Address.DIRECT
        instructions += ref_instructions

    store_instructions = compile_expression(node.args[2], compiler)
    instructions += store_instructions

    instr = Instruction(Instruction.STORE, address, address_mode)
    instructions.append(instr)
    compiler.variables.tvs.pop(address)
    return instructions


def compile_reference(node: ExpressionNode, compiler: Compiler):
    """Compiles (@ x) when it's an lvalue"""
    return store_in_memory(node.args[1], compiler)


def compile_dereference(node: ExpressionNode, compiler: Compiler):
    """Compiles (@ x) when it's an rvalue"""
    instructions, address = evaluate_argument(node.args[1], compiler)
    mode = address.mode + 1
    instruction = Instruction(Instruction.LOAD, address, mode)
    instructions.append(instruction)
    compiler.variables.tvs.pop(address)
    return instructions


def compile_increment(expression, variables):
    instructions = compile_expression(expression.args[1], variables)
    instruction = Instruction(Instruction.ADD,
                              address=Address(1),
                              address_mode=Address.IMMEDIATE)
    instructions.append(instruction)
    return instructions


def compile_decrement(expression, variables):
    instructions = compile_expression(expression.args[1], variables)
    instruction = Instruction(Instruction.SUB,
                              address=Address(1),
                              address_mode=Address.IMMEDIATE)
    instructions.append(instruction)
    return instructions


def transform_comparison_condition(node: ExpressionNode, compiler: Compiler):
    return compile_expression(convert_comparison(node), compiler)


def convert_comparison(node: ExpressionNode):
    '''Converts comparison expression into arithmetic one'''
    op, *args = node.args
    op = op.operator

    if op.code == Operator.LT:
        op = OperatorNode(Operator(Operator.SUB, None))
    elif op.code == Operator.LEQ:
        op = OperatorNode(Operator(Operator.SUB, None))
        args = args[::-1]

    elif op.code == Operator.EQ or op.code == Operator.NEQ:
        op = OperatorNode(Operator(Operator.XOR, None))

    return ExpressionNode([op] + args)


def invert_comparison(node: ExpressionNode):
    '''Converts comparison into inverted one, e.g (a > b) -> (b < a)'''
    op, *args = node.args
    op = op.operator
    args = args[::-1]

    if op.code == Operator.GT:
        op = OperatorNode(Operator(Operator.LT, None))
    elif op.code == Operator.GEQ:
        op = OperatorNode(Operator(Operator.LEQ, None))

    return ExpressionNode([op] + args)


operator_to_compiler = {
    Operator.ASSIGN: compile_assignment,
    Operator.AT: compile_dereference,
    Operator.INC: compile_increment,
    Operator.DEC: compile_decrement,
}
