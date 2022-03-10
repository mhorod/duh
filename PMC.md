# Syntax for PMC language

## Architecture
PMC is 16-bit and stores data in memory of 512 16-bit blocks

Instructions are stored in following format:
| bits   | 15     | 14 - 11  | 10 - 9       | 8 - 0   | 
| ----:  | :----: | :------: | :----------: | :-----: |
| store  | sign   | opcode   | address mode | address |



PMC has four registers:
- `IR` - Instruction Register
- `PC` - Program Counter - address of next instruction
- `AC` - Accumulator for arithmetic operations
- `OP` - operand

## Execution cycle
```
set all registers to zero
until stopped or error occured:
    IR = memory[PC]
    PC++
    decode OP from IR
    execute current instruction
```

## Program syntax
First line of `PMC` program contains number of following lines.

Each line has two possible formats:
```
{instruction address}: {keyword} {address mode} {address}
```
or
```
{number address}: {number}
```
Line may contain a trailing comment starting with `#`

### Example
```
6
0: LOAD . 2
1: ADD @ 5
2: STORE . 6
3. PRINT @ 6 # print 42
4: STOP . 0
5: 40 # value that we add
```

## Instructions
|  code   | keyword  | action |
| :----:  | :-----:  | :---- |
| `0000`  | `NULL`   | 
| `0001`  | `STOP`   | halt machine
| `0010`  | `LOAD`   | `AC = OP`
| `0011`  | `STORE`  | `memory[OP] = AC`
| `0100`  | `JUMP`   | `PC = OP`
| `0101`  | `JNEG`   | `if (AC < 0) PC = OP`
| `0110`  | `JZERO`  | `if (AC == 0) PC = OP`
| `0111`  | `PRINT`  | output `OP` to stdout
| `1000`  | `ADD`    | `AC += OP`
| `1001`  | `SUB`    | `AC -= OP`
| `1100`  | `AND`    | `AC &= OP`
| `1101`  | `OR`     | `AC \|= OP`
| `1110`  | `NOT`    | `AC = ~AC`
| `1111`  | `XOR`    | `AC ^= OP` 

## Address modes
|  code  | symbol   | name | interpretation |
| :----: | :-----:  | :----: | :--- |
| `00`   | `.`   | immediate | `OP = IR.address`
| `01`   | `@`   | direct    | `OP = memory[IR.address]` 
| `10`   | `*`   | indirect  | `OP = memory[memory[IR.address]]`
| `11`   | `+`   | relative  | `OP = memory[AC + IR.address]`