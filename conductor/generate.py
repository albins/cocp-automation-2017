import conductor.common

from collections import defaultdict

import daiquiri
import matplotlib
from itertools import repeat
# This disables interactive back-ends for
# Matplotlib. Maybe. Possibly. No-one seems to know what it does.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

log = daiquiri.getLogger()


def plot_data_as_pdf(data, filename, x_label, y_label, legend_loc=None):
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

        if not legend_loc:
            legend_loc = "upper right"

        ax.legend(loc=legend_loc)
        pp.savefig()


def generate_graph(graph_cfg, experiments, translations):
    """
    Generate a PDF graph with a given configuration and a single
    instance of experiment data.
    """
    # go through data and collect it according to its label
    # dump it according to settings

    label_pattern = graph_cfg.get('label', "")
    x_axis_index = graph_cfg.get('x-index')
    y_axis_index = graph_cfg.get('y-index')
    x_label = graph_cfg.get('x-label', "")
    y_label = graph_cfg.get('y-label', "")
    legend_loc = graph_cfg.get('legend-loc', None)

    # we need to make this two-way: filename, lael -> (x-values, y-values)
    # label -> (x-values, y-values)
    plots = defaultdict(lambda: ([], []))

    # For each experiment, go trough each setup then each result and
    # concatenate them into plots.
    for experiment in experiments:
        print(experiment)

    # Finally, render the plots.

    for exp_cfg_s, exp_results in experiments:
        exp_cfg = conductor.common.deserialise_options(exp_cfg_s, translations)
        print(exp_cfg_s)
        rendered_label = label_pattern.render(**exp_cfg)
        log.info("Adding plot with label %s", rendered_label)

        xs, ys = [], []

        for r in exp_results:
            data = {**exp_cfg, **r}
            try:
                xv, yv = float(data[x_axis_index]), float(data[y_axis_index])
                if xv == float("inf") or yv == float("inf"):
                    log.info("Skipping infinite measurement!")
                    continue
                xs.append(xv)
                ys.append(yv)
            except ValueError as e:
                log.warning("Skipping non-numeric data point %s, a timeout?", e)
                continue

        assert len(xs) == len(ys), "Must have same number of x and y values!"

        old_xs, old_ys = plots[rendered_label]
        plots[rendered_label] = ([*old_xs, *xs], [*old_ys, *ys])

    filename = graph_cfg['file'].render()
    plot_data_as_pdf(plots,
                     legend_loc=legend_loc,
                     filename=filename,
                     x_label=x_label,
                     y_label=y_label)


def write_table(filename, heading, table_rows):
    log.info("Writing %d table rows to %s", len(table_rows), filename)

    with open(filename, "w") as output_file:
        output_file.write(heading + '\n')
        for row in table_rows:
            output_file.write(row + "\n")
            log.debug("Wrote row: %s", row)


def generate_tables(output_cfg, experiments, translations):
    """
    Output one or more LaTeX tables.
    """
    heading_template = output_cfg['heading']
    timeout_symbol = output_cfg.get('timeout-symbol', None)
    sort_by = output_cfg['sort-by']
    filename_template = output_cfg['file']
    row_template = output_cfg['row-format']

    tables = defaultdict(list)
    headings = {}


    def sort_key_fn(res):
        try:
            return float(res.get(sort_by))
        except ValueError:
            return res.get(sort_by)

    for experiment in experiments:
        for setup_s, results in experiment.items():
            setup = conductor.common.deserialise_options(setup_s, translations)
            file_name = filename_template.render(**setup)
            heading = heading_template.render(**setup)
            headings[file_name] = heading
            tables[file_name] += list(zip(results, repeat(setup)))

    for filename, results_and_setup in tables.items():
        heading = headings[filename]
        table_rows = []

        # sort everything globally

        results_and_setup.sort(key=lambda x: sort_key_fn({**x[0], **x[1]}),
                               reverse=False)

        # render row-by-row
        for row, setup in results_and_setup:
            # Render the row
            try:
                table_rows.append(row_template.render(**{**setup, **row}))
            except (ValueError, KeyError) as e:
                log.error("Error rendering template: %s", row_template)
                log.error("With data %s", {**setup, **row})
                log.error("Exception was %s", e)
                continue

        write_table(filename,
                    heading,
                    table_rows)


def generate_output(output_cfg, experiments, translations):
    if output_cfg['type'] == 'graph':
        generate_graph(output_cfg, experiments.values(), translations)
    elif output_cfg['type'] == 'text-file':
        generate_tables(output_cfg, experiments.values(), translations)
    else:
        assert False, "Unknown output type %s" % output_cfg['type']
