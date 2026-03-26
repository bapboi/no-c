# compiler.py

from parser import (
    Program,
    AssignmentStatement,
    PrintStatement,
    ExpressionStatement,
    BinaryExpression,
    IntegerLiteral,
    FloatLiteral,
    StringLiteral,
    Identifier,
    FunctionDeclaration,
    ReturnStatement,
    CallExpression,
)


class Compiler:
    def __init__(self, ast):
        self.ast = ast

    def compile_and_run(self):
        """Compile AST to Python code and execute it"""
        python_code = self.compile_node(self.ast)
        local_scope = {}
        exec(python_code, {}, local_scope)
        return local_scope

    def compile_node(self, node):
        """Convert AST node to Python code string"""
        if isinstance(node, Program):
            return "\n".join(self.compile_node(stmt) for stmt in node.statements)
        elif isinstance(node, AssignmentStatement):
            return f"{self.compile_node(node.identifier)} = {self.compile_node(node.value)}"
        elif isinstance(node, PrintStatement):
            return f"print({self.compile_node(node.value)})"
        elif isinstance(node, ExpressionStatement):
            return self.compile_node(node.expression)
        elif isinstance(node, BinaryExpression):
            left = self.compile_node(node.left)
            right = self.compile_node(node.right)
            op = (
                node.operator.replace("PLUS", "+")
                .replace("MINUS", "-")
                .replace("MULT", "*")
                .replace("DIV", "/")
            )
            return f"({left} {op} {right})"
        elif isinstance(node, FunctionDeclaration):
            params = ", ".join(param.name for param in node.params)
            bodylines = [self.compile_node(statement) for statement in node.body]
            body = "\n".join("\t" + line for line in bodylines)
            return f"def {node.name.name}({params}):\n{body}"
        elif isinstance(node, ReturnStatement):
            return f"return {self.compile_node(node.value)}"
        elif isinstance(node, CallExpression):
            args = ", ".join(self.compile_node(arg) for arg in node.args)
            return f"{node.callee.name}({args})"
        elif isinstance(node, IntegerLiteral):
            return str(node.value)
        elif isinstance(node, FloatLiteral):
            return str(node.value)
        elif isinstance(node, StringLiteral):
            return repr(node.value)
        elif isinstance(node, Identifier):
            return node.name
        else:
            raise Exception(f"Unknown node type: {type(node)}")
