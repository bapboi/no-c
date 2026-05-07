import sys

TT_INT = "INT"
TT_FLOAT = "FLOAT"
TT_STRING = "STRING"
TT_BOOL = "BOOL"

TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MULT = "MULT"
TT_DIV = "DIV"
TT_MOD = "MOD"
TT_INC = "INC"
TT_DEC = "DEC"

TT_EQEQ = "EQEQ"
TT_NEQ = "NEQ"
TT_LT = "LT"
TT_GT = "GT"
TT_LTE = "LTE"
TT_GTE = "GTE"

TT_AND = "AND"
TT_OR = "OR"
TT_NOT = "NOT"
TT_AMP = "AMP"
TT_PIPE = "PIPE"
TT_CARET = "CARET"
TT_TILDE = "TILDE"

TT_EQ = "EQUALS"
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_LBRACE = "LBRACE"
TT_RBRACE = "RBRACE"
TT_LBRACKET = "LBRACKET"
TT_RBRACKET = "RBRACKET"
TT_COMMA = "COMMA"
TT_SEMI = "SEMI"
TT_DOT = "DOT"

TT_IDENTIFIER = "IDENTIFIER"
TT_KEYWORD = "KEYWORD"
TT_TYPE = "TYPE"

TT_EOF = "EOF"
NUM = "0123456789"

KEYWORDS = [
    "fn",
    "return",
    "if",
    "else",
    "while",
    "for",
    "break",
    "raise",
    "mut",
    "module",
    "import",
    "export",
    "true",
    "false",
    "type",
    "new",
    "this",
]

TYPES = [
    "int",
    "float",
    "String",
    "bool",
    "char",
    "void",
    "null",
]


