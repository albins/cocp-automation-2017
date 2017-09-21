#!/usr/bin/env python

import itertools
import sys

if __name__ == '__main__':
    base = sys.argv[1]
    A = [s.strip() for s in sys.argv[2].split(",")]
    B = [s.strip() for s in sys.argv[3].split(",")]

    if len(sys.argv) > 3:
        suffix = sys.argv[4]
    else:
        suffix = ""

    print(" ".join(["{}-{}-{}{}".format(base, a, b, suffix) for a, b in itertools.product(A, B)]))
