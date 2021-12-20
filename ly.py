#!/usr/bin/env python3

# Ly interpreter in Python
# Created by LyricLy
# Commented code is for debugging, uncomment at will.

# pylint: disable=invalid-name,missing-function-docstring,line-too-long,missing-class-docstring,unidiomatic-typecheck
# pylint: disable=too-many-statements,missing-module-docstring,too-many-branches,global-statement,unsubscriptable-object
# pylint: disable=self-cls-assignment,bad-continuation,used-before-assignment,too-many-locals,no-else-return,unused-variable
# pylint: disable=no-self-use,redefined-outer-name
#
# available lower case: gjx
# available upper case: CFPU
# available both cases: HhKkMmTtVvZz
# available symbols...: .@\|

import argparse
import time
import random
import sys
import re

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


try:
    with open(args.filename) as file:
        program = file.read()
except FileNotFoundError:
    print("That file couldn't be found.")
    sys.exit(1)

# remove comments and strings
uncommented_program = re.sub(re.compile(
    '"(?:\\\\.|[^"\\\\])*"', re.DOTALL | re.MULTILINE), "", program)

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
    sys.exit(1)

main_program_body = re.sub(re.compile(
    '.{(.*)}', re.DOTALL), "", uncommented_program)


def interpret(program, input_function, output_function, *, debug=False, delay=0, step_by_step=False):

    class Stack(list):
        nonlocal debug

        def get_value(self):
            if self:
                return self[-1]
            else:
                return None

        def pop_value(self, count=1, implicit=True):
            nonlocal debug

            results = []

            for _ in range(count):
                try:
                    results.append(self.pop())
                except IndexError:
                    if implicit:
                        try:
                            stdin = input_function()
                        except EOFError:
                            stdin = ""
                        if stdin:
                            try:
                                result = int(stdin)
                                if debug:
                                    print("stack empty, using implicit input")
                                results.insert(0, result)
                            except ValueError:
                                raise EmptyStackError("cannot pop from an empty stack, input invalid")
                        else:
                            if debug:
                                print("stack and input empty, using implicit zero")
                            results.append(0)
                    else:
                        raise EmptyStackError("cannot pop from an empty stack")

            return results[0] if len(results) <= 1 else results

        def add_value(self, value):
            if type(value) == list:
                self += value
            else:
                self.append(value)

        def reset_value(self, value):
            while stack:
                stack.pop()
            if type(value) == list:
                for v in value:
                    self.append(v)
            else:
                self.append(value)

    def take_input():
        nonlocal input_function

        try:
            stdin = input_function()
        except EOFError:
            stdin = ""

        return stdin

    def dump_input():
        nonlocal take_input

        stdin = take_input()

        while stdin:
            try:
                stack.add_value(int(stdin))
            except ValueError:
                raise InputError(
                    "program expected integer input, got string instead")
            stdin = take_input()

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
            nxt = program[idx + 1]
        except IndexError:
            nxt = None
        try:
            last = program[idx - 1]
        except IndexError:
            last = None
        if delay:
            time.sleep(delay)
        if debug:
            print(" | ".join([char, str(stacks), str(backup), output_function.__name__, str(idx - 1), str(stack_pointer)]), end=(
                "\n" if not step_by_step else ""))
        try:
            if char in functions:
                def function_input():
                    nonlocal stack

                    return str(stack.pop_value()) if stack else 0

                def function_execution(value):
                    nonlocal stack

                    for val in value.splitlines():
                        if type(val) == int:
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
                    return False
            elif nxt == "{":
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
                try:
                    stdin = input_function()
                    for char in stdin:
                        stack.add_value(ord(char))
                except EOFError:
                    stack.add_value(0)
            elif char == "n":
                if last == "&":
                    dump_input()
                else:
                    try:
                        stack.add_value(int(take_input()))
                    except ValueError:
                        raise InputError(
                            "program expected integer input, got string instead")
            elif char == "o":
                if last == "&":
                    if not stack:
                        for char in take_input():
                            stack.add_value(ord(char))
                    for val in stack[:]:
                        output_function(chr(val))
                        stack.pop_value(implicit=False)
                else:
                    output_function(chr(stack.pop_value(implicit=False)))
            elif char == "u":
                if last == "&":
                    if not stack:
                        dump_input()
                    output_function("\n".join([str(x) for x in stack[:]]))
                    for _ in stack[:]:
                        stack.pop_value(implicit=False)
                else:
                    output_function(stack.pop_value(implicit=False))
            elif char == "r":
                if not stack:
                    dump_input()
                stack.reverse()
            elif char == "+":
                if last == "&":
                    if not stack:
                        dump_input()
                    result = sum(stack)
                    for _ in stack[:]:
                        stack.pop_value(implicit=False)
                    stack.add_value(result)
                else:
                    x, y = stack.pop_value(2)
                    stack.add_value(y + x)
            elif char == "-":
                x, y = stack.pop_value(2)
                stack.add_value(y - x)
            elif char == "*":
                x, y = stack.pop_value(2)
                stack.add_value(y * x)
            elif char == "/":
                x, y = stack.pop_value(2)
                stack.add_value(y / x)
            elif char == "_":
                x, y = stack.pop_value(2)
                stack.add_value(int(y / x))
            elif char == "%":
                x = stack.pop_value()
                y = stack.pop_value()
                stack.add_value(y % x)
            elif char == "A":
                x, y = stack.pop_value(2)
                stack.add_value(int(y & x))
            elif char == "O":
                x, y = stack.pop_value(2)
                stack.add_value(int(y | x))
            elif char == "X":
                x, y = stack.pop_value(2)
                stack.add_value(int(y ^ x))
            elif char == "^":
                x, y = stack.pop_value(2)
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
                    return True
            elif char == ";":
                return True
            elif char == ":":
                if last == "&":
                    if not stack:
                        dump_input()
                    for val in stack[:]:
                        stack.add_value(val)
                else:
                    val = stack.get_value()
                    if val is not None:
                        stack.add_value(val)
            elif char == "p":
                if last == "&":
                    for _ in stack[:]:
                        stack.pop_value(implicit=False)
                else:
                    stack.pop_value(implicit=False)
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
                    if not stack:
                        dump_input()
                    backup = stack[:]
                else:
                    backup = stack.get_value()
            elif char == "f":
                x = stack.pop_value()
                y = stack.pop_value()
                stack.add_value(x)
                stack.add_value(y)
            elif char == "B":
                v = stack.get_value()
                if v is not None:
                    if stack_pointer > 0:
                        p = stack_pointer
                        stack_pointer -= 1
                    else:
                        # since this changes the indexing we don't need to decrement the pointer
                        p = 1
                        stacks.insert(0, Stack())
                    stack = stacks[stack_pointer]
                    stack.add_value(v)
                    stack = stacks[p]
                    stack_pointer = p
            elif char == "b":
                v = stack[0]
                if v is not None:
                    if stack_pointer > 0:
                        p = stack_pointer
                        stack_pointer -= 1
                    else:
                        # since this changes the indexing we don't need to decrement the pointer
                        p = 1
                        stacks.insert(0, Stack())
                    stack = stacks[stack_pointer]
                    stack.add_value(v)
                    stack = stacks[p]
                    stack_pointer = p
            elif char == "<":
                if stack_pointer > 0:
                    stack_pointer -= 1
                else:
                    # since this changes the indexing we don't need to decrement the pointer
                    stacks.insert(0, Stack())
                stack = stacks[stack_pointer]
            elif char == "E":
                v = stack.get_value()
                if v is not None:
                    p = stack_pointer
                    try:
                        stacks[stack_pointer + 1]
                    except IndexError:
                        stacks.append(Stack())
                    stack_pointer += 1
                    stack = stacks[stack_pointer]
                    stack.add_value(v)
                    stack = stacks[p]
                    stack_pointer = p
            elif char == "e":
                v = stack[0]
                if v is not None:
                    p = stack_pointer
                    try:
                        stacks[stack_pointer + 1]
                    except IndexError:
                        stacks.append(Stack())
                    stack_pointer += 1
                    stack = stacks[stack_pointer]
                    stack.add_value(v)
                    stack = stacks[p]
                    stack_pointer = p
            elif char == ">":
                try:
                    stacks[stack_pointer + 1]
                except IndexError:
                    stacks.append(Stack())
                stack_pointer += 1
                stack = stacks[stack_pointer]
            elif char == "$":
                for _ in range(stack.pop_value(implicit=False)):
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
                x, y = stack.pop_value(2)
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
                if "i" in function_body:
                    raise FunctionError("functions cannot contain the 'i' instruction")
                functions[function_name] = function_body
            elif char == "=":
                if stack.pop_value(implicit=False) == stack.get_value():
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
                except ValueError:
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
                if not stack:
                    dump_input()
                try:
                    x = int("".join([str(x) for x in stack]))
                    for _ in stack[:]:
                        stack.pop_value()
                    stack.add_value(x)
                except TypeError:
                    raise EmptyStackError("cannot join an empty stack")
            elif char == "a":
                if not stack:
                    dump_input()
                stack.sort()
            elif char == "N":
                stack.add_value(-stack.pop_value())
            elif char == "Y":
                w = stack.pop_value(implicit=False)
                v = stack[w]
                if w:
                    n = stack[:w] + stack[w+1:]
                else:
                    n = stack[1:]
                stack.reset_value(n+[v,])
                #stack = stacks[stack_pointer]
            elif char == "I":
                stack.add_value(stack[stack.pop_value(implicit=False)])
            elif char == "R":
                x = stack.pop_value()
                y = stack.pop_value()
                for i in range(y, x + 1):
                    stack.add_value(i)
            elif char == "'":
                stack.add_value(ord(nxt))
                idx += 1
            elif char == "w":
                time.sleep(stack.pop_value())
            elif char == "W":
                x = stack.pop_value(implicit=False)
                y = stack.pop_value(implicit=False)
                stack[y], stack[x] = stack[x], stack[y]
            elif char == "`":
                stack.add_value(stack.pop_value() + 1)
            elif char == ",":
                stack.add_value(stack.pop_value() - 1)
            elif char == "~":
                stack.add_value(int(stack.pop_value(implicit=False) in stack))
            elif char == "q":
                r = stack.pop_value()
                l = len(stack)
                s = r % l
                if s:
                    n = stack[s:] + stack[:s]
                    stack.reset_value(n)
            elif char == "Q":
                r = stack.pop_value()
                l = len(stack)
                s = r % l
                if s:
                    n = stack[-s:] + stack[:-s]
                    stack.reset_value(n)
        except errors as err:
            if output_function.__name__ == "function_execution":
                raise FunctionError("{}: {}$${}$${}".format(
                    type(err).__name__, str(err), str(idx), char))
            print("Error occurred at program index {}, instruction {} (zero-indexed, includes comments)".format(idx, char), file=sys.stderr)
            print(type(err).__name__, str(err), sep=": ", file=sys.stderr)
            return False
        idx += 1
        if step_by_step:
            input()

    if debug:
        print("outputting implicitly")
    if output_function.__name__ == "function_execution":
        for val in stack:
            output_function(val)
    else:
        output_function(" ".join([str(x) for x in stack]))
    return True


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
result = interpret(program, input if not args.no_input else lambda: "", normal_execution, debug=args.debug,
          delay=args.time, step_by_step=args.slow)
end = time.time()
if args.timeit:
    print("\nTotal execution time in seconds: " + str(end - start))
if args.debug:
    print("\nTotal output: " + total_output)

sys.exit(int(not result))
