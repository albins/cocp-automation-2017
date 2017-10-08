# What is this?

This is a repository of helpful scripts and utilities for running
experiments in the COCP course at Uppsala University. It is also
packaged together with an utility called Conductor, which is used to
conduct systematic experiments and present their output.

It currently requires Python 3.5 or better.

# Setting up a Vagrant box for development


# Installing

This repository contains a Pip package for Conductor, which means it can
be installed using:

```
$ pip3 install https://github.com/albins/cocp-automation-2017
```

You can also do `python3 setup.py develop` or `python3 setup.py install`
in a cloned repository.

If you are going full-on, you can also just copy (or symbolically link)
the Vagrantfile into your development directory and set up a Vagrant box
as usual (e.g. `vagrant up`). The resulting box will have everything you
need already installed, and your project directory will be available in
`/vagrant/` after entering the machine using `vagrant ssh`.

# Usage and Examples

You configure your experiments for Conductor using a YAML configuration
file, by default assumed to be in the present directory and called
`experiments.yaml`. An example configuration file is provided in
`doc/experiments.yaml`.

The following features are implemented:
- Creating cross/cartesian product combinations of options
- Using templates to set command-line options and environment variables
  for experiments
- Override experiment runner options for certain combinations (e.g. run
  10 experiments for value heuristics involving randomness as per
  instructions)

An experiment configuration running instance sizes in steps of 5, starting at 8 and up to 10 000 or a timeout of 5 000 ms, with 10 rounds and median values for variable/value selection heuristics might look like this. Options are injected into the binary using both environment variables and command-line options (`-propagate`):

``` yaml
queens-experiments:
  val_heuristic:
    - int_val_max
    - int_val_rnd
  var_heuristic:
    - int_var_max
    - int_var_rnd
  version:
    - 0
    - 1

  combine:
    options:
      - val_heuristic
      - var_heuristic
      - version
    with: cartesian-product

  # Override run options for experiments using random-based heuristics
  override-settings:
    - option: val_heuristic
      value: int_val_rnd
      settings:
        nrounds: 10
        collate-with: median

    - option: var_heuristic
      value: int_var_rnd
      settings:
        nrounds: 10
        collate-with: median

  # Default run options
  nrounds: 1
  run-at-least: 1
  timeout-ms: 5000
  die-on-timeout: true
  collate-with: first
  start: 8
  stop: 10000
  step-size: 5

  command: "./queens{version}"
  command-args:
    - "-propagation"
    - "{var_heuristic}"
  environment:
    VAL_HEURISTIC: "{val_heuristic}"
```

This will run a series of commands, e.g. 
`VAL_HEURISTIC=int_val_rnd ./queens0 -propagation int_var_rnd -time 5000 8`.

The configuration key `runs` contains a set (dictionary really) of
mappings between experiment names and their desired outputs. This
example would produce a run named "assignment-A" that produces a number
of LaTeX tables table and a graph of the results:

``` yaml
runs:
  assignment-A:
    experiments:
      - queens-experiments
    output:
      - type: graph
        label: "queens{version} with {var_heuristic}/{val_heuristic}"
        file: queens_comparison.pdf
      - type: tex-table
        combine: split-experiments
        heading: "$n$ & Time & Failures \\\\ \midrule"
        timeout-symbol: Timeout
        sort-by: instance-size
        file-pattern: "queens{version}_comparison_{var_heuristic}_{val_heuristic}.tex"
```

This experiment setup would be invoked by:

```
$ conductor --run assignment-A
```

And would produce a comparison graph in `queens_comparison.pdf` and one
table per combination, named `queens1_comparison_int_val_rnd_int_var_rnd.tex`, etc.

# Other Utilities
This package installs the following scripts in your `$PATH`, in addition
to Conductor:

- `runner.py` -- a script to run and record results in Gecode as LaTeX
  tables
- `merge_tables.py` -- a script to merge, filter, sort, and transpose
  LaTeX tables
- `graph_table.py` -- a script using Pyplot to plot a provided LaTeX
  table to a PDF
- `gather_stats.py` as provided by the TAs in the autumn 2017, included
  for convenience

See `Makefile.example` for suggestions on how to use these tools to
automate performing certain experiments for inclusion into assignment
reports.

# Developing

`python3 setup.py develop`


