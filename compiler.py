from parser import (
    Program,
    ImportStatement,
    ModuleDeclaration,
    TypeDeclaration,
    FunctionDeclaration,
    VarDeclaration,
    ArrayDeclaration,
    AssignmentStatement,
    IncStatement,
    ReturnStatement,
    IfStatement,
    WhileStatement,
    ForStatement,
    BreakStatement,
    RaiseStatement,
    ExpressionStatement,
    BinaryExpression,
    UnaryExpression,
    CallExpression,
    NewExpression,
    IndexExpression,
    DotExpression,
    ArrayLiteral,
    IntegerLiteral,
    FloatLiteral,
    StringLiteral,
    BoolLiteral,
    NullLiteral,
    ThisExpression,
    Identifier,
)


class Symbol:
    def __init__(self, name, type_, mutable, isArray=False):
        self.name = name
        self.type_ = type_
        self.mutable = mutable
        self.isArray = isArray


class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.symbols = {}

    def declare(self, sym):
        self.symbols[sym.name] = sym

    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def lookupLocal(self, name):
        return self.symbols.get(name)


DEFAULTS = {
    "int": "0",
    "float": "0.0",
    "String": '""',
    "bool": "False",
    "char": "' '",
    "void": "None",
    "null": "None",
}

NC_TYPES = {
    "int": "int",
    "float": "float",
    "String": "str",
    "bool": "bool",
    "char": "str",
}

RUNTIME = """\
class _TypeError(Exception): pass
class _ImmutableError(Exception): pass
class _AccessError(Exception): pass
class _DivisionError(Exception): pass
class _VoidReturnError(Exception): pass
class _RuntimeError(Exception): pass

class io:
    def out(value):
        print(value, end='')
    def outln(value=''):
        print(value)
    def input(prompt=''):
        uval = input(prompt)
        try: 
            return int(uval)
        except ValueError:
            try:
                return float(uval)
            except ValueError:
                return uval

def _div(a, b):
    if b == 0: raise _DivisionError('division by zero')
    return a / b if isinstance(a, float) or isinstance(b, float) else a // b

def _typecheck(val, expected, label):
    py = {'int': int, 'float': float, 'String': str, 'bool': bool, 'char': str}
    if expected in py:
        if expected == 'int' and type(val) is bool:
            raise _TypeError(f"{label}: expected int, got bool")
        if expected == 'bool' and type(val) is int and type(val) is not bool:
            raise _TypeError(f"{label}: expected bool, got int")
        if not isinstance(val, py[expected]):
            raise _TypeError(f"{label}: expected {expected}, got {type(val).__name__}")
    return val

def _add(a, b, label):
    if type(a) != type(b):
        raise _TypeError(f"{label}: '+' requires same types, got {type(a).__name__} and {type(b).__name__}")
    return a + b

def _arrget(arr, idx):
    if idx < 0 or idx >= len(arr):
        raise _RuntimeError(f"array index {idx} out of range (length {len(arr)})")
    return arr[idx]

def _arrset(arr, idx, val):
    if idx == len(arr):
        arr.append(val)
    elif 0 <= idx < len(arr):
        arr[idx] = val
    else:
        raise _RuntimeError(f"array index {idx} out of range (length {len(arr)})")

"""


def err(msg, line=None):
    loc = f"line {line}: " if line else ""
    raise Exception(f"{loc}{msg}")


