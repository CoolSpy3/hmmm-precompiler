import re
from typing import Callable

label_pattern = re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*:(?:\s+.*|)$')
one_arg_instruction_pattern = re.compile(r'^(\s*)([^\s]*)(\s+)([^\s]*)(\s+.*|)$')
two_arg_instruction_pattern = re.compile(r'^(\s*)([^\s]*)(\s+)([^\s]*)(\s+)([^\s]*)(\s+.*|)$')


def is_code_line(line: str) -> bool:
    """Checks if the line is a runnable line of HMMM code"""
    return line[:line.find('#')].strip() and not label_pattern.match(line)


def for_each_code_line(lines: list[str], func: Callable[[int, str], str]) -> list[str]:
    """Applies a function to each line of HMMM code"""
    out = []
    line_num = 0
    for line in lines:
        if is_code_line(line):
            out.append(func(line_num, line))
            line_num += 1
        else:
            out.append(line)

    return out


def label_processor(lines: list[str]) -> list[str]:
    """Replaces labels with their line numbers"""
    labels = {}
    line_num = 0

    for line in lines:
        line = line[:line.find('#')].strip()
        if match := label_pattern.match(line):
            # TODO: VALIDATE LABELS
            labels[match.group(1)] = line_num
        elif line:
            line_num += 1

    lines = ["# " + line if label_pattern.match(line) else line for line in lines]

    def process_line(_line_num: int, code_line: str) -> str:
        for label, label_line_num in labels.items():
            code_line = re.sub(label, str(label_line_num), code_line)
        return code_line

    return for_each_code_line(lines, process_line)


def line_number_processor(lines: list[str]) -> list[str]:
    """Adds line numbers to the beginning of each HMMM code line"""
    def process_line(line_num: int, line: str) -> str:
        line = f'{line_num} {line}'
        return line

    return for_each_code_line(lines, process_line)


def alias_processor(lines: list[str], aliases: dict[str, str]) -> list[str]:
    """Replaces aliases with their expansions"""
    aliases = {r'(\s|^)' + alias + r'(\s|$)': replacement for alias, replacement in aliases.items()}

    def process_line(line_num: int, line: str) -> str:
        for alias, replacement in aliases.items():
            line = re.sub(alias, r'\1' + replacement + r'\2', line)
        return line

    return for_each_code_line(lines, process_line)


simple_aliases = {
    "set": "setn",
    "in": "read",
    "out": "write",
    "jeqz": "jeqzn",
    "jnez": "jneqzn",
    "jltz": "jltzn",
    "jgtz": "jgtzn",
    "jz": "jeqzn",
    "jnz": "jneqzn",
    "jl": "jltzn",
    "jg": "jgtzn",
    "jmpn": "jumpn",
    "jmpr": "jumpr",
    "jmp": "jump"
}

call_ret_aliases = {
    "call": "calln r14",
    "ret": "jumpr r14"
}


def aliasing(aliases: dict[str, str]) -> Callable[[list[str]], list[str]]:
    """Creates an aliasing processor with the given aliases"""
    def aliasing_helper(lines: list[str]) -> list[str]:
        return alias_processor(lines, aliases)

    return aliasing_helper


def arg_type_processor(lines: list[str]) -> list[str]:
    """Adds type postfixes to instructions which require them"""
    def process_line(_line_num: int, line: str) -> str:
        if match := two_arg_instruction_pattern.match(line):
            instruction = match.group(2)
            arg = match.group(6)
            if instruction in typed_instructions:
                postfix = "r" if arg.startswith("r") else "n"
                if instruction == "add" and postfix == "r":
                    # add r r r doesn't need a postfix (it's not addr r r r)
                    postfix = ''
                return two_arg_instruction_pattern.sub(r'\1\2' + postfix + r'\3\4\5\6\7', line)

        return line

    return for_each_code_line(lines, process_line)


typed_instructions = [
    "add",
    "jump",
    "store",
    "load"
]


def push_pop_processor(lines: list[str]) -> list[str]:
    """Replaces push and pop instructions with their register equivalents"""
    def process_line(_line_num: int, line: str) -> str:
        if match := one_arg_instruction_pattern.match(line):
            instruction = match.group(2)
            if instruction in ("push", "pop"):
                return one_arg_instruction_pattern.sub(r'\1' + instruction + r'r\3\4 r15\5', line)

        return line

    return for_each_code_line(lines, process_line)


def formatting_processor(lines: list[str]) -> list[str]:
    """Formats the code to be more readable"""
    # Make all instructions the same length
    def normalize_instructions(_line_num: int, line: str) -> str:
        if match := one_arg_instruction_pattern.match(line):
            normalized_instruction = match.group(2).ljust(6)  # 6 is the length of the longest instruction
            return one_arg_instruction_pattern.sub(r'\1' + normalized_instruction + r' \4\5', line)
        else:
            return line

    lines = for_each_code_line(lines, normalize_instructions)

    # Justify comments
    max_line_length = max(len(line[:line.find('#')].rstrip()) for line in lines)

    def justify_comments(line: str) -> str:
        if is_code_line(line) or label_pattern.match(line):
            return (line[:line.find('#')].rstrip().ljust(max_line_length + 1) + line[line.find('#'):]).rstrip()
        return line.lstrip()

    return [justify_comments(line) for line in lines]
