#!/usr/bin/env python
import argparse
import subprocess
import sys

import gather_stats

def run_experiment(command, timeout_ms, size, cmd_args):
    result = subprocess.check_output(
        [command, '-time', str(timeout_ms), str(size),
         cmd_args]).decode('utf-8').split('\n')

    d = gather_stats.parse_stdin(result)
    runtime = str(d['runtime'])
    failures = str(d['failures'])
    return (size, runtime, failures)


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
                                 type=argparse.FileType('a'),
                                 default='-')
    argument_parser.add_argument('--die-on-timeout', dest='die_on_timeout',
                                 action='store_true')
    argument_parser.add_argument('--cmd-args', dest='cmd_args',
                                 type=str,
                                 default="")


    args = argument_parser.parse_args()
    with args.output as output_file:
        for instance_size in range(args.start, args.stop + 1, args.step_size):
            size, runtime, failures = run_experiment(
                args.command, args.timeout_ms, instance_size, args.cmd_args)
            tex_line = "{} & {} & {} \\\\".format(size, runtime, failures)
            output_file.write(tex_line + "\n")
            print(tex_line)

            if runtime.lower() == 'timeout' and \
               instance_size >= args.run_at_least and \
               args.die_on_timeout:
                break
