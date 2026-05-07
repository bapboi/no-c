import os
from lexer import Lexer
from parser import Parser, Program, ImportStatement


def loadProgram(entryPath):
    entryPath = os.path.abspath(entryPath)
    baseDir = os.path.dirname(entryPath)
    loaded = set()
    allImports = []
    allModules = []

    def load(path):
        path = os.path.abspath(path)
        if path in loaded:
            return
        loaded.add(path)

        try:
            src = open(path).read()
        except FileNotFoundError:
            raise Exception(f"file not found: '{path}'")

        lexer = Lexer(src)
        tokens, err = lexer.createTokens()
        if err:
            raise Exception(err.as_string())

        try:
            ast = Parser(tokens).parse()
        except Exception as e:
            raise Exception(f"{os.path.basename(path)}: {e}")

        for imp in ast.imports:
            if imp.name == "io":
                if not any(i.name == "io" for i in allImports):
                    allImports.append(imp)
                continue
            depPath = os.path.join(baseDir, imp.name + ".nc")
            if not os.path.exists(depPath):
                raise Exception(f"import '{imp.name}': file '{depPath}' not found")
            load(depPath)

        for mod in ast.modules:
            if any(m.name == mod.name for m in allModules):
                raise Exception(f"duplicate module name '{mod.name}'")
            allModules.append(mod)

    load(entryPath)
    return Program(allImports, allModules)
