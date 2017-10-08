#!/usr/bin/env python3
from conductor.common import fmt_dict

import os
import sys
import random

if __name__ == '__main__':
    random.seed()

    print("I am running with arguments {} and environment {}"
          .format(" ".join(sys.argv), fmt_dict(os.environ)))

    n = int(sys.argv[-1])
    if n < 50:
        print("runtime: {}".format(random.randint(n, 10*n)))
        print("failures: {}".format(random.randint(n, 1000*n)))
    else:
        print("runtime: Timeout")
        print("failures: 72")
