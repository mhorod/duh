# duh
A small programming language created to solve `PMC` tasks on Programming Basics course

`PMC` is a simple assembly-like language that illustrates von Neumann architecture.

`duh` was created as a structural interface that compiles to `PMC`

## TODO
  - tests
  - error handling
  - examples

## usage
### Compilation
```
$ python3 main.py foo.duh --compile
```
This will output `foo.pmc` file 

### Execution
```
$ python3 main.py foo.duh --run
```
This will run the `foo.duh` file using builtin interpreter.
Program expects `stdin` to be of form:
```
{number_of_cells_with_input} {number_of_cells_with_output}
```
Then `number_of_cells_with_input` rows of form:
```
{cell}: {value}
```
Then `number_of_cells_with_output` rows, each containing a single integer
```
{cell}
```

The machine will be initialized with input, and values from output cells will be printed on `stdout`

Example input:
```
1 1
100: 256
101
```



## syntax

### Variables
```
cell n address
```
Defines `n` as an alias to cell with address `address`

```
var x
```
Declares variable `x`

Variables should be declared at the beginning of the file since they aren't initialized in runtime 

### Literals
`duh` operates only on integers.
Literal can be any signed number in base 2, 8, 16, or 10.

Literals in bases other than 10 have to be prefixed appriopriately
```
0b101010
0o52
0x2a
42
```

### Expressions
EBNF definition for expressions
```
simple expression = variable | literal;
complex expression = "(" , operator, expression, {expression} ,")";
expression = simple expression | complex expression | "(", expression, ")";
```
All operators are prefix, and expression containing an operator has to be parenthesised.
```
x
16
(+ 2 2)
```
Unary operators always take a single argument.
```
(~ 42)
```

There's no unary minus

Binary operators can take any number of arguments that is at least two.
The expression is then left-folded using the operator

The following two expressions are equivalent
```
(<< 1 2 3)
(<< (<< 1 2) 3)
```

Arithmetic expressions supported by `duh`:
```
+   - add
-   - subtract
>>  - shift right
<<  - shift left
&   - bitwise and
|   - bitwise or
^   - bitwise xor
~   - bitwise not
++  - increment
--  - decrement
```

There are two special operators:
  - `=` - assignment
  - `@` - (de)reference

```
(= x (+ x 2))
(= x (@ 0))
(= (@ 0) (++ x))
```

### Control flow
`duh` has only two kinds of control flow statements: `if` and `while`

Both of them consist of a condition expression and block or a single instruction

```
if (++ x) { 
  print x
  (= x (++ x))
}

while a (= a (-- a))
if x print x else print y
```

In addition *comparison expressions* can be used in conditions:
```
if (< x 1) {}
while (>= i j) {}
if (== x 2) {}
while (!= i j) {}
```

Comparison operators:
```
<   - less
<=  - less or equal
>   - greater
>=  - greater or equal
==  - equal
!=  - not equal
```
