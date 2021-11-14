class Address:
    IMMEDIATE, DIRECT, INDIRECT, RELATIVE = range(4)
    TO_STR = ['.', '@', '*', '+']

    def __init__(self, value=None, mode=DIRECT):
        self.value = value
        self.mode = mode

    def __str__(self):
        return f"{self.value}"


class Instruction:
    (NULL, STOP, LOAD, STORE, JUMP, JNEG, JZERO, PRINT, ADD, SUB, SHL, SHR,
     AND, OR, NOT, XOR) = range(16)
    TO_STR = [
        "NULL", "STOP", "LOAD", "STORE", "JUMP", "JNEG", "JZERO", "PRINT",
        "ADD", "SUB", "SHL", "SHR", "AND", "OR", "NOT", "XOR"
    ]

    def __init__(self, code, address=None, address_mode=Address.DIRECT):
        self.code = code
        self.line = Address()
        self.address_mode = address_mode
        if address is None:
            address = Address(0)
        self.address = address

    def __str__(self):
        line = self.line.value
        instr = Instruction.TO_STR[self.code]
        addr_mode = self.address_mode
        addr_mode = Address.TO_STR[addr_mode]
        addr = str(self.address)
        return f"{line}: {instr} {addr_mode} {addr}"


class Machine:
    MEMORY_SIZE = 512

    SIGN_BITS = 1
    OP_BITS = 4
    ADDR_MODE_BITS = 2
    ADDR_BITS = 9

    SIGN_MASK = 0x8000
    OP_MASK = 0x7800
    ADDR_MODE_MASK = 0x600
    ADDR_MASK = 0x1ff

    SIGN_OFFSET = 15
    OP_OFFSET = 11
    ADDR_MODE_OFFSET = 9
    ADDR_OFFSET = 0

    def __init__(self):
        self.reset()

    def run(self, instructions):
        for index, instruction in enumerate(instructions):
            self.memory[index] = self.encode(instruction)

        self.running = True
        while self.running:
            self.instruction_register = self.memory[self.instruction_counter]
            self.instruction_counter += 1
            instruction = self.decode(self.instruction_register)
            addr_mode_to_function[instruction.address_mode](
                self, instruction.address.value)

            if not self.running: break
            op_to_function[instruction.code](self)

    def reset(self):
        self.memory = [0] * self.MEMORY_SIZE
        self.instruction_register = 0
        self.arithmetic_register = 0
        self.instruction_counter = 0
        self.operand = 0
        self.running = False

    def encode(self, instruction):
        code = 0
        sign = 0
        addr = instruction.address.value
        if addr < 0:
            sign = 1
            addr = -addr

        code = sign
        code <<= self.OP_BITS
        code += instruction.code
        code <<= self.ADDR_MODE_BITS
        code += instruction.address_mode
        code <<= self.ADDR_BITS
        code += addr

        return code

    def decode(self, code):
        sign = (code & self.SIGN_MASK) >> self.SIGN_OFFSET
        opcode = (code & self.OP_MASK) >> self.OP_OFFSET
        addr_mode = (code & self.ADDR_MODE_MASK) >> self.ADDR_MODE_OFFSET
        addr = (code & self.ADDR_MASK) >> self.ADDR_OFFSET

        if sign: addr = -addr

        return Instruction(opcode, Address(addr), addr_mode)

    def is_addr_valid(self, addr):
        return addr is not None and addr >= 0 and addr < self.MEMORY_SIZE

    def access(self, addr):
        if self.is_addr_valid(addr):
            return self.memory[addr]
        else:
            self.running = False

    def stop(self):
        self.running = False

    def calculate(self, op):
        '''Evaluate function on AC and operand'''
        self.arithmetic_register = op(self.arithmetic_register, self.operand)

    def load(self):
        self.arithmetic_register = self.operand

    def store(self):
        self.access(self.operand)
        self.memory[self.operand] = self.arithmetic_register

    def jump(self, condition):
        if condition(self):
            self.access(self.operand)
            self.instruction_counter = self.operand


def addr_immediate(machine, addr):
    machine.operand = addr


def addr_direct(machine, addr):
    machine.operand = machine.access(addr)


def addr_indirect(machine, addr):
    machine.operand = machine.access(machine.access(addr))


def addr_relative(machine, addr):
    machine.operand = machine.arithmetic_register + addr


addr_mode_to_function = {
    Address.IMMEDIATE: addr_immediate,
    Address.DIRECT: addr_direct,
    Address.INDIRECT: addr_indirect,
    Address.RELATIVE: addr_relative,
}

op_to_function = {
    Instruction.NULL: lambda m: None,
    Instruction.STOP: lambda m: m.stop(),
    Instruction.LOAD: lambda m: m.load(),
    Instruction.STORE: lambda m: m.store(),
    Instruction.JUMP: lambda m: m.jump(lambda _: True),
    Instruction.JNEG: lambda m: m.jump(lambda m: m.arithmetic_register < 0),
    Instruction.JZERO: lambda m: m.jump(lambda m: m.arithmetic_register == 0),
    Instruction.PRINT: lambda m: print(m.operand),
    Instruction.ADD: lambda m: m.calculate(int.__add__),
    Instruction.SUB: lambda m: m.calculate(int.__sub__),
    Instruction.SHL: lambda m: m.calculate(int.__lshift__),
    Instruction.SHR: lambda m: m.calculate(int.__rshift__),
    Instruction.AND: lambda m: m.calculate(int.__and__),
    Instruction.OR: lambda m: m.calculate(int.__or__),
    Instruction.NOT: lambda m: m.calculate(lambda x, _: ~x),
    Instruction.XOR: lambda m: m.calculate(int.__xor__)
}
