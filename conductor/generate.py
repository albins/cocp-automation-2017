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


def generate_graph(graph_cfg, experiment_data, translations):
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
        exp_cfg = conductor.common.deserialise_options(exp_cfg_s, translations)
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


def write_table(filename, heading, table_rows, timeout_symbol, sort_by):
    log.info("Writing %d table rows to %s", len(table_rows), filename)
    index_fn = lambda row: row[sort_by]
    table_rows.sort(key=index_fn)

    with open(filename, "w") as output_file:
        output_file.write(heading + '\n')
        for size, runtime, failures in table_rows:
            if runtime == float("inf"):
                runtime_s = timeout_symbol
            else:
                runtime_s = "{:.3f}".format(runtime)
            formatted_row = ("{:d} & {} & {} \\\\"
                             .format(size, runtime_s, failures))

            output_file.write(formatted_row + "\n")
            log.debug("Wrote TeX row: %s", formatted_row)


def handle_append(table, experiment, method, skip_rows, skip_columns):
    """
    In-place append the given experiment data to table according to the
    desired method.
    """
    log.debug("Appending %d lines to table using %s, skipping %d rows and %d columns",
              len(experiment), method, skip_rows, skip_columns)


def generate_tables(output_cfg, experiments, translations):
    """
    Output one or more LaTeX tables.
    """
    heading_template = output_cfg['heading']
    timeout_symbol = output_cfg['timeout-symbol']
    sort_by = output_cfg['sort-by']
    filename_template = output_cfg['file']
    combination_method = output_cfg['combine-experiments']['using']
    skip_rows = output_cfg['combine-experiments'].get('skip-rows', 0)
    skip_columns = output_cfg['combine-experiments'].get('skip-columns', 0)

    tables = defaultdict(list)
    headings = {}

    for experiment in experiments:
        for setup_s, results in experiment.items():
            setup = conductor.common.deserialise_options(setup_s, translations)
            file_name = filename_template.format(**setup)

            if file_name in tables:
                handle_append(tables, results,
                          method=combination_method,
                              skip_rows=skip_rows,
                              skip_columns=skip_columns)
                continue

            heading = heading_template.format(**setup)
            headings[file_name] = heading
            tables[file_name] = results

    for filename, table_rows in tables.items():
        heading = headings[filename]
        write_table(filename,
                    heading,
                    table_rows,
                    sort_by=sort_by,
                    timeout_symbol=timeout_symbol)


def generate_output(output_cfg, experiments, translations):
    if output_cfg['type'] == 'graph':
        generate_graph(output_cfg, list(experiments.values())[0], translations)
    elif output_cfg['type'] == 'tex-table':
        generate_tables(output_cfg, experiments.values(), translations)
    else:
        assert False, "Unknown output type %s" % output_cfg['type']
