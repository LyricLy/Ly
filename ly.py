#!/usr/bin/python3

# Ly interpreter in Python
# Created by LyricLy
# Commented code is for debugging, uncomment at will.

import argparse
import time
import random
import sys
import re

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="File to interpret.")
parser.add_argument("-d", "--debug", help="Output additional debug information.", action="store_true")
parser.add_argument("-s", "--slow", help="Go through the program step-by-step.", action="store_true")
parser.add_argument("-i", "--input", help="Input for the program. If not given, you will be prompted if the program requires input.")
parser.add_argument("-t", "--time", help="Time to wait between each execution tick.", type=float)
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
# make sure brackets match
count = 0
for i in program:
    if i == "[":
        count += 1
    elif i == "]":
        count -= 1
    if count < 0:
        print("Error occurred during parsing")
        print("SyntaxError: unmatched brackets in program")
        sys.exit(0)
if count != 0:
    print("Error occurred during parsing")
    print("SyntaxError: unmatched brackets in program")
    sys.exit(0)

function_text = "".join(re.findall("{(.*?)}", program))
input_count = (program.count("n") - function_text.count("n")) + (program.count("i") - function_text.count("i"))
if args.input:
    stdin = args.input
elif input_count > 0:
    stdin = input("Enter program input: ")
else:
    stdin = None
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
            next = program[idx+1]
        except IndexError:
            next = None
        try:
            last = program[idx-1]
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
                    for pos, char in enumerate(program[idx+1:]):
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
                    stack.add_value(ord(stdin[0]))
                    # print("consumed input " + stdin[0])
                except IndexError:
                    stack.add_value(0)
                stdin = stdin[1:]
            elif char == "n":
                if stdin:
                    split_stdin = stdin.split(" ")
                    try:
                        stack.add_value(int(split_stdin[0]))
                        stdin = " ".join(split_stdin[1:])
                    except ValueError:
                        raise InputError("program expected integer input, got string instead")
                else:
                    stack.add_value(0)       
            elif char == "o":
                output_function(chr(stack.pop_value()))
            elif char == "u":
                output_function(stack.pop_value())
            elif char == "r":
                stack.reverse()
            elif char == "+":
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
            elif char == '"':
                for pos, char in enumerate(program[idx+1:]):
                    # print("Char: " + char)
                    if char == '"':
                        # print("Position: " + str(pos))
                        idx += pos + 1
                        break
                    else:
                        stack.add_value(ord(char))
            elif char == "#":
                for pos, char in enumerate(program[idx+1:]):
                    # print("Char: " + char)
                    if char == '\n':
                        # print("Position: " + str(pos))
                        idx += pos + 1
                        break
                else:  # we didn't break, thus we've reached EOF 
                    break
            elif char == ";":
                break
            elif char == ":":
                stack.add_value(stack.get_value())
            elif char == "p":
                stack.pop_value()
            elif char == "!":
                if stack.pop_value() == 0:
                    stack.add_value(1)
                else:
                    stack.add_value(0)
            elif char == "l":
                if backup != None:
                    stack.add_value(backup)
                else:
                    raise BackupCellError("attempted to load backup, but backup is empty")
            elif char == "s":
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
                    stacks.insert(0, Stack())  # since this changes the indexing we don't need to decrement the pointer
                stack = stacks[stack_pointer]
            elif char == ">":
                try:
                    stacks[stack_pointer+1]
                except IndexError:
                    stacks.append(Stack())
                stack_pointer += 1
                stack = stacks[stack_pointer]   
            elif char == "$":
                for _ in range(stack.pop_value()):
                    extra = 0
                    for pos, char in enumerate(program[idx+1:]):
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
                for pos, char in enumerate(program[idx+1:]):
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
                        interpret(functions[function_name], function_input, function_execution, debug=debug, delay=delay, step_by_step=step_by_step)
                    except FunctionError as err:
                        err_info = str(err).split("$$")
                        print("Error occurred in function {}, index {} (zero-indexed, includes comments)".format(function_name, err_info[1]))
                        print(err_info[0])
                        return
                else:
                    functions[function_name] = function_body
        except (LyError, ZeroDivisionError) as err:
            if output_function.__name__ == "function_execution":
                raise FunctionError(type(err).__name__  + ": " + str(err) + "$$" + str(idx))
            print("Error occurred at program index {} (zero-indexed, includes comments)".format(idx), file=sys.stderr)
            print(type(err).__name__, str(err), sep=": ")
            return
        idx += 1
        if debug:
            print(" | ".join([char, str(stacks), str(backup), output_function.__name__]), end=("\n" if not step_by_step else ""))
        if step_by_step:
            input()
if not args.debug:
    def normal_execution(val):
        print(str(val), end="")
else:
    total_output = ""
    def normal_execution(val):
        global total_output
        print("outputted: " + str(val))
        total_output += str(val)
interpret(program, stdin, normal_execution, debug=args.debug, delay=args.time, step_by_step=args.slow)
if args.debug:
    print("Total output: " + total_output)