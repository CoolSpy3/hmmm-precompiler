import argparse
import re

import processors


def main():
    # Parse arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('-l', '--label', action='store_true', help='Replace labels with line numbers')
    parser.add_argument('-i', '--alias', action='store_true', help='Enable instruction aliases')
    parser.add_argument('-c', '--call-ret-instr', action='store_true', help='Enable call and ret instructions')
    parser.add_argument('-t', '--arg-types', action='store_true', help='Enable argument typing')
    parser.add_argument('-p', '--push-pop', action='store_true', help='Enable push and pop instructions')
    parser.add_argument('-f', '--format', action='store_true', help='Enable formatting')
    parser.add_argument('-n', '--line-numbers', action='store_true', help='Enable automatic line numbering')
    parser.add_argument('-a', '--all', action='store_true', help='Enable all features')

    parser.add_argument('infile', help='hmm file to read')
    parser.add_argument('outfile', help='hmm file to write')
    args = parser.parse_args()

    active_processors = []

    if args.label or args.all:
        active_processors.append(processors.label_processor)
    if args.alias or args.all:
        active_processors.append(processors.aliasing(processors.simple_aliases))
    if args.call_ret_instr or args.all:
        active_processors.append(processors.aliasing(processors.call_ret_aliases))
    if args.arg_types or args.all:
        active_processors.append(processors.arg_type_processor)
    if args.push_pop or args.all:
        active_processors.append(processors.push_pop_processor)
    if args.format or args.all:
        active_processors.append(processors.formatting_processor)
    # The line number preprocessor must be last
    if args.line_numbers or args.all:
        active_processors.append(processors.line_number_processor)

    active_switches = []
    if args.all:
        active_switches.append("all")
    else:
        if args.label:
            active_switches.append("label")
        if args.alias:
            active_switches.append("alias")
        if args.call_ret_instr:
            active_switches.append("call_ret_instr")
        if args.arg_types:
            active_switches.append("arg_types")
        if args.push_pop:
            active_switches.append("push_pop")
        if args.format:
            active_switches.append("format")
        if args.line_numbers:
            active_switches.append("line_numbers")

        if len(active_switches) == 7:
            active_switches = ["all"]

    # Read file
    with open(args.infile, 'r') as f:
        lines = f.readlines()

    # Add a comment at the top of the file indicating which features were enabled
    lines.insert(0, f'# Precompiled by CoolSpy3/hmmm-preprocessor with features: {", ".join(active_switches)}\n')

    # If the line number processor is not enabled, we need to remove the line numbers
    # (Many of the other processors rely on this)
    line_numbers = []
    if not args.line_numbers and not args.all:
        new_lines = []
        for line in lines:
            if match := re.match(r'^(\s*\d+\s)(.*)$', line):
                line_numbers.append(match.group(1))
                new_lines.append(match.group(2))
            else:
                line_numbers.append('')
                new_lines.append(line)

        lines = new_lines

    # Run processors
    for processor in active_processors:
        lines = processor(lines)

    # Add the line numbers back in
    if not args.line_numbers and not args.all:
        for line_num, line in enumerate(lines.copy()):
            lines[line_num] = line_numbers[line_num] + line

    # Make sure all the line numbers are the same length
    if args.format or args.all:
        line_num_pattern = re.compile(r'^(\s*)(\d+)(\s+)(.*)$')
        max_line_num_length = max(len(match.group(2)) for line in lines if (match := line_num_pattern.match(line)))
        lines = [line_num_pattern.sub(lambda match: match.group(1) + match.group(2).ljust(max_line_num_length) + match.group(3) + match.group(4), line) for line in lines]

    # Ensure that all lines end with a newline
    lines = [line + '\n' if not line.endswith('\n') else line for line in lines]

    # Write file
    with open(args.outfile, 'w') as f:
        f.writelines(lines)


if __name__ == '__main__':
    main()
