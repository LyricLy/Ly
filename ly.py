#!/usr/bin/python3

# Ly interpreter in Python
# Created by LyricLy
# Commented code is for debugging, uncomment at will.

import argparse
import time
import random
import sys
import re
import time
from classes import *

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="File to interpret.")
parser.add_argument(
    "-d", "--debug", help="Output additional debug information.", action="store_true")
parser.add_argument(
    "-s", "--slow", help="Go through the program step-by-step.", action="store_true")
parser.add_argument(
    "-i", "--input", help="Input for the program. If not given, you will be prompted if the program requires input.")
parser.add_argument(
    "-t", "--time", help="Time to wait between each execution tick.", type=float)
parser.add_argument(
    "-ti", "--timeit", help="Time the program and output how long it took to finish execution.", action="store_true")
parser.add_argument("-ni", "--no-input",
                    help="Don't prompt for input, no matter what.", action="store_true")
args = parser.parse_args()


try:
    with open(args.filename) as file:
        program = file.read()
except FileNotFoundError:
    print("That file couldn't be found.")
    sys.exit(0)

# remove comments and strings
uncommented_program = re.sub(re.compile(
    '^([^#\n]*?)"(?:\\\\.|[^"\\\\])*"', re.DOTALL | re.MULTILINE), "", program)
    
uncommented_program = re.sub(re.compile("#(.*)"), "", uncommented_program)

# check for matching brackets

def match_brackets(code):
    start_chars = "({["
    end_chars = ")}]"
    stack = []
    for idx, char in enumerate(code):
        if char in start_chars:
            stack.append(char)
        elif char in end_chars:
            if not stack:
                return False
            stack_top = stack.pop()
            balancing_bracket = start_chars[end_chars.index(char)]
            if stack_top != balancing_bracket:
                return False
    return not stack


if not match_brackets(uncommented_program):
    print("Error occurred during parsing", file=sys.stderr)
    print("SyntaxError: Unmatched brackets in program", file=sys.stderr)
    sys.exit(0)

main_program_body = re.sub(re.compile(
    '.{(.*)}', re.DOTALL), "", uncommented_program)

if args.input:
    stdin = args.input
elif args.no_input:
    stdin = False
else:
    stdin = None

instructions = {}
    
def interpret(program, stdin, output_function, *, debug=False, delay=0, step_by_step=False):
    stacks = [Stack()]
    stack = stacks[0]
    stack_pointer = 0
    idx = 0
    backup = None
    functions = {}
    errors = (LyError, ZeroDivisionError, IndexError)
    while idx < len(program):
        char = program[idx]
        try:
            next = program[idx + 1]
        except IndexError:
            next = None
        try:
            last = program[idx - 1]
        except IndexError:
            last = None
        if delay:
            time.sleep(delay)
        try:
            if next == "{":
                pass
            elif char.isdigit():
                stack.add_value(int(char))
            elif char == "[":
                if not stack.get_value():
                    extra = 0
                    for pos, char in enumerate(program[idx + 1:]):
                        if char == "[":
                            extra += 1
                        elif char == "]":
                            if extra:
                                extra -= 1
                            else:
                                idx += pos
                                break
            elif char == "]":
                if not stack.get_value():
                    pass
                else:
                    extra = 0
                    for pos, char in reversed(list(enumerate(program[:idx]))):
                        if char == "]":
                            extra += 1
                        elif char == "[":
                            if extra:
                                extra -= 1
                            else:
                                idx = pos
                                break
            elif char == "i":
                if stdin is None:
                    stdin = input()
                if last == "&":
                    for val in stdin[:]:
                        stack.add_value(ord(val))
                    stdin = ""
                else:
                    try:
                        stack.add_value(ord(stdin[0]))
                        # print("consumed input " + stdin[0])
                    except IndexError:
                        stack.add_value(0)
                    stdin = stdin[1:]
            elif char == "n":
                if stdin is None:
                    stdin = input()
                if last == "&":
                    if stdin:
                        split_stdin = stdin.split(" ")
                        split_stdin = list(filter(bool, split_stdin))
                        for val in split_stdin[:]:
                            try:
                                stack.add_value(int(val))
                            except ValueError:
                                raise InputError(
                                    "program expected integer input, got string instead")
                        stdin = ""
                    else:
                        pass
    else:
        if stdin:
            split_stdin = stdin.split(" ")
            split_stdin = list(filter(bool, split_stdin))
            try:
                stack.add_value(int(split_stdin[0]))
                stdin = " ".join(split_stdin[1:])
            except ValueError:
                raise InputError(
                    "program expected integer input, got string instead")
        else:
            stack.add_value(0)
            else:
                args = []
                instruction = instructions[char]
                for arg in range(instruction[1]):
                    try:
                        args.append(stack.pop_value())
                    except EmptyStackError:
                        if not instructions[3]:
                            raise
                if instruction[2]:
                    args.append(last == instruction[2])
                for val in instruction[0](*args):
                    stack.add_value(val)
        except errors as err:
            if output_function.__name__ == "function_execution":
                raise FunctionError("{}: {}$${}$${}".format(
                    type(err).__name__, str(err), str(idx), char))
            print("Error occurred at program index {}, instruction {} (zero-indexed, includes comments)".format(idx, char), file=sys.stderr)
            print(type(err).__name__, str(err), sep=": ", file=sys.stderr)
            return
        idx += 1
        if debug:
            print(" | ".join([char, str(stacks), str(backup), output_function.__name__]), end=(
                "\n" if not step_by_step else ""))
        if step_by_step:
            input()
    
    if debug:
        print("outputting implicitly")
    output_function(" ".join([str(x) for x in stack]))


if not args.debug:
    def normal_execution(val):
        print(str(val), end="", flush=True)
else:
    total_output = ""

    def normal_execution(val):
        global total_output
        print("outputted: " + str(val))
        total_output += str(val)
     
if __name__ == "__main__":     
    start = time.time()
    interpret(program, stdin, normal_execution, debug=args.debug,
              delay=args.time, step_by_step=args.slow)
    end = time.time()
    if args.timeit:
        print("\nTotal execution time in seconds: " + str(end - start))
    if args.debug:
        print("\nTotal output: " + total_output)
