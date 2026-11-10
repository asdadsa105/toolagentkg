import functools
import shlex

def param_decorator(func):
    @functools.wraps(func)
    def wrapper(param_string):
        params = {}
        args = []
        if ',' in param_string:
            param_split = param_string.split(',')
        elif ' ' in param_string:
            param_split = param_string.split(' ')
        else:
            param_split = param_string.strip()
        for param in param_split:    
            param = shlex.split(param)[0]
            if "=" in param:
                key, value = param.split('=')
            elif ":" in param:
                key, value = param.split(':')
            else:
                args.append(param.strip())
                continue
            params[key.strip()] = value.strip()
        return func(*args, **params)
    return wrapper

def param_decorator_download_paper(func):
    @functools.wraps(func)
    def wrapper(param_string):
        params = {}
        args = []

        param_split = shlex.split(param_string)

        for param in param_split:
            if "=" in param:
                key, value = param.split('=')
                try:
                    value = int(value)
                except ValueError:
                    pass
                params[key.strip()] = value
            else:
                args.append(param.strip())
        
        return func(*args, **params)

    return wrapper