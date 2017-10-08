import os
from contextlib import contextmanager
import copy
import itertools
import argparse

import daiquiri

log = daiquiri.getLogger()


@contextmanager
def temp_env(environment):
    """
    Temporarily set environment variables.
    """
    old_env = copy.deepcopy(os.environ)

    for key, val in environment.items():
        os.environ[key] = str(val)

    yield

    os.environ = old_env


def cartesian_product(alternatives):
    """
    Takes a dict of {"option1": [alt1, alt2, alt3], "option2": [alt1,
    alt2, alt3]}, returns [{"option1": alt1, "option2": alt1}] etc.
    """

    keys = list(alternatives.keys())
    values = list(alternatives.values())
    value_combinations = list(itertools.product(*values))

    combinations = []
    for value_combination in value_combinations:
        combination = {k: v for k, v in zip(keys, value_combination)}
        combinations.append(combination)

    return combinations


def tuplewise(alternatives):
    pass


def fmt_dict(d):
    return ", ".join(["{}={}".format(k, v) for k, v in d.items()])


def set_log_level_from_args(args, logger):
    log_level = (max(3 - args.verbose_count, 0) * 10)
    logger.setLevel(log_level)


def setup_verbosity_flags(parser):
    parser.add_argument('--verbose', '-v',
                        action='count',
                        dest='verbose_count',
                        help="enable more verbose logging",
                        default=0)


def make_base_parser():
    parser = argparse.ArgumentParser(description="")
    setup_verbosity_flags(parser)
    return parser
