import os
from contextlib import contextmanager
import copy
import itertools
import argparse
import random
import importlib

import daiquiri
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

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


def deserialise_options(option_s):
    """
    Take a serialised dictionary on the form key=value,key=value... and
    return an actual dictionary.
    """
    pairs = option_s.split(",")

    options = {}
    for pair in pairs:
        k, v = [s.strip() for s in pair.split("=")]
        options[k] = v
    return options


def load_palette(palette_str):
    if not palette_str:
        return None

    try:
        import palettable
        group_name, scheme_name = palette_str.split(".")
        colours = random_cycle_list(getattr(getattr(palettable, group_name),
                                            scheme_name).mpl_colors)
        return colours
    except ModuleNotFoundError:
        log.error("Palettable module not installed -- foregoing colour palettes!")
        return None


def random_cycle_list(lst):
    split_at = random.randint(0, len(lst)-2)
    fst, snd = lst[:split_at], lst[split_at:]
    return [*snd, *fst]


def render_pyplot_scatter_plot(xs, ys, data_labels, file_name,
                               x_label="", y_label="", colours=None,
                               x_range=None, y_range=None):

    with PdfPages(file_name) as pp:
        fig, ax = plt.subplots()
        if colours:
            plt.scatter(x=xs, y=ys, c=colours)
        else:
            plt.scatter(x=xs, y=ys)

        for i, txt in enumerate(data_labels):
            ax.annotate(txt, (xs[i], ys[i]), fontsize='xx-small')

        ax.set_ylabel(y_label)
        ax.set_xlabel(x_label)

        if x_range:
            xlo, xhi = [float(x) for x in x_range.split(":")]
            ax.set_xlim(xlo, xhi)
        if y_range:
            ylo, yhi = [float(y) for y in y_range.split(":")]
            ax.set_ylim(ylo, yhi)

        plt.tight_layout()
        pp.savefig()
