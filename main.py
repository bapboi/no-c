import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from loader import loadProgram
from compiler import Compiler

if len(sys.argv) < 2:
    print("usage: python main.py <file.nc>")
    sys.exit(1)

file_path = sys.argv[1]

try:
    ast = loadProgram(file_path)
except Exception as e:
    print(f"error: {e}")
    sys.exit(1)

try:
    Compiler(ast).compile_and_run()
except Exception as e:
    print(f"error: {e}")
    sys.exit(1)
