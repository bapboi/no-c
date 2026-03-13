import re
import sys

TOKEN_SPEC = [
    ("INTEGER", r"\d+"),
    ("STRING", r'"[^"]*"'),
    ("PRINT", r"\bprint\b"),
    ("IDENTIFIER", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("PLUS", r"\+"),
    ("MINUS", r"\-"),
    ("STAR", r"\*"),
    ("SLASH", r"/"),
    ("EQUAL", r"="),
    ("SEMICOLON", r";"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
]

token = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC)


def lex(input):
    tokens = []
    for match in re.finditer(token, input):
        token_type = match.lastgroup
        token_value = match.group()

        tokens.append((token_type, token_value))
    tokens.append(("EOF", ""))
    return tokens


def main():
    if len(sys.argv) < 2:
        print("usage: python lex.py <filepath>")
        sys.exit(1)
    file_path = sys.argv[1]

    try:
        with open(file_path, "r") as file:
            source = file.read()
            tokens = lex(source)
            for token in tokens:
                print(token)
    except FileNotFoundError:
        print(f"file '{file_path}' not found")
    except Exception as e:
        print(f"unknown error '{e}'")


if __name__ == "__main__":
    main()
