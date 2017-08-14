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