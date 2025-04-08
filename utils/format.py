from collections import Counter

USE_MARKDOWN = True


def format_table(data, extra_space=4, right_align_columns=range(1, 99999), use_markdown=USE_MARKDOWN):
    # Find the maximum length of each column
    col_widths = Counter()
    numeric_cols = []
    if not any(r is None for r in data):
        data.insert(1, None)

    for row in data:
        if not row:
            continue

        for i, item in enumerate(row):
            if isinstance(item, int | float):
                numeric_cols.append(i)
                item = row[i] = f'{item:_}'

            col_widths[i] = max(col_widths[i], len(str(item)))

    if right_align_columns is None:
        right_align_columns = numeric_cols

    col_count = len(col_widths)
    one_row_len = sum(col_widths.values()) + extra_space * (col_count - 1)
    line_row = "-" * one_row_len
    if use_markdown:
        extra_space = 2
        lr = []
        for i in range(col_count):
            j = col_widths[i] + extra_space
            lr.append(j * "-")
        line_row = "|" + ("|".join(lr)) + "|"
        extra_space = 0 # for markdown we will do this manually

    # Print each row with proper alignment
    result = []
    for row in data:
        if row is None:
            result.append(line_row)
            continue

        cols = []
        if use_markdown:
            i = len(row)
            while i < col_count:
                row.append(" ")
                i += 1

        for i, item in enumerate(row):
            if i in right_align_columns:
                col = str(item).rjust(col_widths[i]) + " " * extra_space
            else:
                col = str(item).ljust(col_widths[i] + extra_space)
            cols.append(col)

        if use_markdown:
            row_str = "| " + (" | ".join(cols)) + " |"
        else:
            row_str = "".join(cols).rstrip()
        result.append(row_str)

    return "\n".join(result)


def print_table(data, extra_space=4, right_align_columns=range(1, 99999), use_markdown=USE_MARKDOWN):
    print(format_table(data, extra_space, right_align_columns, use_markdown))


def pct(a, total):
    if total == 0:
        return replace_trailing_zero_with_space(0)
    return replace_trailing_zero_with_space(100 * a / total)


def replace_trailing_zero_with_space(ratio):
    s = f'{ratio:.2f}'
    ss = s.rstrip('0').rstrip('.')
    return ss + (" " * (len(s) - len(ss)))


def trim_trailing_zero(num):
    s = f'{num:.2f}'
    return s.rstrip('0').rstrip('.')


def pct_row(name, a, total):
    return [name, a, pct(a, total)]


def pct2_row(name, a, b):
    return pct_row(name, a, (a + b))


def print_h1(s):
    print(f'# {s}')


def print_h2(s):
    print(f'## {s}')


def print_h3(s):
    print(f'### {s}')


def print_h4(s):
    print(f'#### {s}')
