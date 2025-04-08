import re
from ctypes import c_float

NUM_RE = re.compile(r"(-?\d+\.\d+)")
MAKE_UPPER = 'max', 'min', 'abs', 'sd'


def repl(match):
    f = str(c_float(float(match.group(0))).value)

    n = len(f.split(".")[0]) + 1 + 7
    return f[:n] + "f"


def replace_double_with_trimmed_c_float(text):
    for m in MAKE_UPPER:
        text = text.replace(m, m.upper())
    text = text.replace("*", " * ")
    text = text.replace("  *  ", " * ")
    return NUM_RE.sub(repl, text) + ";"


if __name__ == '__main__':
    print("Enter your formula:\n")
    output = replace_double_with_trimmed_c_float(input())
    print()
    print(output)
