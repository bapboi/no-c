# no-c

no-c is a functional language that intends to have no global namespace and functional features, while still adopting imperative programming standards.

## how to run

`ncc` is a bash script that calls the lexer, parser, and compiler.
you can either add the folder that contains it to your .bashrc or .zshrc, but i choose to run it within the local environment with `./ncc`

the format is `ncc <flag> <filepath>`, where flag is one of three flags (-l, -p, -r) that either calls the lexer, the parser, or transpiles and executes the provided program.
the file format is not enforced yet but planned to take .nc files.

written in python.

//TODO: resolve None conditional comparisons, add unsupported functions to parser, cleanup parser in general