class Compiler:
    def __init__(self, ast):
        self.ast = ast
        self.moduleExports = {}
        self.currentModule = None
        self.currentClass = None
        self.knownTypes = {}  # typeName -> TypeDeclaration

    def compile_and_run(self):
        src = self.compileNode(self.ast)
        exec(src, {})

    def compileNode(self, node):
        if isinstance(node, Program):
            for mod in node.modules:
                self.moduleExports[mod.name] = set(mod.exports)
                for item in mod.body:
                    if isinstance(item, TypeDeclaration):
                        self.knownTypes[item.name] = item

            moduleSrc = "\n".join(self.compileNode(mod) for mod in node.modules)
            singletons = "\n".join(
                f"{mod.name} = _{mod.name}()" for mod in node.modules
            )
            entry = self.compileEntry()
            return RUNTIME + moduleSrc + "\n" + singletons + "\n" + entry

        elif isinstance(node, ModuleDeclaration):
            self.currentModule = node.name
            outerScope = Scope()

            classes = [item for item in node.body if isinstance(item, TypeDeclaration)]
            varDecls = [
                item
                for item in node.body
                if isinstance(item, (VarDeclaration, ArrayDeclaration))
            ]
            fns = [item for item in node.body if isinstance(item, FunctionDeclaration)]

            classSrc = "\n".join(self.compileClass(c) for c in classes)

            varLines = []
            for decl in varDecls:
                varLines.append(self.compileModuleVar(decl, outerScope))

            mutableNames = {v.name for v in varDecls if v.mutable}

            fnLines = []
            for fn in fns:
                fnLines.append(self.compileFn(fn, outerScope))

            inner = ""
            if varLines:
                inner += "\n".join("    " + line for line in varLines) + "\n\n"
            inner += "    _exports = " + repr(set(node.exports)) + "\n"
            inner += "    _mutable = " + repr(mutableNames) + "\n\n"
            inner += "\n".join(fnLines)

            return (
                classSrc + "\n" if classSrc else ""
            ) + f"class _{node.name}:\n{inner}\n"

        else:
            err(f"unknown top-level node: {type(node)}")

    def compileClass(self, cls):
        self.currentClass = cls.name
        lines = []
        lines.append(f"class {cls.name}:")

        # __init__ from fields
        fieldParams = ["self"]
        for mut, type_, name, default, ln in cls.fields:
            fieldParams.append(name)

        initBody = []
        for mut, type_, name, default, ln in cls.fields:
            initBody.append(f"    self.{name} = {name}")

        if initBody:
            lines.append(f"    def __init__({', '.join(fieldParams)}):")
            for l in initBody:
                lines.append(f"    {l}")
        else:
            lines.append("    def __init__(self):")
            lines.append("        pass")

        classScope = Scope()
        for mut, type_, name, default, ln in cls.fields:
            classScope.declare(Symbol(name, type_, mut))

        for method in cls.methods:
            lines.append(self.compileFn(method, classScope, indent=1, inClass=True))

        self.currentClass = None
        return "\n".join(lines) + "\n"

    def compileModuleVar(self, decl, scope):
        if isinstance(decl, ArrayDeclaration):
            if decl.value == None:
                err(f"'{decl.name}' must be explicitly initialized", decl.line)
            sym = Symbol(decl.name, decl.elemType + "[]", decl.mutable, True)
            scope.declare(sym)
            val = self.compileExpr(decl.value, scope)
            return f"{decl.name} = {val}"
        else:
            if decl.value == None:
                err(f"'{decl.name}' must be explicitly initialized", decl.line)
            sym = Symbol(decl.name, decl.type_, decl.mutable)
            scope.declare(sym)
            val = self.compileExpr(decl.value, scope)
            if decl.type_ in NC_TYPES and not isinstance(decl.value, NullLiteral):
                return f"{decl.name} = _typecheck({val}, '{decl.type_}', 'line {decl.line}')"
            return f"{decl.name} = {val}"

    def compileFn(self, fn, outerScope, indent=1, inClass=False):
        fnScope = Scope(parent=outerScope)
        params = ["self"]
        for mut, type_, pname in fn.params:
            params.append(pname)
            fnScope.declare(Symbol(pname, type_, mut))

        paramStr = ", ".join(params)
        bodyLines = self.compileBlock(fn.body, fnScope, fn.returnType)
        pad = "    " * indent
        bodyPad = "    " * (indent + 1)

        if not bodyLines:
            body = bodyPad + "pass"
        else:
            body = "\n".join(bodyPad + l for l in bodyLines)

        return f"{pad}def {fn.name}({paramStr}):\n{body}\n"

    def compileBlock(self, stmts, scope, returnType=None):
        lines = []
        for stmt in stmts:
            lines.extend(self.compileStmt(stmt, scope, returnType))
        return lines

    def compileStmt(self, node, scope, returnType=None):
        if isinstance(node, VarDeclaration):
            if scope.lookupLocal(node.name):
                err(f"'{node.name}' already declared in this scope", node.line)
            if node.value == None:
                err(f"'{node.name}' must be explicitly initialized", node.line)
            scope.declare(Symbol(node.name, node.type_, node.mutable))
            val = self.compileExpr(node.value, scope)
            if node.type_ in NC_TYPES and not isinstance(node.value, NullLiteral):
                return [
                    f"{node.name} = _typecheck({val}, '{node.type_}', 'line {node.line}')"
                ]
            return [f"{node.name} = {val}"]

        elif isinstance(node, ArrayDeclaration):
            if node.value == None:
                err(f"'{node.name}' must be explicitly initialized", node.line)
            scope.declare(Symbol(node.name, node.elemType + "[]", node.mutable, True))
            val = self.compileExpr(node.value, scope)
            return [f"{node.name} = {val}"]

        elif isinstance(node, AssignmentStatement):
            return self.compileAssignment(node, scope)

        elif isinstance(node, IncStatement):
            return self.compileInc(node, scope)

        elif isinstance(node, ReturnStatement):
            if returnType == "void":
                if node.value != None:
                    err(f"void function cannot return a value", node.line)
                return ["return"]
            val = self.compileExpr(node.value, scope) if node.value != None else "None"
            if returnType and returnType in NC_TYPES and node.value != None:
                return [f"return _typecheck({val}, '{returnType}', 'line {node.line}')"]
            return [f"return {val}"]

        elif isinstance(node, IfStatement):
            cond = self.compileExpr(node.condition, scope)
            lines = [f"if {cond}:"]
            thenLines = self.compileBlock(
                node.thenBody, Scope(parent=scope), returnType
            )
            lines.extend("    " + l for l in (thenLines if thenLines else ["pass"]))
            if node.elseBody:
                lines.append("else:")
                elseLines = self.compileBlock(
                    node.elseBody, Scope(parent=scope), returnType
                )
                lines.extend("    " + l for l in (elseLines if elseLines else ["pass"]))
            return lines

        elif isinstance(node, WhileStatement):
            cond = self.compileExpr(node.condition, scope)
            lines = [f"while {cond}:"]
            bodyLines = self.compileBlock(node.body, Scope(parent=scope), returnType)
            lines.extend("    " + l for l in (bodyLines if bodyLines else ["pass"]))
            return lines

        elif isinstance(node, ForStatement):
            loopScope = Scope(parent=scope)
            lines = []
            if node.init:
                lines.extend(self.compileStmt(node.init, loopScope, returnType))
            cond = self.compileExpr(node.condition, loopScope)
            lines.append(f"while {cond}:")
            bodyLines = self.compileBlock(
                node.body, Scope(parent=loopScope), returnType
            )
            if node.update:
                bodyLines.extend(self.compileStmt(node.update, loopScope, returnType))
            lines.extend("    " + l for l in (bodyLines if bodyLines else ["pass"]))
            return lines

        elif isinstance(node, BreakStatement):
            return ["break"]

        elif isinstance(node, RaiseStatement):
            msg = self.compileExpr(node.message, scope)
            return [f"raise _RuntimeError({msg})"]

        elif isinstance(node, ExpressionStatement):
            return [self.compileExpr(node.expression, scope)]

        else:
            err(f"unknown statement node: {type(node)}")

    def compileInc(self, node, scope):
        target = node.target
        op = node.op
        sign = "+" if op == "++" else "-"

        if isinstance(target, Identifier):
            sym = scope.lookup(target.name)
            if sym == None:
                err(f"undefined variable '{target.name}'", node.line)
            if not sym.mutable:
                err(
                    f"'{target.name}' is immutable — declare with 'mut' to use {op}",
                    node.line,
                )
            if sym.type_ not in ("int", "float"):
                err(
                    f"'{op}' can only be used on int or float, not '{sym.type_}'",
                    node.line,
                )
            return [f"{target.name} = ({target.name} {sign} 1)"]

        elif isinstance(target, DotExpression):
            obj = self.compileExpr(target.obj, scope)
            return [f"{obj}.{target.member} = ({obj}.{target.member} {sign} 1)"]

        elif isinstance(target, IndexExpression):
            tExpr = self.compileExpr(target.target, scope)
            idx = self.compileExpr(target.index, scope)
            return [f"{tExpr}[{idx}] = ({tExpr}[{idx}] {sign} 1)"]

        else:
            err(f"invalid target for {op}", node.line)

    def compileAssignment(self, node, scope):
        target = node.target

        if isinstance(target, Identifier):
            sym = scope.lookup(target.name)
            if sym == None:
                err(f"undefined variable '{target.name}'", node.line)
            if not sym.mutable:
                err(
                    f"'{target.name}' is immutable — declare with 'mut' to reassign",
                    node.line,
                )
            val = self.compileExpr(node.value, scope)
            if sym.type_ in NC_TYPES and not isinstance(node.value, NullLiteral):
                return [
                    f"{target.name} = _typecheck({val}, '{sym.type_}', 'line {node.line}')"
                ]
            return [f"{target.name} = {val}"]

        elif isinstance(target, IndexExpression):
            base = target.target
            if isinstance(base, Identifier):
                sym = scope.lookup(base.name)
                if sym and not sym.mutable:
                    err(f"cannot mutate immutable array '{base.name}'", node.line)
            tExpr = self.compileExpr(target.target, scope)
            idx = self.compileExpr(target.index, scope)
            val = self.compileExpr(node.value, scope)
            return [f"_arrset({tExpr}, {idx}, {val})"]

        elif isinstance(target, DotExpression):
            if isinstance(target.obj, Identifier):
                modName = target.obj.name
                if modName in self.moduleExports:
                    err(
                        f"cannot directly mutate '{target.member}' on module '{modName}' — use an exported function",
                        node.line,
                    )
            obj = self.compileExpr(target.obj, scope)
            val = self.compileExpr(node.value, scope)
            return [f"{obj}.{target.member} = {val}"]

        else:
            err(f"invalid assignment target", node.line)

    def compileExpr(self, node, scope):
        if isinstance(node, IntegerLiteral):
            return str(node.value)

        elif isinstance(node, FloatLiteral):
            return str(node.value)

        elif isinstance(node, StringLiteral):
            return repr(node.value)

        elif isinstance(node, BoolLiteral):
            return "True" if node.value else "False"

        elif isinstance(node, NullLiteral):
            return "None"

        elif isinstance(node, ThisExpression):
            return "self"

        elif isinstance(node, ArrayLiteral):
            elems = ", ".join(self.compileExpr(e, scope) for e in node.elements)
            return f"[{elems}]"

        elif isinstance(node, NewExpression):
            if node.className in self.moduleExports:
                err(
                    f"'{node.className}' is a module and cannot be instantiated — only types can",
                    node.line,
                )
            if node.className not in self.knownTypes:
                err(f"unknown type '{node.className}'", node.line)
            args = ", ".join(self.compileExpr(a, scope) for a in node.args)
            return f"{node.className}({args})"

        elif isinstance(node, Identifier):
            name = node.name
            sym = scope.lookup(name)
            if sym == None:
                if name in self.moduleExports or name == "io":
                    return name
                err(f"undefined identifier '{name}'", node.line)
            return name

        elif isinstance(node, DotExpression):
            obj = self.compileExpr(node.obj, scope)
            member = node.member
            objName = node.obj.name if isinstance(node.obj, Identifier) else None
            if objName and objName in self.moduleExports:
                if member not in self.moduleExports[objName] and member != "_exports":
                    err(
                        f"'{member}' is not exported by module '{objName}' — exported: {sorted(self.moduleExports[objName])}",
                        node.line,
                    )
            if member == "length":
                return f"len({obj})"
            return f"{obj}.{member}"

        elif isinstance(node, IndexExpression):
            target = self.compileExpr(node.target, scope)
            idx = self.compileExpr(node.index, scope)
            return f"_arrget({target}, {idx})"

        elif isinstance(node, BinaryExpression):
            left = self.compileExpr(node.left, scope)
            right = self.compileExpr(node.right, scope)
            op = node.operator
            if op == "/":
                return f"_div({left}, {right})"
            if op == "+":
                return f"_add({left}, {right}, 'line {node.line}')"
            if op == "||":
                return f"({left} or {right})"
            if op == "&&":
                return f"({left} and {right})"
            return f"({left} {op} {right})"

        elif isinstance(node, UnaryExpression):
            operand = self.compileExpr(node.operand, scope)
            op = node.operator
            if op == "!":
                return f"(not {operand})"
            elif op == "-":
                return f"(-{operand})"
            elif op == "~":
                return f"(~{operand})"
            return f"({op}{operand})"

        elif isinstance(node, CallExpression):
            return self.compileCall(node, scope)

        else:
            err(f"unknown expression node: {type(node)}")

    def compileCall(self, node, scope):
        args = ", ".join(self.compileExpr(a, scope) for a in node.args)

        if isinstance(node.callee, DotExpression):
            obj = self.compileExpr(node.callee.obj, scope)
            member = node.callee.member

            if obj == "io":
                if member in ("out", "outln", "input"):
                    return f"io.{member}({args})"
                err(f"io has no member '{member}'", node.line)

            objName = (
                node.callee.obj.name
                if isinstance(node.callee.obj, Identifier)
                else None
            )
            if objName and objName in self.moduleExports:
                if member not in self.moduleExports[objName]:
                    err(f"'{member}' is not exported by module '{objName}'", node.line)
            return f"{obj}.{member}({args})"

        elif isinstance(node.callee, Identifier):
            name = node.callee.name
            sym = scope.lookup(name)
            if sym == None and self.currentModule != None:
                return f"self.{name}({args})"
            return f"{name}({args})"

        else:
            callee = self.compileExpr(node.callee, scope)
            return f"{callee}({args})"

    def compileEntry(self):
        if "main" in self.moduleExports and "main" in self.moduleExports["main"]:
            return "main.main()\n"
        return ""
