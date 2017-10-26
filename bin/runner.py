#!/usr/bin/env python3
import conductor.run_experiments
import conductor.common

from conductor.run_experiments import ALLOWED_COLLATE_METHODS as COLLATE_METHODS

import argparse

import daiquiri

log = daiquiri.getLogger()

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
                                 choices=COLLATE_METHODS,
                                 default="first")
    argument_parser.add_argument('--timeout-symbol',
                                 type=str,
                                 default="$\\infty$")
    argument_parser.add_argument('--verbose', '-v',
                                 action='count',
                                 dest='verbose_count',
                                 default=0)

    args = argument_parser.parse_args()

    daiquiri.setup()
    conductor.common.set_log_level_from_args(args, log)
    cmd_args = args.cmd_args.split(" ") if args.cmd_args else []

    results = conductor.run_experiments.run_experiments(
        args.command,
        cmd_args,
        settings={
            'collate-with': args.collate_with,
            'nrounds': args.nrounds,
            'die-on-timeout': args.die_on_timeout,
            'run-at-least': args.run_at_least,
            'timeout-ms': args.timeout_ms,
            'step-size': args.step_size,
            'stop': args.stop,
            'start': args.start})

    with args.output as output_file:
        if args.heading:
            output_file.write(args.heading + "\n")
            log.info("TeX: %s", args.heading)

        for size, runtime, failures in results:
            if runtime == float("inf"):
                runtime_s = args.timeout_symbol
            else:
                runtime_s = "{:.3f}".format(runtime)
            tex_line = "{:d} & {} & {} \\\\".format(size, runtime_s, failures)
            output_file.write(tex_line + "\n")
            log.info("TeX: %s", tex_line)
