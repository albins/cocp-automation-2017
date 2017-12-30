import conductor.gather_stats
from conductor.common import fmt_dict

from statistics import median, mean
import subprocess
import sys
import re

import daiquiri

log = daiquiri.getLogger()


RUNTIME_RE = r"\s*runtime:.*\((?P<timeout_ms>[0-9\.]+)\s+ms\).*"
REASON_RE = r"\s*reason:\s+(?P<reason>.*)"
FAILURES_RE = r"\s*failures:\s+(?P<failures>.*)"
# This was experimentally verified and not mentioned anywhere? YMMV
# here.
ERR_OOM = -9

ALLOWED_COLLATE_METHODS = ["first", "median",
                           "min", "max", "mean"]


class OutOfMemory(Exception):
    pass


class Timeout(Exception):
    pass


def handle_captures(line, captures, capture_conf):
    for c_name, c in capture_conf.items():
        convert_fn = c['type']
        capture_re = re.compile(c['regex'])
        match = capture_re.match(line)

        if match and not (c_name in captures and c['use'] == 'first'):
            log.debug("Re %s matched: %s", c_name, match)
            captures[c_name] = convert_fn(match.group(c_name))
        else:
            log.debug("Re %s did not match", c_name)



def parse_gecode_output(in_file, capture=None):
    timeout_re = re.compile(RUNTIME_RE)
    reason_re = re.compile(REASON_RE)
    failures_re = re.compile(FAILURES_RE)
    runtime = None
    reason = None
    failures = None
    captures = {}

    for line in in_file:
        if not line.strip():
            continue
        #log.debug("Read line: %s", line)
        tout_match = timeout_re.match(line)

        if capture:
            handle_captures(line, captures, capture_conf=capture)

        if failures_re.match(line):
            failures = int(failures_re.match(line).group('failures'))
            continue

        # Don't match if we have timed out
        if tout_match and not runtime:
            runtime = float(tout_match.group('timeout_ms'))
            continue

        if reason_re.match(line):
            reason = reason_re.match(line).group('reason')
            log.debug("Stopped search with message '%s'", reason)
            if "time" in reason:
                runtime = float("inf")

    assert runtime, "Found no runtime in the input!"

    return {'runtime': runtime / 1000,
            'failures': failures,
            **captures}


def run_experiment(command, cmd_args, capture=None):
    cli_args = [command, *[str(a) for a in cmd_args]]

    log.debug("Invoking command %s", " ".join(cli_args))
    try:
        result = subprocess.check_output(cli_args)\
                           .decode('utf-8').split('\n')
        try:
            res = parse_gecode_output(result, capture=capture)
            log.info("Captured data: %s", res)
            return res
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

    capture = settings.get('capture', {})
    for c_name, _c_opts in capture.items():
        capture[c_name]['type'] = lambda x: int(x)

    results = []
    runtimes, failures_l, res_l = [], [], []

    for _ in range(0, settings['nrounds']):
        try:
            res = run_experiment(
                command,
                args,
                capture=capture)
            runtime = res['runtime']
            failures = res['failures']

        except OutOfMemory:
            runtime = float("inf")
            failures = 0  # I wish there were a better solution than this!

        runtimes.append(float(runtime))
        failures_l.append(int(failures))

        del res['runtime']
        del res['failures']
        res_l.append(res)

        # Die early on timeout
        if settings['die-on-timeout'] and runtimes[-1] == float("inf"):
            break

    runtime = collate_fn(runtimes)
    failures = int(collate_fn(failures_l))
    results.append({'runtime': runtime,
                    'failures': failures,
                    # Fixme: this is slightly controversial: use the
                    # captured results from the first run.
                    **res_l[0]})
    # if runtime == float("inf") and settings['die-on-timeout']:
    #     raise Timeout("Timeout!")
    return results
