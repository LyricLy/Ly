#!/usr/bin/python3

# Ly interpreter in Python
# Created by LyricLy
# Commented code is for debugging, uncomment at will.

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="File to interpret.")
parser.add_argument("-d", "--debug", help="Output additional debug information.", action="store_true")
parser.add_argument("-s", "--slow", help="Go through the program step-by-step.", action="store_true")
parser.add_argument("-i", "--input", help="Input for the program. If not given, you will be prompted if the program requires input.")
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

    
class Stack(list):

    def get_value(self):
        if self:
            return self[-1]
        else:
            return False
     
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
if args.input:
    stdin = args.input
elif "n" in program or "i" in program:
    stdin = input("Enter program input: ")
stacks = [Stack()]
stack = stacks[0]
stack_pointer = 0
idx = 0
backup = None
if args.debug:
    total_output = ""
while idx < len(program):
    char = program[idx]
    try:
        if char.isdigit():
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
            if args.debug:
                output = chr(stack.pop_value())
                print("outputted: " + output)
                total_output += output
            else:
                print(chr(stack.pop_value()), end="")
        elif char == "u":
            if args.debug:
                output = stack.pop_value()
                print("outputted: " + str(output))
                total_output += output
            else:
                print(stack.pop_value(), end="")
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
            if backup:
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
        idx += 1
        if args.debug:
            if args.slow:
                print(" | ".join([char, str(stacks), str(backup)]), end="")
                input()
            else:
                print(" | ".join([char, str(stacks), str(backup)]))
    except (LyError, ZeroDivisionError) as err:
        print("Error occurred at program index {} (zero-indexed, includes comments)".format(idx))
        print(type(err).__name__ + ": " + str(err))
        break
# print("\nStacks: " + " | ".join([" ".join([str(x) for x in y]) for y in stacks]))
if args.debug:
    print("\nTotal output: " + total_output)
