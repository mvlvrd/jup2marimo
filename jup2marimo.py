import json
import sys

from jinja2 import Environment, FileSystemLoader

from VarFinder import getUndefinedVars, UnparsableError

env = Environment(loader=FileSystemLoader("templates"))
cellTemplate = env.get_template("codeCell.py.jinja")
marimoTemplate = env.get_template("marimo.py.jinja")
mdTemplate = env.get_template("markdownCell.py.jinja")
errorTemplate = env.get_template("errorCell.py.jinja")


def parseMDCell(cell):
    mdText = "".join(cell["source"])
    return mdTemplate.render(mdText=mdText)


def parseLine(src):
    magics, body = [], []
    for line in src:
        line = line.rstrip()
        if line.startswith('%'):
            magics.append(line)
        else:
            body.append(line)
    return "\n".join(magics), "\n".join(body)


def parseCodeCell(cell):
    "TODO: See what to do with Jupyter magics. Right now they are just avoided."
    if not cell["source"]:
        return None
    src = cell["source"]
    magics, body = parseLine(src)
    func_name = "_"
    try:
        args, returnVals = getUndefinedVars(body)
    except UnparsableError as unparsableError:
        return errorTemplate.render(body=body)
    returnVals = f"({returnVals.pop()},)" if len(returnVals) == 1 else ", ".join(sorted(returnVals))
    return cellTemplate.render(
        func_name=func_name, args=sorted(args), body=body.split('\n'), returnVals=returnVals
    )


def convertJupyter(jupyterFileName):
    with open(jupyterFileName) as inFile:
        jupy = json.load(inFile)

    marimo_cells = []
    needsMO = False
    for cell in jupy["cells"]:
        cell_type = cell["cell_type"]
        if cell_type == "code":
            outCell = parseCodeCell(cell)
        elif cell_type == "markdown":
            needsMO = True
            outCell = parseMDCell(cell)
        else:
            outCell = None

        if outCell:
            marimo_cells.append(outCell)

    marimotxt = marimoTemplate.render(cells=marimo_cells, needsMO=needsMO)
    return marimotxt


if __name__ == "__main__":
    jupyterFileName = sys.argv[1]

    output = convertJupyter(jupyterFileName)
    print(output)
