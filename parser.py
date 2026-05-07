import sys
from lexer import (
    Lexer,
    TT_INT,
    TT_FLOAT,
    TT_STRING,
    TT_BOOL,
    TT_IDENTIFIER,
    TT_KEYWORD,
    TT_TYPE,
    TT_PLUS,
    TT_MINUS,
    TT_MULT,
    TT_DIV,
    TT_MOD,
    TT_INC,
    TT_DEC,
    TT_EQEQ,
    TT_NEQ,
    TT_LT,
    TT_GT,
    TT_LTE,
    TT_GTE,
    TT_AND,
    TT_OR,
    TT_NOT,
    TT_TILDE,
    TT_AMP,
    TT_PIPE,
    TT_CARET,
    TT_EQ,
    TT_LPAREN,
    TT_RPAREN,
    TT_LBRACE,
    TT_RBRACE,
    TT_LBRACKET,
    TT_RBRACKET,
    TT_COMMA,
    TT_SEMI,
    TT_DOT,
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
                if value != None:
                    result += f"\n{'  ' * (indent + 1)}{value}"
        return result


class Program(Node):
    def __init__(self, imports, modules):
        self.imports = imports
        self.modules = modules


class ImportStatement(Node):
    def __init__(self, name):
        self.name = name


class ModuleDeclaration(Node):
    def __init__(self, name, exports, body):
        self.name = name
        self.exports = exports
        self.body = body


class TypeDeclaration(Node):
    def __init__(self, name, fields, methods, line=None):
        self.name = name
        self.fields = fields  # list of (type_, name, defaultValue)
        self.methods = methods  # list of FunctionDeclaration
        self.line = line


class FunctionDeclaration(Node):
    def __init__(self, returnType, name, params, body, line=None):
        self.returnType = returnType
        self.name = name
        self.params = params
        self.body = body
        self.line = line


class VarDeclaration(Node):
    def __init__(self, mutable, type_, name, value, line=None):
        self.mutable = mutable
        self.type_ = type_
        self.name = name
        self.value = value
        self.line = line


class ArrayDeclaration(Node):
    def __init__(self, mutable, elemType, name, value, line=None):
        self.mutable = mutable
        self.elemType = elemType
        self.name = name
        self.value = value
        self.line = line


class AssignmentStatement(Node):
    def __init__(self, target, value, line=None):
        self.target = target
        self.value = value
        self.line = line


class IncStatement(Node):
    def __init__(self, target, op, line=None):
        self.target = target  # Identifier or DotExpression or IndexExpression
        self.op = op  # "++" or "--"
        self.line = line


class ReturnStatement(Node):
    def __init__(self, value, line=None):
        self.value = value
        self.line = line


class IfStatement(Node):
    def __init__(self, condition, thenBody, elseBody=None, line=None):
        self.condition = condition
        self.thenBody = thenBody
        self.elseBody = elseBody
        self.line = line


class WhileStatement(Node):
    def __init__(self, condition, body, line=None):
        self.condition = condition
        self.body = body
        self.line = line


class ForStatement(Node):
    def __init__(self, init, condition, update, body, line=None):
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body
        self.line = line


class BreakStatement(Node):
    def __init__(self, line=None):
        self.line = line


class RaiseStatement(Node):
    def __init__(self, message, line=None):
        self.message = message
        self.line = line


class ExpressionStatement(Node):
    def __init__(self, expression, line=None):
        self.expression = expression
        self.line = line


class BinaryExpression(Node):
    def __init__(self, operator, left, right, line=None):
        self.operator = operator
        self.left = left
        self.right = right
        self.line = line


class UnaryExpression(Node):
    def __init__(self, operator, operand, postfix=False, line=None):
        self.operator = operator
        self.operand = operand
        self.postfix = postfix
        self.line = line


class CallExpression(Node):
    def __init__(self, callee, args, line=None):
        self.callee = callee
        self.args = args
        self.line = line


class NewExpression(Node):
    def __init__(self, className, args, line=None):
        self.className = className
        self.args = args
        self.line = line


class IndexExpression(Node):
    def __init__(self, target, index, line=None):
        self.target = target
        self.index = index
        self.line = line


class DotExpression(Node):
    def __init__(self, obj, member, line=None):
        self.obj = obj
        self.member = member
        self.line = line


class ArrayLiteral(Node):
    def __init__(self, elements, line=None):
        self.elements = elements
        self.line = line


class IntegerLiteral(Node):
    def __init__(self, value, line=None):
        self.value = value
        self.line = line


class FloatLiteral(Node):
    def __init__(self, value, line=None):
        self.value = value
        self.line = line


class StringLiteral(Node):
    def __init__(self, value, line=None):
        self.value = value
        self.line = line


class BoolLiteral(Node):
    def __init__(self, value, line=None):
        self.value = value
        self.line = line


class NullLiteral(Node):
    def __init__(self, line=None):
        self.line = line


class ThisExpression(Node):
    def __init__(self, line=None):
        self.line = line


class Identifier(Node):
    def __init__(self, name, line=None):
        self.name = name
        self.line = line


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

    def line(self):
        t = self.current()
        return t.line if t else 0

    def eat(self, type_):
        token = self.current()
        if token == None:
            raise Exception(f"line {self.line()}: unexpected EOF, expected {type_}")
        if token.type == type_:
            self.pos += 1
            return token
        else:
            raise Exception(f"line {token.line}: expected {type_}, got {token.type}")

    def eatKeyword(self, value):
        token = self.current()
        if token == None or token.type != TT_KEYWORD or token.value != value:
            got = token.value if token else "EOF"
            ln = token.line if token else "?"
            raise Exception(f"line {ln}: expected keyword '{value}', got '{got}'")
        self.pos += 1
        return token

    def eatType(self):
        token = self.current()
        if token == None or token.type != TT_TYPE:
            ln = token.line if token else "?"
            raise Exception(
                f"line {ln}: expected a type, got {token.type if token else 'EOF'}"
            )
        self.pos += 1
        return token.value

    def eatTypeOrClass(self):
        token = self.current()
        if token == None:
            raise Exception(f"line ?: expected a type")
        if token.type == TT_TYPE:
            self.pos += 1
            return token.value
        if token.type == TT_IDENTIFIER:
            self.pos += 1
            return token.value
        raise Exception(
            f"line {token.line}: expected a type or type name, got {token.type}"
        )

    def semiHelper(self):
        self.eat(TT_SEMI)

    def parse(self):
        imports = []
        modules = []
        while self.current() and self.current().type != TT_EOF:
            token = self.current()
            if token.type == TT_KEYWORD and token.value == "import":
                imports.append(self.parseImport())
            elif token.type == TT_KEYWORD and token.value == "module":
                modules.append(self.parseModule())
            else:
                raise Exception(
                    f"line {token.line}: top-level must be 'import' or 'module', got '{token.value}'"
                )
        return Program(imports, modules)

    def parseImport(self):
        self.eatKeyword("import")
        name = self.eat(TT_IDENTIFIER).value
        self.semiHelper()
        return ImportStatement(name)

    def parseModule(self):
        self.eatKeyword("module")
        name = self.eat(TT_IDENTIFIER).value
        self.eat(TT_LBRACE)

        exports = []
        body = []

        while self.current() and self.current().type != TT_RBRACE:
            token = self.current()
            if token.type == TT_KEYWORD and token.value == "export":
                exports = self.parseExportBlock()
            elif token.type == TT_KEYWORD and token.value == "fn":
                body.append(self.parseFunction())
            elif token.type == TT_KEYWORD and token.value == "type":
                body.append(self.parseType())
            elif token.type == TT_KEYWORD and token.value == "mut":
                body.append(self.parseVarOrArray(True))
            elif token.type == TT_TYPE:
                body.append(self.parseVarOrArray(False))
            else:
                raise Exception(
                    f"line {token.line}: unexpected token in module body: '{token.value}'"
                )

        self.eat(TT_RBRACE)
        return ModuleDeclaration(name, exports, body)

    def parseExportBlock(self):
        self.eatKeyword("export")
        self.eat(TT_LBRACE)
        names = []
        if self.current().type != TT_RBRACE:
            names.append(self.eat(TT_IDENTIFIER).value)
            while self.current().type == TT_COMMA:
                self.eat(TT_COMMA)
                names.append(self.eat(TT_IDENTIFIER).value)
        self.eat(TT_RBRACE)
        return names

    def parseType(self):
        ln = self.line()
        self.eatKeyword("type")
        name = self.eat(TT_IDENTIFIER).value
        self.eat(TT_LBRACE)

        fields = []
        methods = []

        while self.current() and self.current().type != TT_RBRACE:
            token = self.current()
            if token.type == TT_KEYWORD and token.value == "fn":
                methods.append(self.parseFunction())
            elif token.type == TT_KEYWORD and token.value == "mut":
                fields.append(self.parseField(True))
            elif token.type == TT_TYPE or token.type == TT_IDENTIFIER:
                fields.append(self.parseField(False))
            else:
                raise Exception(
                    f"line {token.line}: unexpected token in class body: '{token.value}'"
                )

        self.eat(TT_RBRACE)
        return TypeDeclaration(name, fields, methods, ln)

    def parseField(self, mutable):
        if mutable:
            self.eatKeyword("mut")
        ln = self.line()
        type_ = self.eatTypeOrClass()
        isArray = False
        if self.current().type == TT_LBRACKET:
            self.eat(TT_LBRACKET)
            self.eat(TT_RBRACKET)
            isArray = True
        name = self.eat(TT_IDENTIFIER).value
        default = None
        if self.current().type == TT_EQ:
            self.eat(TT_EQ)
            default = self.parseExpression()
        self.semiHelper()
        return (mutable, type_ + ("[]" if isArray else ""), name, default, ln)

    def parseFunction(self):
        ln = self.line()
        self.eatKeyword("fn")
        returnType = self.eatTypeOrClass()
        name = self.eat(TT_IDENTIFIER).value
        self.eat(TT_LPAREN)
        params = []
        if self.current().type != TT_RPAREN:
            params.append(self.parseParam())
            while self.current().type == TT_COMMA:
                self.eat(TT_COMMA)
                params.append(self.parseParam())
        self.eat(TT_RPAREN)
        body = self.parseBlock()
        return FunctionDeclaration(returnType, name, params, body, ln)

    def parseParam(self):
        mutable = False
        if self.current().type == TT_KEYWORD and self.current().value == "mut":
            self.eatKeyword("mut")
            mutable = True
        type_ = self.eatTypeOrClass()
        isArray = False
        if self.current().type == TT_LBRACKET:
            self.eat(TT_LBRACKET)
            self.eat(TT_RBRACKET)
            isArray = True
        name = self.eat(TT_IDENTIFIER).value
        return (mutable, type_ + ("[]" if isArray else ""), name)

    def parseBlock(self):
        self.eat(TT_LBRACE)
        statements = []
        while self.current() and self.current().type != TT_RBRACE:
            if self.current().type == TT_EOF:
                raise Exception(f"line {self.line()}: unexpected EOF, missing }}")
            stmt = self.parseStatement()
            if stmt != None:
                statements.append(stmt)
        self.eat(TT_RBRACE)
        return statements

    def parseStatement(self):
        token = self.current()

        if token.type == TT_SEMI:
            self.eat(TT_SEMI)
            return None

        if token.type == TT_KEYWORD:
            if token.value == "return":
                return self.parseReturn()
            elif token.value == "if":
                return self.parseIf()
            elif token.value == "while":
                return self.parseWhile()
            elif token.value == "for":
                return self.parseFor()
            elif token.value == "break":
                ln = self.line()
                self.eatKeyword("break")
                self.semiHelper()
                return BreakStatement(ln)
            elif token.value == "raise":
                return self.parseRaise()
            elif token.value == "mut":
                return self.parseVarOrArray(True)
            elif token.value == "this" or token.value == "new":
                return self.parseIdentStatement()
            else:
                raise Exception(
                    f"line {token.line}: unknown keyword '{token.value}' in statement"
                )

        if token.type == TT_TYPE:
            return self.parseVarOrArray(False)

        # class-typed declaration: Identifier Identifier = ...
        if (
            token.type == TT_IDENTIFIER
            and self.peek()
            and self.peek().type == TT_IDENTIFIER
        ):
            return self.parseVarOrArray(False)

        if token.type in (TT_INC, TT_DEC):
            ln = token.line
            op = "++" if token.type == TT_INC else "--"
            self.pos += 1
            target = self.parsePostfix(self.parsePrimary())
            self.semiHelper()
            return IncStatement(target, op, ln)

        if token.type == TT_IDENTIFIER:
            return self.parseIdentStatement()

        if token.type == TT_KEYWORD and token.value == "this":
            return self.parseIdentStatement()

        expr = self.parseExpression()
        self.semiHelper()
        return ExpressionStatement(expr, token.line)

    def parseVarOrArray(self, mutable):
        if mutable:
            self.eatKeyword("mut")
        ln = self.line()
        type_ = self.eatTypeOrClass()
        isArray = False
        if self.current().type == TT_LBRACKET:
            self.eat(TT_LBRACKET)
            self.eat(TT_RBRACKET)
            isArray = True
        name = self.eat(TT_IDENTIFIER).value
        value = None
        if self.current().type == TT_EQ:
            self.eat(TT_EQ)
            value = self.parseArrayLiteral() if isArray else self.parseExpression()
        self.semiHelper()
        if isArray:
            return ArrayDeclaration(mutable, type_, name, value, ln)
        return VarDeclaration(mutable, type_, name, value, ln)

    def parseReturn(self):
        ln = self.line()
        self.eatKeyword("return")
        if self.current().type == TT_SEMI:
            self.semiHelper()
            return ReturnStatement(None, ln)
        expr = self.parseExpression()
        self.semiHelper()
        return ReturnStatement(expr, ln)

    def parseRaise(self):
        ln = self.line()
        self.eatKeyword("raise")
        msg = self.parseExpression()
        self.semiHelper()
        return RaiseStatement(msg, ln)

    def parseIf(self):
        ln = self.line()
        self.eatKeyword("if")
        self.eat(TT_LPAREN)
        condition = self.parseExpression()
        self.eat(TT_RPAREN)
        thenBody = self.parseBlock()
        elseBody = None
        if (
            self.current()
            and self.current().type == TT_KEYWORD
            and self.current().value == "else"
        ):
            self.eatKeyword("else")
            if self.current().type == TT_KEYWORD and self.current().value == "if":
                elseBody = [self.parseIf()]
            else:
                elseBody = self.parseBlock()
        return IfStatement(condition, thenBody, elseBody, ln)

    def parseWhile(self):
        ln = self.line()
        self.eatKeyword("while")
        self.eat(TT_LPAREN)
        condition = self.parseExpression()
        self.eat(TT_RPAREN)
        body = self.parseBlock()
        return WhileStatement(condition, body, ln)

    def parseFor(self):
        ln = self.line()
        self.eatKeyword("for")
        self.eat(TT_LPAREN)
        init = self.parseForInit()
        condition = self.parseExpression()
        self.eat(TT_SEMI)
        update = self.parseForUpdate()
        self.eat(TT_RPAREN)
        body = self.parseBlock()
        return ForStatement(init, condition, update, body, ln)

    def parseForInit(self):
        token = self.current()
        if token.type == TT_SEMI:
            self.eat(TT_SEMI)
            return None
        if token.type == TT_KEYWORD and token.value == "mut":
            self.eatKeyword("mut")
            ln = self.line()
            type_ = self.eatTypeOrClass()
            name = self.eat(TT_IDENTIFIER).value
            value = None
            if self.current().type == TT_EQ:
                self.eat(TT_EQ)
                value = self.parseExpression()
            self.eat(TT_SEMI)
            return VarDeclaration(True, type_, name, value, ln)
        if token.type == TT_TYPE:
            ln = self.line()
            type_ = self.eatTypeOrClass()
            name = self.eat(TT_IDENTIFIER).value
            value = None
            if self.current().type == TT_EQ:
                self.eat(TT_EQ)
                value = self.parseExpression()
            self.eat(TT_SEMI)
            return VarDeclaration(False, type_, name, value, ln)
        expr = self.parseExpression()
        if self.current().type == TT_EQ:
            ln = self.line()
            self.eat(TT_EQ)
            value = self.parseExpression()
            self.eat(TT_SEMI)
            return AssignmentStatement(expr, value, ln)
        self.eat(TT_SEMI)
        return ExpressionStatement(expr, token.line)

    def parseForUpdate(self):
        token = self.current()
        if token.type == TT_RPAREN:
            return None
        ln = token.line
        # prefix ++ / --
        if token.type in (TT_INC, TT_DEC):
            op = "++" if token.type == TT_INC else "--"
            self.pos += 1
            target = self.parsePrimary()
            return IncStatement(target, op, ln)
        expr = self.parsePostfix(self.parsePrimary())
        # postfix ++ / --
        if self.current() and self.current().type in (TT_INC, TT_DEC):
            op = "++" if self.current().type == TT_INC else "--"
            self.pos += 1
            return IncStatement(expr, op, ln)
        if self.current().type == TT_EQ:
            self.eat(TT_EQ)
            value = self.parseExpression()
            return AssignmentStatement(expr, value, ln)
        return ExpressionStatement(expr, ln)

    def parseIdentStatement(self):
        ln = self.line()
        expr = self.parsePostfix(self.parsePrimary())
        # postfix ++ / -- as a statement
        if self.current() and self.current().type in (TT_INC, TT_DEC):
            op = "++" if self.current().type == TT_INC else "--"
            self.pos += 1
            self.semiHelper()
            return IncStatement(expr, op, ln)
        if self.current().type == TT_EQ:
            self.eat(TT_EQ)
            value = self.parseExpression()
            self.semiHelper()
            return AssignmentStatement(expr, value, ln)
        self.semiHelper()
        return ExpressionStatement(expr, ln)

    def parseExpression(self):
        return self.parseOr()

    def parseOr(self):
        left = self.parseAnd()
        while self.current() and self.current().type == TT_OR:
            ln = self.line()
            self.eat(TT_OR)
            left = BinaryExpression("||", left, self.parseAnd(), ln)
        return left

    def parseAnd(self):
        left = self.parseEquality()
        while self.current() and self.current().type == TT_AND:
            ln = self.line()
            self.eat(TT_AND)
            left = BinaryExpression("&&", left, self.parseEquality(), ln)
        return left

    def parseEquality(self):
        left = self.parseComparison()
        while self.current() and self.current().type in (TT_EQEQ, TT_NEQ):
            ln = self.line()
            op = "==" if self.current().type == TT_EQEQ else "!="
            self.pos += 1
            left = BinaryExpression(op, left, self.parseComparison(), ln)
        return left

    def parseComparison(self):
        left = self.parseBitOr()
        ops = {TT_LT: "<", TT_GT: ">", TT_LTE: "<=", TT_GTE: ">="}
        while self.current() and self.current().type in ops:
            ln = self.line()
            op = ops[self.current().type]
            self.pos += 1
            left = BinaryExpression(op, left, self.parseBitOr(), ln)
        return left

    def parseBitOr(self):
        left = self.parseBitXor()
        while self.current() and self.current().type == TT_PIPE:
            ln = self.line()
            self.eat(TT_PIPE)
            left = BinaryExpression("|", left, self.parseBitXor(), ln)
        return left

    def parseBitXor(self):
        left = self.parseBitAnd()
        while self.current() and self.current().type == TT_CARET:
            ln = self.line()
            self.eat(TT_CARET)
            left = BinaryExpression("^", left, self.parseBitAnd(), ln)
        return left

    def parseBitAnd(self):
        left = self.parseAdditive()
        while self.current() and self.current().type == TT_AMP:
            ln = self.line()
            self.eat(TT_AMP)
            left = BinaryExpression("&", left, self.parseAdditive(), ln)
        return left

    def parseAdditive(self):
        left = self.parseTerm()
        while self.current() and self.current().type in (TT_PLUS, TT_MINUS):
            ln = self.line()
            op = "+" if self.current().type == TT_PLUS else "-"
            self.pos += 1
            left = BinaryExpression(op, left, self.parseTerm(), ln)
        return left

    def parseTerm(self):
        left = self.parseUnary()
        ops = {TT_MULT: "*", TT_DIV: "/", TT_MOD: "%"}
        while self.current() and self.current().type in ops:
            ln = self.line()
            op = ops[self.current().type]
            self.pos += 1
            left = BinaryExpression(op, left, self.parseUnary(), ln)
        return left

    def parseUnary(self):
        token = self.current()
        if token.type == TT_NOT:
            ln = self.line()
            self.eat(TT_NOT)
            return UnaryExpression("!", self.parseUnary(), False, ln)
        elif token.type == TT_MINUS:
            ln = self.line()
            self.eat(TT_MINUS)
            return UnaryExpression("-", self.parseUnary(), False, ln)
        elif token.type == TT_TILDE:
            ln = self.line()
            self.eat(TT_TILDE)
            return UnaryExpression("~", self.parseUnary(), False, ln)
        return self.parsePostfix(self.parsePrimary())

    def parsePostfix(self, node):
        while True:
            token = self.current()
            if token == None:
                break
            if token.type == TT_DOT:
                ln = token.line
                self.eat(TT_DOT)
                member = self.eat(TT_IDENTIFIER).value
                node = DotExpression(node, member, ln)
                if self.current() and self.current().type == TT_LPAREN:
                    node = self.callFinish(node, ln)
            elif token.type == TT_LBRACKET:
                ln = token.line
                self.eat(TT_LBRACKET)
                index = self.parseExpression()
                self.eat(TT_RBRACKET)
                node = IndexExpression(node, index, ln)
            elif token.type == TT_LPAREN and isinstance(
                node, (Identifier, DotExpression)
            ):
                node = self.callFinish(node, token.line)
            else:
                break
        return node

    def parsePrimary(self):
        token = self.current()
        if token == None:
            raise Exception(f"line ?: unexpected EOF in expression")
        ln = token.line
        if token.type == TT_INT:
            self.pos += 1
            return IntegerLiteral(token.value, ln)
        elif token.type == TT_FLOAT:
            self.pos += 1
            return FloatLiteral(token.value, ln)
        elif token.type == TT_STRING:
            self.pos += 1
            return StringLiteral(token.value, ln)
        elif token.type == TT_BOOL:
            self.pos += 1
            return BoolLiteral(token.value, ln)
        elif token.type == TT_TYPE and token.value == "null":
            self.pos += 1
            return NullLiteral(ln)
        elif token.type == TT_KEYWORD and token.value == "this":
            self.pos += 1
            return ThisExpression(ln)
        elif token.type == TT_KEYWORD and token.value == "new":
            return self.parseNew()
        elif token.type == TT_IDENTIFIER:
            self.pos += 1
            return Identifier(token.value, ln)
        elif token.type == TT_LPAREN:
            self.eat(TT_LPAREN)
            expr = self.parseExpression()
            self.eat(TT_RPAREN)
            return expr
        elif token.type == TT_LBRACKET:
            return self.parseArrayLiteral()
        else:
            raise Exception(f"line {ln}: unexpected token '{token.value}'")

    def parseNew(self):
        ln = self.line()
        self.eatKeyword("new")
        className = self.eat(TT_IDENTIFIER).value
        self.eat(TT_LPAREN)
        args = []
        if self.current().type != TT_RPAREN:
            args.append(self.parseExpression())
            while self.current().type == TT_COMMA:
                self.eat(TT_COMMA)
                args.append(self.parseExpression())
        self.eat(TT_RPAREN)
        return NewExpression(className, args, ln)

    def parseArrayLiteral(self):
        ln = self.line()
        self.eat(TT_LBRACKET)
        elements = []
        if self.current().type != TT_RBRACKET:
            elements.append(self.parseExpression())
            while self.current().type == TT_COMMA:
                self.eat(TT_COMMA)
                elements.append(self.parseExpression())
        self.eat(TT_RBRACKET)
        return ArrayLiteral(elements, ln)

    def callFinish(self, callee, ln):
        self.eat(TT_LPAREN)
        args = []
        if self.current().type != TT_RPAREN:
            args.append(self.parseExpression())
            while self.current().type == TT_COMMA:
                self.eat(TT_COMMA)
                args.append(self.parseExpression())
        self.eat(TT_RPAREN)
        return CallExpression(callee, args, ln)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 parser.py <filename>")
        sys.exit(1)
    file_path = sys.argv[1]

    try:
        with open(file_path, "r") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"file '{file_path}' not found")
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
        print(f"parse error: {e}")
        sys.exit(1)

    print(ast.to_tree())


if __name__ == "__main__":
    main()
