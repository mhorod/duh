'''
Core of the duh compiler. 
Contains basic data structures used in compilation
'''

from duh.ast import *
from duh.pmc import *
from duh.lang import *

# Type annotations
import collections


class DependentAddress(Address):
    def __init__(self, address, transform):
        self.address = address
        self.transform = transform
        self.immediate = False

    @property
    def value(self):
        return self.transform(self.address.value)

    def __str__(self):
        return f"{self.value}"


def next_address(address):
    return DependentAddress(address, lambda x: x + 1)


class TVS:
    ''' Temporary Variable Stack 
    Keeps track of temporary variables used for evaluating expressions
    '''
    def __init__(self, var_to_address):
        self.var_to_address = var_to_address
        self.variables = []
        self.active = 0

    def push(self):
        if len(self.variables) == self.active:
            self.create_new_variable()
        address = self.var_to_address[self.variables[self.active]]
        self.active += 1
        return address

    def pop(self, address):
        if address in self.variables:
            self.active -= 1

    def create_new_variable(self):
        name = f"$tmp{self.active}"
        self.variables.append(name)
        self.var_to_address[name] = Address()


class Variables:
    '''Keeps track of all variables'''
    def __init__(self, var_to_address):
        self.var_to_address = var_to_address
        self.tvs = TVS(self.var_to_address)

    def __getitem__(self, item):
        return self.var_to_address[item]


class CompiledInstructions:
    '''Sequence of instructions in PMC
    May contain additional data created during compialation
    '''
    def __init__(self, instructions=None, data=None):
        if instructions is None:
            instructions = []
        self.instructions = instructions
        self.data = data

    def append(self, instruction: Instruction):
        self.instructions.append(instruction)

    def __iadd__(self, other):
        self.instructions += other.instructions
        return self

    def __add__(self, other):
        return CompiledInstructions(self.instructions + other.instructions)

    def __iter__(self):
        return self.instructions.__iter__()

    def __getitem__(self, index):
        return self.instructions[index]

    def __len__(self):
        return len(self.instructions)

    def __str__(self):
        result = f"{len(self.instructions)}\n"
        for instruction in self.instructions:
            result += str(instruction) + '\n'
        return result


class LoadInstruction(Instruction):
    def __init__(self, address=None, address_mode=Address.DIRECT):
        super().__init__(Instruction.LOAD, address, address_mode)


class LoadLiteralInstruction(LoadInstruction):
    def __init__(self, address):
        super().__init__(address, address_mode=Address.IMMEDIATE)


class CompilationError(Exception):
    pass


class UnsupportedNode(CompilationError):
    def __init__(self, node):
        message = f"{type(node)} is not supported by the compiler."
        super().__init__(message)


class Compiler:
    pass


CompilerFunction = collections.Callable[[ASTNode, Compiler],
                                        CompiledInstructions]


class SimpleCompiler(Compiler):
    """Collection of data used for compiling"""
    def __init__(self, variables: Variables,
                 node_type_to_compiler: dict[type, CompilerFunction]):
        self.variables = variables
        self.node_type_to_compiler = node_type_to_compiler


def variables_from_node(node: ProgramNode) -> Variables:
    '''Maps variables and cells to Address objects and stores in Variables'''
    var_to_address = {}
    for instruction in node.instructions:
        if isinstance(instruction, VarNode):
            var_to_address[instruction.name.content] = Address()
        elif isinstance(instruction, CellNode):
            var_to_address[instruction.name.content] = Address(
                int(instruction.address.content))

    return Variables(var_to_address)


def identifier_address(node: ASTNode, compiler: Compiler):
    '''Returns address of an identifier'''
    return compiler.variables[node.identifier.content]


def literal_address(node: ASTNode):
    '''Returns address representing a literal'''
    return Address(node.literal.value, Address.IMMEDIATE)


def assign_addresses(instructions: CompiledInstructions, variables: Variables):
    '''Assign an address to each instruction and variable'''
    for i, instr in enumerate(instructions):
        instr.line.value = i
    index = 0
    for i, var in enumerate(variables.var_to_address):
        if variables[var].value is None:
            variables[var].value = index + len(instructions)
            index += 1


def compile_node(node: ASTNode, compiler: Compiler) -> CompiledInstructions:
    if type(node) in compiler.node_type_to_compiler:
        return compiler.node_type_to_compiler[type(node)](node, compiler)
    else:
        raise UnsupportedNode(node)


def operator_to_instruction_code(op):
    '''Represents instruction code for Operator object'''
    op_map = {
        Operator.ADD: Instruction.ADD,
        Operator.SUB: Instruction.SUB,
        Operator.SHL: Instruction.SHL,
        Operator.SHR: Instruction.SHR,
        Operator.AND: Instruction.AND,
        Operator.OR: Instruction.OR,
        Operator.XOR: Instruction.XOR,
        Operator.NOT: Instruction.NOT,
    }

    return op_map[op.code] if op.code in op_map else None
