#!/usr/bin/env python3
import argparse

def read_table(table_filename):
    """
    Read a LaTeX table (without headings) from a file.

    Returns it as a list of rows.
    """
    table = []
    with open(table_filename) as f:
        for line in f:
            line = line.replace("\\", "")
            values = [s.strip() for s in line.split("&") if s.strip()]
            if values:
                table.append(values)
    return table

def write_table(tex_table, table_file, heading):
    """
    Writes a LaTeX table from a list of rows to a file, without
    headings.
    """
    if heading:
        table_file.write(heading + "\n")
    with table_file as f:
        for row in tex_table:
            tex_line = " & ".join([str(x) for x in row]) + " \\\\"
            table_file.write(tex_line + "\n")
            print(tex_line)

def append_column(tex_table, column):
    """
    Takes a table of dimension n x m and a column of dimension n and
    appends it, returning a table of dimension n x m + 1.
    """
    # Pad with n/a
    if len(column) < len(tex_table):
        column = column + (["-"] * (len(tex_table) - len(column)))

    for row, val in zip(tex_table, column):
        row.append(val)
    return tex_table


def append_row(tex_table, row):
    """
    Takes a table of dimension n x m and a column of dimension m and
    appends it, returning a table of dimension n + 1 x m.
    """
    if len(row) < len(tex_table[0]):
        row = row + (["-"] * (len(tex_table[0]) - len(row)))

    tex_table.append(row)
    return tex_table


def transpose_table(tex_table):
    """
    Turn a list of rows to a list of columns, and vice versa.
    """
    return list(map(list, zip(*tex_table)))


if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('--skip-columns', type=int,
                                 default=0)
    argument_parser.add_argument('--skip-rows', type=int,
                                 default=0)
    argument_parser.add_argument('--append-as', type=str,
                                 choices=['columns', 'rows'],
                                 default='columns')
    argument_parser.add_argument('--master-table', type=str,
                                 choices=['longest', 'first'],
                                 default='first')
    argument_parser.add_argument('--skip-master-too',
                                 action='store_true')
    argument_parser.add_argument('files',
                                 nargs='+')
    argument_parser.add_argument('--output', dest='output',
                                 type=argparse.FileType('w'),
                                 default='-')
    argument_parser.add_argument('--heading',
                                 type=str,
                                 default=None)
    argument_parser.add_argument('--sort-by-col',
                                 type=int,
                                 default=None)
    argument_parser.add_argument('--sort-desc',
                                 action='store_true')
    args = argument_parser.parse_args()
    tables = [read_table(table_file) for table_file in args.files]

    if args.master_table == 'longest':
       # Sort by length, longest to shortest
       tables.sort(key=lambda l: len(l), reverse=True)

    master_table = tables[0]
    tables_to_merge = tables[1:]

    if args.skip_master_too:
        if args.skip_columns > 0:
            master_table = [row[args.skip_columns:] for rn, row in enumerate(master_table)
                            if rn >= args.skip_rows]
        elif args.skip_columns < 0:
            master_table = [row[:args.skip_columns] for rn, row in enumerate(master_table)
                                  if rn >= args.skip_rows]

    for i, table in enumerate(tables_to_merge):
        if args.skip_columns > 0:
            tables_to_merge[i] = [row[args.skip_columns:] for rn, row in enumerate(table)
                                  if rn >= args.skip_rows]
        elif args.skip_columns < 0:
            tables_to_merge[i] = [row[:args.skip_columns] for rn, row in enumerate(table)
                                  if rn >= args.skip_rows]

    if args.append_as == 'columns':
        append_fn = append_column
    else:
        append_fn = append_row

    for to_append in tables_to_merge:
        if args.append_as == 'columns':
            to_append = transpose_table(to_append)

        # print("Appending: {} x {}".format(len(to_append),
        #                                   len(to_append[0])))
        # print("to: {} x {}".format(len(master_table),
        #                            len(master_table[0])))

        for row_or_column in to_append:
            master_table = append_fn(master_table, row_or_column)

    if args.sort_by_col is not None:
        index_fn = lambda row: row[args.sort_by_col]
        master_table.sort(key=index_fn, reverse=args.sort_desc)

    write_table(master_table, args.output, heading=args.heading)
