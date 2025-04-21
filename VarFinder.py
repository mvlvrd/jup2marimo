import ast
import builtins
import sys


class UnparsableError(Exception):
    pass


class VarFinder(ast.NodeVisitor):
    # TODO: It doesn't work well when variables are used before being defined.
    # This could be done by checking the variable is Stored when it is being Loaded,
    # however this method doesn't work well with comprehension targets.
    # E.g. x + 1;x = 4

    def __init__(self):
        self.default_vars = set(dir(builtins)).union(globals().keys())
        self.nameSpaces = [self.default_vars.copy()]
        self.used_vars = [set()]
        self.undefinedVars = set()
        self.is_marimo_parsable = True

        for name in "ListComp", "SetComp", "DictComp", "GeneratorExp":
            methodName = f"visit_{name}"
            setattr(self, methodName, self.visit_Comp)

        for name in "Import", "ImportFrom":
            methodName = f"visit_{name}"
            setattr(self, methodName, self.visit_import)

        # def generic_visit(self, node):
        #     print(node)
        #     ast.NodeVisitor.generic_visit(self, node)

    def addNamespace(self, *newNames):
        self.used_vars.append(set())
        self.nameSpaces.append(set(*newNames))

    def closeNamespace(self):
        for useVar in self.used_vars[-1]:
            unDefined = True
            for nmspc in self.nameSpaces[::-1]:
                if useVar in nmspc:
                    unDefined = False
                    break
            if unDefined:
                self.undefinedVars.add(useVar)
        self.used_vars.pop()
        return self.nameSpaces.pop()

    def visit_Comp(self, node):
        self.addNamespace()
        self.generic_visit(node)
        self.closeNamespace()

    def visit_Lambda(self, node):
        self.addNamespace(arg.arg for arg in node.args.args)
        self.generic_visit(node)
        self.closeNamespace()

    def visit_FunctionDef(self, node):
        self.nameSpaces[-1].add(node.name)
        self.addNamespace(arg.arg for arg in node.args.args)
        self.generic_visit(node)
        self.closeNamespace()

    def visit_ClassDef(self, node):
        self.nameSpaces[-1].add(node.name)
        self.addNamespace()
        self.generic_visit(node)
        self.closeNamespace()

    def visit_Name(self, node):
        name = node.id
        ctx = node.ctx
        if isinstance(ctx, ast.Load):
            self.used_vars[-1].add(name)
        elif isinstance(ctx, ast.Store):
            self.nameSpaces[-1].add(name)
        elif isinstance(ctx, ast.Del):
            pass  # TODO

    def visit_import(self, node):
        names = [alias.asname if alias.asname else alias.name for alias in node.names]
        if "*" in names:
            raise UnparsableError()
        self.nameSpaces[-1].update(names)
        self.generic_visit(node)

    def getUndefinedVars(self):
        # Returns Undefined and Defined Vars
        # all_def_vars = set().union(*self.nameSpaces)
        all_def_vars = self.closeNamespace()
        return self.undefinedVars, all_def_vars - self.default_vars


def getUndefinedVars(code):
    tree = ast.parse(code)
    varFinder = VarFinder()
    varFinder.visit(tree)
    return varFinder.getUndefinedVars()


if __name__ == "__main__":
    with open(sys.argv[1]) as inFile:
        code = inFile.read()

    undef_vars = getUndefinedVars(code)
    print(undef_vars)
