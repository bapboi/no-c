# no-c

no-c is an imperative language that intends to have no global namespace and functional features, while still adopting c-like standards.

no-c supports arrays and array accessing, strings as arrays, divison by zero, error checking, null types, logical and bitwise operations, cross file imports, and features assumed for most programming languages 

no-c's main feature is the `module` keyword. excluding imports, everything must be defined within a `module`. modules define a singleton that can be exported using the `export` keyword to allow access to files that import it using `import`, and restricts reinstantiation. within modules, all features of the language are possible, including definition of user defined types, using the `type` keyword. `type` defines a type that can have multiple instances. 

## how to run

linux/osx:
`./ncc <flag> <filepath>`
`<flag>`: one of three flags (-l, -p, -r) that either calls the lexer, the parser, or transpiles and executes the provided program, with the loader resolving file paths 

requirements: python3 (developed in python 3.14.0) path in your env

written in python.


TODO: add support for os operations, expand built in library for basic math operations (make in no-c lawl), fix strings 

