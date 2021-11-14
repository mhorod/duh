# Compilation of while loops

from duh.compiler.core import *
from duh.compiler.expressions import *
from duh.compiler.conditionals import *


def compile_while(node, compiler):
    if isinstance(node.condition,
                  ExpressionNode) and len(node.condition.args) > 1:
        op = node.condition.args[0].operator
        if op.code in operator_to_while_compiler:
            return operator_to_while_compiler[op.code](node, compiler)
    else:
        return compile_other_op_while(node, compiler)


def compile_lt_while(node, compiler):
    ''' Compile while (< a b)'''
    return compile_while_with_builder(node, compiler,
                                      transform_comparison_condition,
                                      build_pattern_A_while, Instruction.JNEG)


def compile_leq_while(node, compiler):
    ''' Compile while (<= a b)'''
    return compile_while_with_builder(node, compiler,
                                      transform_comparison_condition,
                                      build_pattern_B_while, Instruction.JNEG)


def compile_gt_while(node: WhileNode, compiler: Compiler):
    '''Compile while (> a b)'''
    node.condition = invert_comparison(node.condition)
    return compile_lt_while(node, compiler)


def compile_geq_while(node: WhileNode, compiler: Compiler):
    '''Compile while (>= a b)'''
    node.condition = invert_comparison(node.condition)
    return compile_leq_while(node, compiler)


def compile_while_with_builder(node, compiler, transform_condition,
                               build_while, jump):
    '''Generic if compiling function
    Transforms condition using transform_condition into form that can use jump easily
    Then compiles everything together using build_if
    jump can be either JNEG when comparing order and JZERO when comparing equality
    '''
    condition = transform_condition(node.condition, compiler)
    block = compile_node(node.block, compiler)
    return build_while(condition, block, jump)


def compile_eq_while(node: IfNode, compiler: Compiler):
    '''Compile while (== a b)'''
    return compile_while_with_builder(node, compiler,
                                      transform_comparison_condition,
                                      build_pattern_A_while, Instruction.JZERO)


def compile_neq_while(node: IfNode, compiler: Compiler):
    '''Compile while (!= a b)'''
    return compile_while_with_builder(node, compiler,
                                      transform_comparison_condition,
                                      build_pattern_B_while, Instruction.JZERO)


def compile_other_op_while(node: IfNode, compiler: Compiler):
    '''Compile while (op a b)'''
    return compile_while_with_builder(
        node, compiler,
        lambda condition, compiler: compile_expression(condition, compiler),
        build_pattern_B_while, Instruction.JZERO)


def build_pattern_A_while(condition, block, jump):
    '''Compile while into the following form

    condition:
    {jump} body:
    JUMP endwhile:
    block:
    JUMP beginwhile:
    endwhile:
    '''
    instructions = CompiledInstructions()
    instructions += condition

    if block:
        jump_to_block = Instruction(jump, address_mode=Address.IMMEDIATE)
        jump_to_while_end = Instruction(Instruction.JUMP,
                                        address_mode=Address.IMMEDIATE)

        instructions.append(jump_to_block)
        instructions.append(jump_to_while_end)

        instructions += block
        jump_to_block.address = block[0].line

    jump_to_begin = Instruction(Instruction.JUMP,
                                address_mode=Address.IMMEDIATE)
    instructions.append(jump_to_begin)

    if block:
        jump_to_while_end.address = next_address(instructions[-1].line)
    jump_to_begin.address = instructions[0].line

    return instructions


def build_pattern_B_while(condition, block, jump):
    '''Compile while into the following form
    condition:
    {jump} endwhile:
    block:
    JUMP beginwhile:
    endwhile:
    '''

    instructions = CompiledInstructions()
    instructions += condition

    jump_to_while_end = Instruction(jump, address_mode=Address.IMMEDIATE)
    instructions.append(jump_to_while_end)
    instructions += block
    jump_to_begin = Instruction(Instruction.JUMP,
                                address_mode=Address.IMMEDIATE)
    instructions.append(jump_to_begin)

    jump_to_while_end.address = next_address(instructions[-1].line)
    jump_to_begin.address = instructions[0].line

    return instructions


operator_to_while_compiler = {
    Operator.LT: compile_lt_while,
    Operator.LEQ: compile_leq_while,
    Operator.GT: compile_gt_while,
    Operator.GEQ: compile_geq_while,
    Operator.EQ: compile_eq_while,
    Operator.NEQ: compile_neq_while,
}
