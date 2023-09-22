# HMMM Precompiler
This is a precompiler for the [HMMM assembly language](https://www.cs.hmc.edu/~cs5grad/cs5/hmmm/documentation/documentation.html). It adds a couple of features to the HMMM language which make writing code in it easier.

I wrote this fairly quickly, so there are probably still a few bugs, but it should work for most cases. If you find a bug, please open an issue.

## Features
In order to make this program modular and easy to use. Each feature can be individually toggled on or off using command-line switches. The following features are available

### Labels
Labels allow you to mark certain lines of code and reference them by name rather than by line. A label is defined by a line that ends with a colon. For example
```
label
```
Labels can be referenced by using the label name. For example
```
0 jumpn label
1 halt
label:
2 jumpr r14
```

### Aliases
Aliases alias certain commands to other commands which are shorter or more intuitive. For example, are currently defined

| Alias | Command |
|-------|---------|
| set   | setn    |
| in    | read    |
| out   | write   |
| jeqz  | jeqzn   |
| jnez  | jneqzn  |
| jltz  | jltzn   |
| jgtz  | jgtzn   |
| jz    | jeqzn   |
| jnz   | jneqzn  |
| jl    | jltzn   |
| jg    | jgtzn   |
| jmpn  | jumpn   |
| jmpr  | jumpr   |
| jmp   | jump    |

### Call and Return Instructions
In order to comply with the HMMM calling convention, the precompiler adds the `call` and `ret` instructions. These are aliases for `calln r14` and `jumpr r14` respectively.

The `call` instruction will be rewritten as a call to `calln` with the return address in `r14`. For example
```
call 25
```
expands to
```
calln r14 25
```

The `ret` instruction will be rewritten as a call to `jumpr` with the return address in `r14`. For example
```
ret
```
expands to
```
jumpr r14
```

### Automatic Argument Types
Several instructions in HMMM have different variants for the type of argument they take. For example, `addnn` takes a number as its second argument, while `add` takes a register. The precompiler will automatically determine which variant of the instruction to use based on the type of the argument. For example
```
add r1 r2 r3
add r1 1
jump r12
```
expands to
```
add r1 r2 r3
addn r1 1
jumpr r12
```

### Push and Pop Instructions
In order to comply with the HMMM calling convention, the precompiler adds the `push` and `pop` instructions. These are aliases for `pushr rX r14` and `popr rY r14` respectively. For example
```
push r1
pop r2
```
expands to
```
pushr r1 r14
popr r2 r14
```

### Formatter
The precompiler can also format your code to make it more readable. It will space all instructions out to be 6 characters long and align the arguments of each instruction. For example
```
add r1 r1 r2 # x += y
add r1 1 # x++
```
becomes
```
add    r1 r1 r2 # x += y
add    r1 1     # x++
``` 

### Automatic Line Numbers
The precompiler can also automatically number your lines. This prevents you from having to manually number your lines to conform to the HMMM standard. For example
```
setn r1 1
setn r2 2
# Now we'll set r3
setn r3 3
```
becomes
```
0 setn r1 1
1 setn r2 2
# Now we'll set r3
2 setn r3 3
```

## Usage
The precompiler is run from the command line. It is run through the python interpreter with the command `python hmmpre.py [options] infile outfile`.

The full argument list is as follows:
```
usage: hmmpre.py [-h] [-l] [-i] [-c] [-t] [-p] [-f] [-n] [-a] infile outfile

positional arguments:
  infile                hmm file to read
  outfile               hmm file to write

options:
  -h, --help            show this help message and exit
  -l, --label           Replace labels with line numbers
  -i, --alias           Enable instruction aliases
  -c, --call-ret-instr  Enable call and ret instructions
  -t, --arg-types       Enable argument typing
  -p, --push-pop        Enable push and pop instructions
  -f, --format          Enable formatting
  -n, --line-numbers    Enable automatic line numbering
  -a, --all             Enable all features

```

A sample input and output file are provided in the `test.hmmm` and `testo.hmmm` files respectively.

## Can I use this to complete my homework?
At the moment, this precompiler has not been allowed to be used to complete homework or other assignments. Please ask your professor if you are allowed to use this precompiler.

The precompiler will also add a line to the beginning of every file that states that the file has been precompiled and lists which features were enabled. This allows professors to easily check if you used the precompiler. Editing or removing this line without permission from your professor is a violation of the HMC Honor Code.
