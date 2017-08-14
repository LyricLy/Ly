import dec

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
elif char == "o":
    if last == "&":
        for val in stack[:]:
            output_function(chr(val))
            stack.pop_value(implicit=False)
    else:
        output_function(chr(stack.pop_value(implicit=False)))
elif char == "u":
    if last == "&":
        output_function(" ".join([str(x) for x in stack[:]]))
        for _ in stack[:]:
            stack.pop_value(implicit=False)
    else:
        output_function(stack.pop_value(implicit=False))
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

        def function_execution(val):
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
    try:
        x = int("".join([str(x) for x in stack]))
        for _ in stack[:]:
            stack.pop_value()
        stack.add_value(x)
    except TypeError:
        raise EmptyStackError("cannot join an empty stack")
elif char == "a":
    stack.sort()
elif char == "N":
    stack.add_value(-stack.pop_value())
elif char == "I":
    stack.add_value(stack[stack.pop_value(implicit=False)])