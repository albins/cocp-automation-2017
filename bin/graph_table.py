#!/usr/bin/env python3

import argparse
import random
import logging
import sys

from merge_tables import read_table
from conductor.common import render_pyplot_scatter_plot, load_palette

log = logging.getLogger()


if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('--skip-columns', type=int,
                                 default=0)
    argument_parser.add_argument('--skip-rows', type=int,
                                 default=0)
    argument_parser.add_argument('table_file', type=str)
    argument_parser.add_argument('output_file', type=str)
    argument_parser.add_argument('--palette',
                                 type=str,
                                 help="Try eg wesanderson.Moonrise1_5",
                                 default=None)
    argument_parser.add_argument('--x-column',
                                 type=int,
                                 help="AFTER skipping!",
                                 default=0)
    argument_parser.add_argument('--y-column',
                                 type=int,
                                 help="AFTER skipping!",
                                 default=1)
    argument_parser.add_argument('--x-label',
                                 type=str,
                                 default="")
    argument_parser.add_argument('--y-label',
                                 type=str,
                                 default="")
    argument_parser.add_argument('--x-range',
                                 type=str,
                                 help="format 0:10",
                                 default=None)
    argument_parser.add_argument('--y-range',
                                 type=str,
                                 help="format 0:10",
                                 default=None)
    argument_parser.add_argument('--label-values',
                                 action="store_true")

    argument_parser.add_argument('--verbose', '-v', action='count', dest='verbose_count',
                        default=0)

    args = argument_parser.parse_args()

    log_level = (max(3 - args.verbose_count, 0) * 10)
    log.setLevel(log_level)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    ch.setFormatter(formatter)
    log.addHandler(ch)

    try:
        colours = load_palette(args.palette)
    except ValueError:
        log.error("Colour palette must be on the format group.scheme!")
        exit(1)

    values = read_table(args.table_file)

    values = [row[args.skip_columns:] for rn, row in enumerate(values)
                           if rn >= args.skip_rows]

    def convert_float(num_s):
        try:
            return float(num_s)
        except ValueError as e:
            # Handle LaTeX infinity numbers
            if "infty" in num_s or "inf" in num_s:
                return float("inf")
            else:
                raise e

    xs = [convert_float(row[args.x_column]) for row in values]
    ys = [convert_float(row[args.y_column]) for row in values]

    if args.label_values:
        labels = ys
    else:
        labels = []

    render_pyplot_scatter_plot(xs, ys, labels, args.output_file, colours=colours,
                               x_label=args.x_label, y_label=args.y_label,
                               x_range=args.x_range, y_range=args.y_range)
