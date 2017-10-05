#!/usr/bin/env python3
import argparse
import subprocess
import logging
import sys
from statistics import median, mean

import gather_stats

log = logging.getLogger()

# This was experimentally verified and not mentioned anywhere? YMMV
# here.
ERR_OOM = -9

class OutOfMemory(Exception):
    pass

def run_experiment(command, timeout_ms, size, cmd_args=None):
    cli_args =  [command, '-time', str(timeout_ms)]
    if cmd_args:
        extra_args_list = cmd_args.split(" ")
        for arg in extra_args_list:
            cli_args.append(arg)
    cli_args.append(str(size))
    log.debug("Invoking command %s", " ".join(cli_args))
    try:
        result = subprocess.check_output(cli_args)\
                           .decode('utf-8').split('\n')
        d = gather_stats.parse_stdin(result)
        runtime = str(d['runtime'])
        failures = str(d['failures'])
    except subprocess.CalledProcessError as e:
        # Out of memory-error
        if e.returncode == ERR_OOM:
            log.error("Out of memory running %s!",
                      " ".join(cli_args))
            raise OutOfMemory()
        else:
            raise e

    return (runtime, failures)


if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('command', metavar='E', type=str,
                                 help='the experiment to run')
    argument_parser.add_argument('--start', dest='start', type=int,
                                 default=8)
    argument_parser.add_argument('--stop', dest='stop', type=int,
                                 default=1000)
    argument_parser.add_argument('--step-size', dest='step_size', type=int,
                                 default=5)
    argument_parser.add_argument('--timeout-ms', dest='timeout_ms', type=int,
                                 default=1000)
    argument_parser.add_argument('--run-at-least', dest='run_at_least', type=int,
                                 default=0)
    argument_parser.add_argument('--output', dest='output',
                                 type=argparse.FileType('w'),
                                 default='-')
    argument_parser.add_argument('--die-on-timeout', dest='die_on_timeout',
                                 action='store_true')
    argument_parser.add_argument('--cmd-args', dest='cmd_args',
                                 type=str,
                                 default="")
    argument_parser.add_argument('--heading',
                                 type=str,
                                 default=None)
    argument_parser.add_argument('--nrounds',
                                 type=int,
                                 default=1)
    argument_parser.add_argument('--collate-with',
                                 type=str,
                                 choices=["first", "median",
                                         "min", "max", "mean"],
                                 default="first")
    argument_parser.add_argument('--timeout-symbol',
                                 type=str,
                                 default="$\\infty$")
    argument_parser.add_argument('--verbose', '-v', action='count', dest='verbose_count',
                        default=0)


    args = argument_parser.parse_args()

    log_level = (max(3 - args.verbose_count, 0) * 10)
    log.setLevel(log_level)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    ch.setFormatter(formatter)
    log.addHandler(ch)

    if args.collate_with == "first":
        collate_fn = lambda l: l[0]
    elif args.collate_with == "median":
        collate_fn = median
    elif args.collate_with == "min":
        collate_fn = min
    elif args.collate_with == "max":
        collate_fn = max
    elif args.collate_with == "mean":
        collate_fn = mean
    else:
        assert False, "Unsupported collate type %s" % args.collate_with

    with args.output as output_file:
        if args.heading:
            output_file.write(args.heading + "\n")
            log.info("TeX: %s", args.heading)
        for instance_size in range(args.start, args.stop + 1, args.step_size):
            sizes, runtimes, failures_l = [], [], []
            for _ in range(0, args.nrounds):
                size = instance_size
                try:
                    runtime, failures = run_experiment(
                        args.command, args.timeout_ms, instance_size, args.cmd_args)
                except OutOfMemory:
                    runtime = float("inf")
                    failures = 0 # I wish there were a better solution than this!

                log.debug("{} {} {}".format(size, runtime, failures))
                sizes.append(int(size))
                try:
                    runtimes.append(float(runtime))
                except ValueError:
                    runtimes.append(float("inf"))
                failures_l.append(int(failures))

            size = int(collate_fn(sizes))
            runtime = collate_fn(runtimes)
            failures = int(collate_fn(failures_l))

            if runtime == float("inf"):
                runtime_s = args.timeout_symbol
            else:
                runtime_s = "{:.3f}".format(runtime)

            tex_line = "{:d} & {} & {} \\\\".format(size, runtime_s, failures)
            output_file.write(tex_line + "\n")
            log.info("TeX: %s", tex_line)

            if runtime == float("inf") and \
               instance_size >= args.run_at_least and \
               args.die_on_timeout:
                break
