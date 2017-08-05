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

# errors


class LyError(Exception):
    pass


class EmptyStackError(LyError):
    pass


class InputError(LyError):
    pass


class BackupCellError(LyError):
    pass


class FunctionError(LyError):
    pass


class Stack(list):

    def get_value(self):
        if self:
            return self[-1]
        else:
            return None

    def pop_value(self):
        try:
            return self.pop()
        except IndexError:
            raise EmptyStackError("cannot pop from an empty stack")

    def add_value(self, value):
        if type(value) == list:
            self += value
        else:
            self.append(value)


try:
    with open(args.filename) as file:
        program = file.read()
except FileNotFoundError:
    print("That file couldn't be found.")

# remove comments and strings
uncommented_program = re.sub(re.compile("#(.*)"), "", program)
uncommented_program = re.sub(re.compile(
    '"(.*?)"', re.DOTALL), "", uncommented_program)

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
elif ("i" in main_program_body or "n" in main_program_body) and not args.no_input:
    stdin = input("Enter program input: ")
else:
    stdin = ""


def interpret(program, stdin, output_function, *, debug=False, delay=0, step_by_step=False):
    stacks = [Stack()]
    stack = stacks[0]
    stack_pointer = 0
    idx = 0
    backup = None
    functions = {}
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
                        # print("Char: " + char)
                        if char == "[":
                            extra += 1
                        elif char == "]":
                            if extra:
                                extra -= 1
                            else:
                                # print("Position: " + str(pos))
                                idx += pos
                                break
            elif char == "]":
                if not stack.get_value():
                    pass
                else:
                    extra = 0
                    for pos, char in reversed(list(enumerate(program[:idx]))):
                        # print("Char: " + char)
                        if char == "]":
                            extra += 1
                        elif char == "[":
                            if extra:
                                extra -= 1
                            else:
                                # print("Position: " + str(pos))
                                idx = pos
                                break
            elif char == "i":
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
            elif char == "o":
                if last == "&":
                    for val in stack[:]:
                        output_function(chr(val))
                        stack.pop_value()
                else:
                    output_function(chr(stack.pop_value()))
            elif char == "u":
                if last == "&":
                    output_function(" ".join([str(x) for x in stack[:]]))
                    for _ in stack[:]:
                        stack.pop_value()
                else:
                    output_function(stack.pop_value())
            elif char == "r":
                stack.reverse()
            elif char == "+":
                if last == "&":
                    stack.add_value(sum(stack))
                else:
                    x = stack.pop_value()
                    y = stack.pop_value()
                    stack.add_value(y + x)
            elif char == "-":
                x = stack.pop_value()
                y = stack.pop_value()
                stack.add_value(y - x)
            elif char == "*":
                x = stack.pop_value()
                y = stack.pop_value()
                stack.add_value(y * x)
            elif char == "/":
                x = stack.pop_value()
                y = stack.pop_value()
                stack.add_value(y / x)
            elif char == "%":
                x = stack.pop_value()
                y = stack.pop_value()
                stack.add_value(y % x)
            elif char == "^":
                x = stack.pop_value()
                y = stack.pop_value()
                stack.add_value(y ** x)
            elif char == "L":
                x = stack.pop_value()
                stack.add_value(int(stack.get_value() < x))
            elif char == "G":
                x = stack.pop_value()
                stack.add_value(int(stack.get_value() > x))
            elif char == '"':
                for pos, char in enumerate(program[idx + 1:]):
                    # print("Char: " + char)
                    if char == '"':
                        if program[idx + pos] == "\\":
                            stack.add_value(ord(char))
                        else:
                            # print("Position: " + str(pos))
                            idx += pos + 1
                            break
                    elif char == "n":
                        if program[idx + pos] == "\\":
                            stack.add_value(ord('\n'))
                        else:
                            stack.add_value(ord(char))
                    elif char == "\\" and program[idx + pos + 2] in ['"', 'n']:
                        pass
                    else:
                        stack.add_value(ord(char))
            elif char == "#":
                for pos, char in enumerate(program[idx + 1:]):
                    # print("Char: " + char)
                    if char == '\n':
                        # print("Position: " + str(pos))
                        idx += pos + 1
                        break
                else:  # we didn't break, thus we've reached EOF
                    return
            elif char == ";":
                return
            elif char == ":":
                if last == "&":
                    for val in stack[:]:
                        stack.add_value(val)
                else:
                    val = stack.get_value()
                    if val:
                        stack.add_value(val)
            elif char == "p":
                if last == "&":
                    for _ in stack[:]:
                        stack.pop_value()
                else:
                    stack.pop_value()
            elif char == "!":
                if stack.pop_value() == 0:
                    stack.add_value(1)
                else:
                    stack.add_value(0)
            elif char == "l":
                if type(backup) == list:
                    for item in backup[:]:
                        stack.add_value(item)
                elif backup is not None:
                    stack.add_value(backup)
                else:
                    raise BackupCellError(
                        "attempted to load backup, but backup is empty")
            elif char == "s":
                if last == "&":
                    backup = stack[:]
                else:
                    backup = stack.get_value()
            elif char == "f":
                x = stack.pop_value()
                y = stack.pop_value()
                stack.add_value(x)
                stack.add_value(y)
            elif char == "<":
                if stack_pointer > 0:
                    stack_pointer -= 1
                else:
                    # since this changes the indexing we don't need to decrement the pointer
                    stacks.insert(0, Stack())
                stack = stacks[stack_pointer]
            elif char == ">":
                try:
                    stacks[stack_pointer + 1]
                except IndexError:
                    stacks.append(Stack())
                stack_pointer += 1
                stack = stacks[stack_pointer]
            elif char == "$":
                for _ in range(stack.pop_value()):
                    extra = 0
                    for pos, char in enumerate(program[idx + 1:]):
                        # print("Char: " + char)
                        if char == "[":
                            extra += 1
                        elif char == "]":
                            if extra:
                                extra -= 1
                            else:
                                # print("Position: " + str(pos))
                                idx += pos + 1
                                break
            elif char == "?":
                x = stack.pop_value()
                y = stack.pop_value()
                stack.add_value(random.randint(y, x))
            elif char == "{":
                function_name = last
                function_body = ""
                extra = 0
                for pos, char in enumerate(program[idx + 1:]):
                    # print("Char: " + char)
                    if char == "{":
                        extra += 1
                    elif char == "}":
                        if extra:
                            extra -= 1
                        else:
                            # print("Position: " + str(pos))
                            idx += pos
                            break
                    else:
                        function_body += char
                if function_name in functions:
                    function_params = function_body.split(",")
                    function_input = ""
                    for param in function_params:
                        if param.isdigit():
                            function_input += param + " "
                        elif param == "c":
                            function_input += chr(stack.pop_value())
                        elif param == "i":
                            function_input += str(stack.pop_value())

                    def stack_addition(val):
                        global stack
                        stack.add_value(val)

                    def function_execution(val):
                        global stack_addition
                        if type(val) != str:
                            stack.add_value(val)
                        else:
                            stack.add_value(ord(val))
                    try:
                        interpret(functions[function_name], function_input, function_execution,
                                  debug=debug, delay=delay, step_by_step=step_by_step)
                    except FunctionError as err:
                        err_info = str(err).split("$$")
                        print("Error occurred in function {}, index {}, instruction {} (zero-indexed, includes comments)".format(
                            function_name, err_info[1], err_info[2]), file=sys.stderr)
                        print(err_info[0], file=sys.stderr)
                        return
                else:
                    functions[function_name] = function_body
            elif char == "=":
                if stack.pop_value() == stack.get_value():
                    stack.add_value(1)
                else:
                    stack.add_value(0)
            elif char == "(":
                body = ""
                extra = 0
                for pos, char in enumerate(program[idx + 1:]):
                    # print("Char: " + char)
                    if char == "(":
                        extra += 1
                    elif char == ")":
                        if extra:
                            extra -= 1
                        else:
                            # print("Position: " + str(pos))
                            idx += pos
                            break
                    elif char.isdigit():
                        body += char
                try:
                    stack.add_value(int(body))
                except TypeError:
                    pass
            elif char == "y":
                stack.add_value(len(stack))
            elif char == "c":
                stack.add_value(len(str(stack.pop_value())))
            elif char == "S":
                x = str(stack.pop_value())
                for digit in x:
                    stack.add_value(int(digit))
            elif char == "J":
                try:
                    x = int("".join([str(x) for x in stack]))
                    for _ in stack[:]:
                        stack.pop_value()
                    stack.add_value(x)
                except TypeError:
                    raise EmptyStackError("cannot join an empty stack")
            elif char == "a":
                stack.sort()
        except (LyError, ZeroDivisionError) as err:
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


if not args.debug:
    def normal_execution(val):
        print(str(val), end="", flush=True)
else:
    total_output = ""

    def normal_execution(val):
        global total_output
        print("outputted: " + str(val))
        total_output += str(val)
start = time.time()
interpret(program, stdin, normal_execution, debug=args.debug,
          delay=args.time, step_by_step=args.slow)
end = time.time()
if args.timeit:
    print("\nTotal execution time in seconds: " + str(end - start))
if args.debug:
    print("\nTotal output: " + total_output)
