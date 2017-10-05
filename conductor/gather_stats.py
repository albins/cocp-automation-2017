#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse


def parse_stdin(in_file):
    d = {}
    for line in in_file:
        if ':' in line:
            split = line.split(':')
            stripped = [s.strip() for s in split]
            #if len(stripped) > 2:
            #  print 'Warning: ignoring remaining column in line \'', line, '\''

            # the split(' ')[0] is mainly to get rid of the ms info in runtime
            d[stripped[0]] = stripped[1].split(' ')[0]

    # Something whent wrong
    if 'reason' in d:
        if 'time' in d['reason']:
            d['runtime'] = 'Timeout'
        else:
            d['runtime'] = 'N/A'
    return d


def print_data(d, keys):
    values = [d[key] for key in keys]

    s = '&'.join(values)
    s += '\\\\'
    print(s)

if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser(
        description=("A program to parse output form the COCP exercises."
                     " Pipe the input from your experiment file into it, "
                     " like so: ./queens | gather_stats.py."))
    # Normally, we would save the results but we're not using them now.
    argument_parser.parse_args()

    d = parse_stdin(sys.stdin)
    print_data(d, keys=['runtime', 'failures'])
