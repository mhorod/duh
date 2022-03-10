"""main file of duh compiler"""
import sys

from duh.lang import Source
from duh.lexer import lex
from duh.parser import parse_tokens
from duh.compiler.compile import compile_program
from duh.compiler.core import SimpleCompiler
from duh.pmc import Machine


def compile_source(source):
    """Compile text into instruction"""
    tokens = lex(source)
    program_node = parse_tokens(tokens)
    instructions = compile_program(program_node, SimpleCompiler)
    return instructions


def run_program(instructions, input_memory={}, output_memory=[]):
    """Run instructions on PMC machine"""
    machine = Machine()
    for index, value in input_memory.items():
        machine.memory[index] = value
    machine.run(instructions)
    for index in output_memory:
        print(machine.memory[index])


def compile_file(source_name, target_name):
    """Compile `source_name` file and save as `target_name` file"""
    with open(source_name, "r", encoding="utf-8") as source_file:
        source = Source(source_name, source_file.read())
        instructions = compile_source(source)
    compiled_code = str(instructions)
    with open(target_name, "w", encoding="utf-8") as target_file:
        target_file.write(compiled_code)


def run_file(source_name):
    """Compiles file and runs it with extension check"""
    extension = source_name.split('.')[-1]
    if extension == "duh":
        run_duh_file(source_name)
    else:
        print("Unknown file type")

def run_duh_file(source_name):
    """Executes file in duh language"""
    with open(source_name, "r", encoding="utf-8") as source_file:
        source = Source(source_name, source_file.read())
        instructions = compile_source(source)

    inp, out = [int(i) for i in input().split()]
    input_memory = {}
    for _ in range(inp):
        index, value = [int(i) for i in input().split(':')]
        input_memory[index] = value

    output_memory = []
    for _ in range(out):
        output_memory.append(int(input()))

    run_program(instructions, input_memory, output_memory)


def print_usage_info():
    print("Usage:")
    print("python3 main.py {filename} {mode}")
    print("Where mode is either --compile or --run")

if __name__ == '__main__':
    if len(sys.argv) == 3:
        source_file_name = sys.argv[1]
        mode = sys.argv[2]
        if mode == '--compile':
            name, _ = source_file_name.split('.')
            target_file_name = name + '.pmc'
            compile_file(source_file_name, target_file_name)
        elif mode == '--run':
            run_file(source_file_name)
        else:
            print(f"Unknown mode `{mode}`")
            print_usage_info()
    else:
        print("Invalid number of arguments")
        print_usage_info()
