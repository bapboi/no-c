import sys
from lexer import (
    Lexer,
    TT_INT,
    TT_FLOAT,
    TT_STRING,
    TT_IDENTIFIER,
    TT_KEYWORD,
    TT_PLUS,
    TT_MINUS,
    TT_MULT,
    TT_DIV,
    TT_LPAREN,
    TT_RPAREN,
    TT_LBRACE,
    TT_RBRACE,
    TT_SEMI,
    TT_COMMA,
    TT_EQ,
    TT_EOF,
)


class Node:
    def to_tree(self, indent=0):
        spaces = "  " * indent
        result = f"{spaces}{self.__class__.__name__}"
        for value in self.__dict__.values():
            if isinstance(value, Node):
                result += "\n" + value.to_tree(indent + 1)
            elif isinstance(value, list):
                for v in value:
                    if isinstance(v, Node):
                        result += "\n" + v.to_tree(indent + 1)
                    else:
                        result += f"\n{'  ' * (indent + 1)}{v}"
            else:
                if value is not None:
                    result += f"\n{'  ' * (indent + 1)}{value}"
        return result


class Program(Node):
    def __init__(self, statements):
        self.statements = statements

    def node_label(self):
        return "Program"


class AssignmentStatement(Node):
    def __init__(self, identifier, value):
        self.identifier = identifier
        self.value = value


class PrintStatement(Node):
    def __init__(self, value):
        self.value = value


class ExpressionStatement(Node):
    def __init__(self, expression):
        self.expression = expression


class BinaryExpression(Node):
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right


class CallExpression(Node):
    def __init__(self, callee, args):
        self.callee = callee
        self.args = args


class IntegerLiteral(Node):
    def __init__(self, value):
        self.value = value

    def node_label(self):
        return f"IntegerLiteral({self.value})"


class FloatLiteral(Node):
    def __init__(self, value):
        self.value = value


class StringLiteral(Node):
    def __init__(self, value):
        self.value = value


class Identifier(Node):
    def __init__(self, name):
        self.name = name


class FunctionDeclaration(Node):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

    def node_label(self):
        return f"FunctionDeclaration({self.name.name})"


class ReturnStatement(Node):
    def __init__(self, value):
        self.value = value

    def node_label(self):
        return f"ReturnStatement"