class Token:
    def __init__(self, type_, value=None, line=1):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        if self.value != None:
            return f"{self.type}:{self.value}"
        return f"{self.type}"


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = -1
        self.line = 1
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos += 1
        if self.pos < len(self.text):
            if self.text[self.pos] == "\n":
                self.line += 1
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def peekChar(self):
        nxt = self.pos + 1
        return self.text[nxt] if nxt < len(self.text) else None

    def tok(self, type_, value=None):
        return Token(type_, value, self.line)

    def createTokens(self):
        tokens = []
        while self.current_char != None:
            if self.current_char in " \t\n\r":
                self.advance()
            elif self.current_char == "/" and self.peekChar() == "/":
                self.skipComment()
            elif self.current_char in NUM:
                tokens.append(self.makeNum())
            elif self.current_char.isalpha() or self.current_char == "_":
                tokens.append(self.makeIdent())
            elif self.current_char == '"':
                tokens.append(self.makeString())
            elif self.current_char == "'":
                tokens.append(self.makeChar())
            elif self.current_char == "+":
                if self.peekChar() == "+":
                    tokens.append(self.tok(TT_INC))
                    self.advance()
                else:
                    tokens.append(self.tok(TT_PLUS))
                self.advance()
            elif self.current_char == "-":
                if self.peekChar() == "-":
                    tokens.append(self.tok(TT_DEC))
                    self.advance()
                else:
                    tokens.append(self.tok(TT_MINUS))
                self.advance()
            elif self.current_char == "*":
                tokens.append(self.tok(TT_MULT))
                self.advance()
            elif self.current_char == "/":
                tokens.append(self.tok(TT_DIV))
                self.advance()
            elif self.current_char == "%":
                tokens.append(self.tok(TT_MOD))
                self.advance()
            elif self.current_char == "=":
                if self.peekChar() == "=":
                    tokens.append(self.tok(TT_EQEQ))
                    self.advance()
                else:
                    tokens.append(self.tok(TT_EQ))
                self.advance()
            elif self.current_char == "!":
                if self.peekChar() == "=":
                    tokens.append(self.tok(TT_NEQ))
                    self.advance()
                else:
                    tokens.append(self.tok(TT_NOT))
                self.advance()
            elif self.current_char == "<":
                if self.peekChar() == "=":
                    tokens.append(self.tok(TT_LTE))
                    self.advance()
                else:
                    tokens.append(self.tok(TT_LT))
                self.advance()
            elif self.current_char == ">":
                if self.peekChar() == "=":
                    tokens.append(self.tok(TT_GTE))
                    self.advance()
                else:
                    tokens.append(self.tok(TT_GT))
                self.advance()
            elif self.current_char == "&":
                if self.peekChar() == "&":
                    tokens.append(self.tok(TT_AND))
                    self.advance()
                else:
                    tokens.append(self.tok(TT_AMP))
                self.advance()
            elif self.current_char == "|":
                if self.peekChar() == "|":
                    tokens.append(self.tok(TT_OR))
                    self.advance()
                else:
                    tokens.append(self.tok(TT_PIPE))
                self.advance()
            elif self.current_char == "^":
                tokens.append(self.tok(TT_CARET))
                self.advance()
            elif self.current_char == "~":
                tokens.append(self.tok(TT_TILDE))
                self.advance()
            elif self.current_char == "(":
                tokens.append(self.tok(TT_LPAREN))
                self.advance()
            elif self.current_char == ")":
                tokens.append(self.tok(TT_RPAREN))
                self.advance()
            elif self.current_char == "{":
                tokens.append(self.tok(TT_LBRACE))
                self.advance()
            elif self.current_char == "}":
                tokens.append(self.tok(TT_RBRACE))
                self.advance()
            elif self.current_char == "[":
                tokens.append(self.tok(TT_LBRACKET))
                self.advance()
            elif self.current_char == "]":
                tokens.append(self.tok(TT_RBRACKET))
                self.advance()
            elif self.current_char == ",":
                tokens.append(self.tok(TT_COMMA))
                self.advance()
            elif self.current_char == ";":
                tokens.append(self.tok(TT_SEMI))
                self.advance()
            elif self.current_char == ".":
                tokens.append(self.tok(TT_DOT))
                self.advance()
            else:
                char = self.current_char
                line = self.line
                self.advance()
                return [], IllegalCharacterError("'" + char + "'", line)
        tokens.append(self.tok(TT_EOF))
        return tokens, None

    def skipComment(self):
        while self.current_char != None and self.current_char != "\n":
            self.advance()

    def makeNum(self):
        num_str = ""
        dotcount = 0
        line = self.line
        while self.current_char != None and self.current_char in NUM + ".":
            if self.current_char == ".":
                if dotcount == 1:
                    break
                dotcount += 1
                num_str += "."
            else:
                num_str += self.current_char
            self.advance()

        if dotcount == 0:
            return Token(TT_INT, int(num_str), line)
        else:
            return Token(TT_FLOAT, float(num_str), line)

    def makeIdent(self):
        id_str = ""
        line = self.line
        while self.current_char != None and (
            self.current_char.isalnum() or self.current_char == "_"
        ):
            id_str += self.current_char
            self.advance()

        if id_str == "true":
            return Token(TT_BOOL, True, line)
        elif id_str == "false":
            return Token(TT_BOOL, False, line)
        elif id_str in KEYWORDS:
            return Token(TT_KEYWORD, id_str, line)
        elif id_str in TYPES:
            return Token(TT_TYPE, id_str, line)
        else:
            return Token(TT_IDENTIFIER, id_str, line)

    def makeString(self):
        string = ""
        line = self.line
        self.advance()
        while self.current_char != None and self.current_char != '"':
            if self.current_char == "\\":
                self.advance()
                escapes = {"n": "\n", "t": "\t", "\\": "\\", '"': '"'}
                string += escapes.get(self.current_char, self.current_char)
            else:
                string += self.current_char
            self.advance()
        self.advance()
        return Token(TT_STRING, string, line)

    def makeChar(self):
        line = self.line
        self.advance()
        ch = self.current_char
        self.advance()
        if self.current_char == "'":
            self.advance()
        return Token(TT_STRING, ch, line)


class Error:
    def __init__(self, error_name, info, line=None):
        self.error_name = error_name
        self.info = info
        self.line = line

    def as_string(self):
        loc = f" (line {self.line})" if self.line else ""
        return f"{self.error_name}{loc}: {self.info}"


class IllegalCharacterError(Error):
    def __init__(self, info, line=None):
        super().__init__("Illegal Character", info, line)


def main():
    if len(sys.argv) < 2:
        print("usage: python lexer.py <filepath>")
        sys.exit(1)
    file_path = sys.argv[1]

    try:
        with open(file_path, "r") as file:
            source = file.read()
            lexer = Lexer(source)
            tokens, error = lexer.createTokens()
            if error:
                print(error.as_string())
            else:
                for token in tokens:
                    print(token)
    except FileNotFoundError:
        print(f"file '{file_path}' not found")
    except Exception as e:
        print(f"unknown error '{e}'")


if __name__ == "__main__":
    main()
