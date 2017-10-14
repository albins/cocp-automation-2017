import conductor.common

from collections import defaultdict

import daiquiri
import matplotlib
# This disables interactive back-ends for
# Matplotlib. Maybe. Possibly. No-one seems to know what it does.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

log = daiquiri.getLogger()


def plot_data_as_pdf(data, filename, x_label, y_label):
    """
    Take data on the form label: [x-values, y-values] and plot a graph
    to a given file name.
    """

    with PdfPages(filename) as pp:
        fig, ax = plt.subplots()
        ax.set_ylabel(y_label)
        ax.set_xlabel(x_label)

        for label, (xs, ys) in data.items():
            ax.plot(xs, ys, label=label)

        ax.legend(loc="upper right")
        pp.savefig()


def generate_graph(graph_cfg, experiment_data):
    """
    Generate a PDF graph with a given configuration and a single
    instance of experiment data.
    """
    # go through data and collect it according to its label
    # dump it according to settings

    label_pattern = graph_cfg.get('label', "")
    x_axis_index = graph_cfg.get('x-index', 0)
    y_axis_index = graph_cfg.get('y-index', 1)
    x_label = graph_cfg.get('x-label', "")
    y_label = graph_cfg.get('y-label', "")

    # label -> (x-values, y-values)
    plots = defaultdict(lambda: ([], []))

    for exp_cfg_s, exp_results in experiment_data.items():
        exp_cfg = conductor.common.deserialise_options(exp_cfg_s)
        rendered_label = label_pattern.format(**exp_cfg)
        log.info("Adding plot with label %s", rendered_label)

        xs, ys = [], []

        for r in exp_results:

            try:
                xv, yv = float(r[x_axis_index]), float(r[y_axis_index])
                if xv == float("inf") or yv == float("inf"):
                    log.warning("Skipping infinite measurement!")
                    continue
                xs.append(xv)
                ys.append(yv)
            except ValueError as e:
                log.warning("Skipping non-numeric data point %s, a timeout?", e)
                continue

        assert len(xs) == len(ys), "Must have same number of x and y values!"

        old_xs, old_ys = plots[rendered_label]
        plots[rendered_label] = ([*old_xs, *xs], [*old_ys, *ys])

    plot_data_as_pdf(plots,
                     filename=graph_cfg['file'],
                     x_label=x_label,
                     y_label=y_label)


def generate_output(output_cfg, experiments):
    if output_cfg['type'] == 'graph':
        generate_graph(output_cfg, list(experiments.values())[0])
    elif output_cfg['type'] == 'tex-table':
        pass
    else:
        assert False, "Unknown output type %s" % output_cfg['type']
