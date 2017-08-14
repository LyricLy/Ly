from ly import instructions

def instruction(name, arity, modifier=None):
    def decorator(func):
        instructions[name] = (func, arity, modifier)
        return func
    return decorator