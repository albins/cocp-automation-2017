import conductor.gather_stats
from conductor.common import fmt_dict

from statistics import median, mean
import subprocess
import sys

import daiquiri

log = daiquiri.getLogger()


# This was experimentally verified and not mentioned anywhere? YMMV
# here.
ERR_OOM = -9

ALLOWED_COLLATE_METHODS = ["first", "median",
                           "min", "max", "mean"]


class OutOfMemory(Exception):
    pass


def run_experiment(command, timeout_ms, size, cmd_args=[]):
    cli_args = [command,
                '-time',
                str(timeout_ms),
                *[str(a) for a in cmd_args],
                str(size)]

    log.debug("Invoking command %s", " ".join(cli_args))
    try:
        result = subprocess.check_output(cli_args)\
                           .decode('utf-8').split('\n')
        try:
            d = conductor.gather_stats.parse_stdin(result)
            runtime = str(d['runtime'])
            failures = str(d['failures'])
        except KeyError as e:
            log.error("Invalid output from command %s: %s",
                      command,
                      ", ".join(result))
            raise e
    except subprocess.CalledProcessError as e:
        # Out of memory-error
        if e.returncode == ERR_OOM:
            log.error("Out of memory running %s!",
                      " ".join(cli_args))
            raise OutOfMemory()
        else:
            raise e

    return (runtime, failures)


def run_experiments(command, args, settings):
    """
    Return a list of [instance_size, runtime_ms, number_of_failures]"

    Runtime is inf if a timeout or memory-out occurred.

    Failures is 0 if a memory-out occurred, as that information is not
    available in that case.
    """

    log.debug(("Running experiment command %s with arguments"
               " %s and settings %s"),
              command, ", ".join(args), fmt_dict(settings))

    if settings['collate-with'] == "first":
        collate_fn = lambda l: l[0]
    elif settings['collate-with'] == "median":
        collate_fn = median
    elif settings['collate-with'] == "min":
        collate_fn = min
    elif settings['collate-with'] == "max":
        collate_fn = max
    elif settings['collate-with'] == "mean":
        collate_fn = mean
    else:
        assert False, "Unsupported collate type %s" % settings['collate-with']

    results = []
    for instance_size in range(settings['start'], settings['stop'] + 1,
                               settings['step-size']):
        for _ in range(0, settings['nrounds']):
            size = instance_size
            runtimes, failures_l = [], []

            try:
                runtime, failures = run_experiment(
                    command,
                    settings['timeout-ms'],
                    instance_size,
                    args)

            except OutOfMemory:
                runtime = float("inf")
                failures = 0  # I wish there were a better solution than this!

            log.debug("{} {} {}".format(size, runtime, failures))
            try:
                runtimes.append(float(runtime))
            except ValueError:
                runtimes.append(float("inf"))
            failures_l.append(int(failures))

        runtime = collate_fn(runtimes)
        failures = int(collate_fn(failures_l))
        results.append((size, runtime, failures))
        if runtime == float("inf") and \
           instance_size >= settings['run-at-least'] and \
           settings['die-on-timeout']:
            break
    return results
