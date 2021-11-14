# Compilation of if statements

from duh.compiler.core import *
from duh.ast import *
from duh.compiler.expressions import *


def compile_if(node: IfNode, compiler: Compiler):
    if isinstance(node.condition,
                  ExpressionNode) and len(node.condition.args) > 1:
        op = node.condition.args[0].operator
        if op.code in operator_to_if_compiler:
            return operator_to_if_compiler[op.code](node, compiler)

    return compile_other_op_if(node, compiler)


def compile_lt_if(node: IfNode, compiler: Compiler):
    '''Compile if (< a b)'''
    return compile_if_with_builder(node, compiler,
                                   transform_comparison_condition,
                                   build_pattern_A_if, Instruction.JNEG)


def compile_leq_if(node: IfNode, compiler: Compiler):
    '''Compile if (<= a b)'''
    return compile_if_with_builder(node, compiler,
                                   transform_comparison_condition,
                                   build_pattern_B_if, Instruction.JNEG)


def compile_gt_if(node: IfNode, compiler: Compiler):
    '''Compile if (> a b)'''
    node.condition = invert_comparison(node.condition)
    return compile_lt_if(node, compiler)


def compile_geq_if(node: IfNode, compiler: Compiler):
    '''Compile if (>= a b)'''
    node.condition = invert_comparison(node.condition)
    return compile_leq_if(node, compiler)


def compile_eq_if(node: IfNode, compiler: Compiler):
    '''Compile if (== a b)'''
    return compile_if_with_builder(node, compiler,
                                   transform_comparison_condition,
                                   build_pattern_A_if, Instruction.JZERO)


def compile_neq_if(node: IfNode, compiler: Compiler):
    '''Compile if (!= a b)'''
    return compile_if_with_builder(node, compiler,
                                   transform_comparison_condition,
                                   build_pattern_B_if, Instruction.JZERO)


def compile_other_op_if(node: IfNode, compiler: Compiler):
    '''Compile if (op a b)'''
    return compile_if_with_builder(
        node, compiler,
        lambda condition, compiler: compile_expression(condition, compiler),
        build_pattern_B_if, Instruction.JZERO)


def compile_if_with_builder(node, compiler, transform_condition, build_if,
                            jump):
    '''Generic if compiling function
    Transforms condition using transform_condition into form that can use jump easily
    Then compiles everything together using build_if
    jump can be either JNEG when comparing order and JZERO when comparing equality
    '''
    condition = transform_condition(node.condition, compiler)
    block = compile_node(node.block, compiler)
    else_block = compile_node(node.else_block,
                              compiler) if node.else_block else None

    return build_if(condition, block, else_block, jump)


def build_pattern_A_if(condition, block, else_block, jump):
    '''Compile if into the following form
    condition:
    {jump} if:
    JUMP else:
    if:
    JUMP endif:
    else:
    endif:
    '''
    instructions = CompiledInstructions()
    instructions += condition

    if block:
        jump_to_if = Instruction(jump, address_mode=Address.IMMEDIATE)
        jump_to_else = Instruction(Instruction.JUMP,
                                   address_mode=Address.IMMEDIATE)

        instructions.append(jump_to_if)
        instructions.append(jump_to_else)

        instructions += block
        jump_to_if.address = block[0].line
        jump_to_else.address = next_address(block[-1].line)

    if else_block:
        jump_to_else.address = else_block[0].line
        jump_to_end = Instruction(Instruction.JUMP,
                                  address_mode=Address.IMMEDIATE)
        jump_to_end.address = next_address(else_block[-1].line)

        instructions.append(jump_to_end)
        instructions += else_block

    return instructions


def build_pattern_B_if(condition, block, else_block, jump):
    '''Compile if into the following form
    condition:
    {jump} else:
    if:
    JUMP endif:
    else:
    endif:
    '''
    instructions = CompiledInstructions()
    instructions += condition
    jump_to_else = Instruction(jump, address_mode=Address.IMMEDIATE)

    if block:
        jump_to_else.address = next_address(block[-1].line)
        instructions.append(jump_to_else)
    instructions += block

    if else_block:
        jump_to_else.address = else_block[0].line
        jump_to_end = Instruction(Instruction.JUMP,
                                  address_mode=Address.IMMEDIATE)
        jump_to_end.address = next_address(else_block[-1].line)

        instructions.append(jump_to_end)
        instructions += else_block

    return instructions


operator_to_if_compiler = {
    Operator.LT: compile_lt_if,
    Operator.LEQ: compile_leq_if,
    Operator.GT: compile_gt_if,
    Operator.GEQ: compile_geq_if,
    Operator.EQ: compile_eq_if,
    Operator.NEQ: compile_neq_if,
}
