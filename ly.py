#!/usr/bin/python3

# Ly interpreter in Python
# Created by LyricLy
# Commented code is for debugging, uncomment at will.

import sys

args = sys.argv

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

if not args[1:]:
    print("Usage: {} <filename>".format(sys.argv[0]))
else:
    filename = " ".join(args[1:])
    try:
        with open(filename) as file:
            program = file.read()
    except OSError:  # *probably* means that they inputted a Ly program as an argument
        program = filename
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
    stdin = input("Enter program input: ")
    stack = Stack()
    idx = 0
    backup = None
    while idx < len(program):
        char = program[idx]
        # print("-------")
        # print(char)
        # print(stack)
        # print(backup)
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
                split_stdin = stdin.split(" ")
                try:
                    stack.add_value(int(split_stdin[0]))
                    stdin = " ".join(split_stdin[1:])
                except ValueError:
                    raise InputError("program expected integer input, got string instead")
                    
            elif char == "o":
                print(chr(stack.pop_value()), end="")
            elif char == "u":
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
            idx += 1
            # input()
        except LyError as err:
            print("Error occurred at program index {} (zero-indexed, includes comments)".format(idx))
            print(type(err).__name__ + ": " + str(err))
            break
# print("\nStack: " + " ".join([str(x) for x in stack]))