class ConditionalStatement(Node):
    def __init__(self, condition, then_body, else_body=None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body


class BlockStatement(Node):
    def __init__(self, statements):
        self.statements = statements


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def peek(self):
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return None

    def eat(self, type_):
        token = self.current()
        if token is None:
            raise Exception(f"Unexpected EOF, expected {type_}")
        if token.type == type_:
            self.pos += 1
            return token
        else:
            raise Exception(f"Expected token {type_}, got {token.type}")

    def semiHelper(self):
        self.eat(TT_SEMI)

    def parse(self):
        statements = []
        while self.current() and self.current().type != TT_EOF:
            statements.append(self.parse_statement())
        return Program(statements)

    def parse_statement(self):
        token = self.current()
        if token.type == TT_KEYWORD:
            if token.value == "print":
                return self.parse_print()
            elif token.value == "return":
                return self.parse_return()
            elif token.value == "if":
                return self.parse_if()
            elif token.value == "while":
                return self.parse_while()
            elif token.value == "fn":
                return self.parse_function()
            else:
                raise Exception(f"Unknown keyword {token.value}")
        elif token.type == TT_IDENTIFIER:
            next_token = self.peek()
            if next_token and next_token.type == TT_EQ:
                return self.parse_assignment()
            else:
                expr = self.parse_expression()
                self.semiHelper()
                return ExpressionStatement(expr)
        elif token.type in (TT_INT, TT_FLOAT, TT_STRING, TT_LPAREN):
            expr = self.parse_expression()
            return ExpressionStatement(expr)
        elif token.type == TT_SEMI:
            self.eat(TT_SEMI)
            return None
        else:
            raise Exception(f"Unknown statement starting with {token.type}")

    def parse_assignment(self):
        identifier = Identifier(self.eat(TT_IDENTIFIER).value)
        self.eat(TT_EQ)
        expr = self.parse_expression()
        return AssignmentStatement(identifier, expr)

    def parse_print(self):
        self.eat(TT_KEYWORD)
        self.eat(TT_LPAREN)
        expr = self.parse_expression()
        self.eat(TT_RPAREN)
        self.semiHelper()
        return PrintStatement(expr)

    def parse_return(self):
        self.eat(TT_KEYWORD)
        expr = self.parse_expression()
        self.semiHelper()
        return ReturnStatement(expr)

    def parse_function(self):
        self.eat(TT_KEYWORD)
        name = self.eat(TT_IDENTIFIER)
        name = Identifier(name.value)
        self.eat(TT_LPAREN)
        params = []
        if self.current().type != TT_RPAREN:
            val = self.eat(TT_IDENTIFIER)
            params.append(Identifier(val.value))
            while self.current().type == TT_COMMA:
                self.eat(TT_COMMA)
                val = self.eat(TT_IDENTIFIER)
                params.append(Identifier(val.value))
        self.eat(TT_RPAREN)
        body = self.parse_block()
        return FunctionDeclaration(name, params, body.statements)

    def parse_block(self):
        self.eat(TT_LBRACE)
        statements = []
        while self.current() and self.current().type != TT_RBRACE:
            if self.current().type == TT_EOF:
                raise Exception("Unexpected EOF: missing }")
            statement = self.parse_statement()
            if statement is not None:
                statements.append(statement)

        self.eat(TT_RBRACE)
        return BlockStatement(statements)

    def parse_expression(self):
        left = self.parse_term()
        while self.current() and self.current().type in (TT_PLUS, TT_MINUS):
            op = self.eat(self.current().type).type
            left = BinaryExpression(op, left, self.parse_term())
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.current() and self.current().type in (TT_MULT, TT_DIV):
            op = self.eat(self.current().type).type
            left = BinaryExpression(op, left, self.parse_factor())
        return left

    def parse_factor(self):
        token = self.current()
        if token.type == TT_INT:
            self.eat(TT_INT)
            return IntegerLiteral(token.value)
        elif token.type == TT_FLOAT:
            self.eat(TT_FLOAT)
            return FloatLiteral(token.value)
        elif token.type == TT_STRING:
            self.eat(TT_STRING)
            return StringLiteral(token.value)
        elif token.type == TT_IDENTIFIER:
            tokenid = self.eat(TT_IDENTIFIER)
            identifier = Identifier(tokenid.value)
            if self.current() and self.current().type == TT_LPAREN:
                return self.callfinish(identifier)
            return identifier
        elif token.type == TT_LPAREN:
            self.eat(TT_LPAREN)
            expr = self.parse_expression()
            self.eat(TT_RPAREN)
            return expr
        else:
            raise Exception(f"Unexpected token {token.type}")

    def callfinish(self, callee):
        self.eat(TT_LPAREN)
        args = []
        if self.current().type != TT_RPAREN:
            args.append(self.parse_expression())
            while self.current().type == TT_COMMA:
                self.eat(TT_COMMA)
                args.append(self.parse_expression())
        self.eat(TT_RPAREN)
        return CallExpression(callee, args)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 parser.py <filename>")
        sys.exit(1)

    file_path = sys.argv[1]
    try:
        with open(file_path, "r") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"File '{file_path}' not found")
        sys.exit(1)

    lexer = Lexer(source)
    tokens, error = lexer.createTokens()
    if error:
        print(error.as_string())
        sys.exit(1)

    parser = Parser(tokens)
    try:
        ast = parser.parse()
    except Exception as e:
        print(f"Parse error: {e}")
        sys.exit(1)

    print(ast.to_tree())


if __name__ == "__main__":
    main()
