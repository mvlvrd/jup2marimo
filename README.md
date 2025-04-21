# jup2marimo

This is a simple tool to convert Jupyter notebooks into Marimo.
It doesn't intend to improve on the actual tool from the official repo, it is mostly a learning exercise for me to better understand the Marimo format and also the ast Python library. Nevertheless, it works in simple examples.

### Usage:
python jup2marimo.py JUPYTERFILE

It outputs the Marimo code to standard output.

### TODOs:
- It fails when variables are used before being defined in the same cell.
- Jupyter magics are just discarded.
- del statements are ignored.
