def cmd_export(path, fmt):
    return f"exported {path} as {fmt}"

def main(argv):
    # real invocation is:  prog <path> <fmt>   ->  argv[1]=path, argv[2]=fmt
    # BUG: arguments passed in the wrong order.
    return cmd_export(argv[2], argv[1])
