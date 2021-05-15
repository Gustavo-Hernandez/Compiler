# ------------------------------------------------------------
# lex.py
# A01364749 Gustavo Hernandez Sanchez
# A01364701 Luis Miguel Maawad Hinojosa
# ------------------------------------------------------------
import ply.lex as lex
import sys

# List of token names.
tokens = (
    'ID',
    'CTE_F',
    'CTE_I',
    'CTE_S',
    'COLON',
    'POINT',
    'SEMICOLON',
    'OPEN_BRACKET',
    'CLOSED_BRACKET',
    'EQUALS',
    'GREATER_THAN',
    'LOWER_THAN',
    'NOT_EQUAL',
    'OPEN_PARENTHESIS',
    'CLOSED_PARENTHESIS',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    "COMMA",
    "OPEN_SQRT_BRACKET",
    "CLOSED_SQRT_BRACKET",
    "EQUALITY"
)
# Reserved words
reserved = {
    'class': 'CLASS',
    'public': 'PUBLIC',
    'private': 'PRIVATE',
    'protected': 'PROTECTED',
    'main': 'MAIN',
    'func': 'FUNC',
    'void': 'VOID',
    'int': 'INT',
    'float': 'FLOAT',
    'double': 'DOUBLE',
    'string': 'STRING',
    'bool': 'BOOL',
    'print': 'PRINT',
    'if': 'IF',
    'else': 'ELSE',
    'loop': 'LOOP',
    'true': 'TRUE',
    'false': 'FALSE',
    'and': 'AND',
    'or': 'OR',
    'return': 'RETURN'
}

# Add the reserved values to the token list.
tokens += tuple(reserved.values())

# Regular expression rules for simple tokens
t_CTE_I = r'[0-9][0-9]*'
t_CTE_F = r'[0-9]+\.[0-9]* '
t_CTE_S = r'\"(\\.|[^"\\])*\"'
t_COLON = r'\:'
t_POINT = r'\.'
t_COMMA = r'\,'
t_SEMICOLON = r'\;'
t_OPEN_BRACKET = r'\{'
t_CLOSED_BRACKET = r'\}'
t_OPEN_SQRT_BRACKET = r'\['
t_CLOSED_SQRT_BRACKET = r'\]'
t_EQUALS = r'\='
t_GREATER_THAN = r'\>'
t_LOWER_THAN = r'\<'
t_NOT_EQUAL = r'!='
t_OPEN_PARENTHESIS = r'\('
t_CLOSED_PARENTHESIS = r'\)'
t_PLUS = r'\+'
t_MINUS = r'\-'
t_TIMES = r'\*'
t_DIVIDE = r'\/'

# Special token to ignore whitespaces and tabs.
t_ignore = ' \t'

# ID token must be defined here in order to prevent
# reserved words to be classified as IDs


def t_ID(t):
    r'[A-Za-z][A-Za-z0-9|"_"]*'
    if t.value in reserved:
        t.type = reserved[t.value]
    return t

# EQuality token must be defined here in order to prevent
# EQUALITY to be classified as two EQUALS


def t_EQUALITY(t):
    r'=='
    return t

# Rule definition to track the amount of lines.


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Error handling Rule.


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()

# Validate if a file was passed through the command line
if(len(sys.argv) > 1):
    with open(sys.argv[1], 'r') as file:
        file_content = file.read().replace('\n', ' ')

    # Set file_content as the lexer's input.
    lexer.input(file_content)

    # Tokenize the provided input
    while True:
        tok = lexer.token()
        if not tok:
            break
        # print(tok)
