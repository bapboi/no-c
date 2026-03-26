import sys

TT_INT = "INT"
TT_FLOAT = "FLOAT"
TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MULT = "MULT"
TT_DIV = "DIV"
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_LBRACE = "LBRACE"
TT_RBRACE = "RBRACE"
TT_IDENTIFIER = "IDENTIFIER"
TT_KEYWORD = "KEYWORD"
TT_EQ = "EQUALS"
TT_COMMA = "COMMA"
TT_SEMI = "SEMI"
TT_STRING = "STRING"

TT_EOF = "EOF"
NUM = "0123456789"

KEYWORDS = [
    "fn",
    "return",
    "if",
    "else",
    "while",
    "mut",
    "module",
    "import",
    "export",
    "print",
]


class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value:
            return f"{self.type}:{self.value}"
        return f"{self.type}"


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = -1
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def createTokens(self):
        tokens = []
        while self.current_char != None:
            if self.current_char in " \t\n":
                self.advance()
            elif self.current_char in NUM:
                tokens.append(self.makeNum())
            elif self.current_char.isalpha() or self.current_char == "_":
                tokens.append(self.makeIdent())
            elif self.current_char == '"':
                tokens.append(self.makeString())
            elif self.current_char == "+":
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif self.current_char == "-":
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.current_char == "*":
                tokens.append(Token(TT_MULT))
                self.advance()
            elif self.current_char == "/":
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.current_char == "(":
                tokens.append(Token(TT_LPAREN))
                self.advance()
            elif self.current_char == ")":
                tokens.append(Token(TT_RPAREN))
                self.advance()
            elif self.current_char == "=":
                tokens.append(Token(TT_EQ))
                self.advance()
            elif self.current_char == "{":
                tokens.append(Token(TT_LBRACE))
                self.advance()
            elif self.current_char == "}":
                tokens.append(Token(TT_RBRACE))
                self.advance()
            elif self.current_char == ",":
                tokens.append(Token(TT_COMMA))
                self.advance()
            elif self.current_char == ";":
                tokens.append(Token(TT_SEMI))
                self.advance()
            else:
                char = self.current_char
                self.advance()
                return [], IllegalCharacterException("'" + char + "'")
        tokens.append(Token(TT_EOF))
        return tokens, None

    def makeNum(self):
        num_str = ""
        dotcount = 0
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
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))

    def makeIdent(self):
        id_str = ""
        while self.current_char != None and (
            self.current_char.isalnum() or self.current_char == "_"
        ):
            id_str += self.current_char
            self.advance()
        if id_str in KEYWORDS:
            return Token(TT_KEYWORD, id_str)
        else:
            return Token(TT_IDENTIFIER, id_str)

    def makeString(self):
        string = ""
        self.advance()
        while self.current_char != None and self.current_char != '"':
            string += self.current_char
            self.advance()
        self.advance()
        return Token(TT_STRING, string)


class Error:
    def __init__(self, error_name, info):
        self.error_name = error_name
        self.info = info

    def as_string(self):
        result = f"{self.error_name}: {self.info}"
        return result


class IllegalCharacterException(Error):
    def __init__(self, info):
        super().__init__("Illegal Character", info)


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
        print(f"unkown error '{e}'")


if __name__ == "__main__":
    main()
