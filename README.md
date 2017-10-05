# What is this?

This is a repository of helpful scripts and utilities for running experiments in the COCP course at Uppsala University.

# Usage and Examples
This repository currently contains the following:

- A Vagrantfile to set up an Ubuntu-based virtual machine with the
  latest version of Gecode compiled.
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


