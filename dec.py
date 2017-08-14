from ly import instructions

def instruction(name, arity, implicit=True, modifier=None):
    def decorator(func):
        instructions[name] = (func, arity, modifier, implicit)
        return func
    return decorator