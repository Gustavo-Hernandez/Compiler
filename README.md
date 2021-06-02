# LepLang Compiler
This compiler is a project part of the Compilers Design class taught at the Instituto Tecnológico y de Estudios de Monterrey Campus Monterrey. This project aims to evaluate the core aspects of an object-oriented programming language, for example, the implementation of multi-scope variables, functions, arrays, class definitions, extension and the use of interfaces.
## Dependencies
 - Python: Version >3.8.7
 - PLY (Python Lex-Yacc): 
	 - Used for tokens and grammar definitions.
	 - Source code available at: https://github.com/dabeaz/ply

## Installation
[Install Python](https://www.python.org/downloads/)

Install PLY:

    pip install ply
    
## Usage

 ### macOS
To compile a program:

    python3 parser.py <path/filename.txt>

To run a compiled program:

    python3 virtual_machine.py <path/out.obj> 

 ### Windows
To compile a program:

    python parser.py <path/filename.txt>

To run a compiled program:

    python virtual_machine.py <path/out.obj> 
## Programming in LepLang
- A quick reference guide for LepLang can be found inside this repository at *docs/UserManual*
- A series of code examples can be found at *testcases*

## Authors

 - Gustavo Hernández Sánchez
 - Luis Miguel Maawad Hinojosa
