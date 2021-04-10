# ------------------------------------------------------------
# parser.py
# A01364749 Gustavo Hernandez Sanchez
# ------------------------------------------------------------
import ply.yacc as yacc
import sys

# Get the token map from the lexer.  This is required.
from lexer import tokens

#Grammars Definition

#---- BEGIN CLASS DEFINITION ---------
def p_class(p):
    '''class    : visibility CLASS ID class_1'''
def p_class_1(p):
    '''class_1  : class_2 OPEN_BRACKET class_3 class_4 CLOSED_BRACKET'''
def p_class_2(p):
    '''class_2  : extension
                | empty'''
def p_class_3(p):
    '''class_3  : statement class_3
                | empty'''
def p_class_4(p):
    '''class_4  : module class_4
                | empty'''
#---- END CLASS DEFINITION ---------
 
#---- BEGIN VISIBILITY DEFINITION ---------
def p_visibility(p):
    '''visibility   : PUBLIC
                    | PRIVATE
                    | PROTECTED'''
#---- END VISIBILITY DEFINITION ---------

#---- BEGIN STATEMENT DEFINITION ---------
def p_statement(p):
    '''statement    : assignation 
                    | condition
                    | printing
                    | declaration
                    | loop'''
#---- END STATEMENT DEFINITION ---------

#---- BEGIN BLOCK DEFINITION ---------
def p_block(p):
    '''block   : OPEN_BRACKET block_1 CLOSED_BRACKET'''
def p_block_1(p):
    '''block_1 : statement block_1
                | empty'''
#---- END BLOCK DEFINITION ---------

#---- BEGIN MODULE DEFINITION ---------
def p_module(p):
    '''module   : FUNC module_1'''
def p_module_1(p):
    '''module_1 : module_ret
                | module_void'''
#---- END MODULE DEFINITION ---------

#---- BEGIN MODULE_VOID DEFINITION ---------
def p_module_void(p):
    '''module_void  : VOID ID params block'''
#---- END MODULE_VOID DEFINITION ---------

#---- BEGIN MODULE_RET DEFINITION ---------
def p_module_ret(p):
    '''module_ret  : type_atomic ID params OPEN_BRACKET module_ret_1 RETURN expression SEMICOLON CLOSED_BRACKET'''
def p_module_ret_1(p):
    '''module_ret_1 : statement module_ret_1
                    | empty'''
#---- END MODULE_RET DEFINITION ---------

#---- BEGIN PARAMS DEFINITION ---------
def p_params(p):
    '''params  : OPEN_PARENTHESIS params_1 CLOSED_PARENTHESIS'''
def p_params_1(p):
    '''params_1 : type_atomic ID params_2
                | empty'''
def p_params_2(p):
    '''params_2 : COMMA type_atomic ID params_2
                | empty'''
#---- END PARAMS DEFINITION ---------

#---- BEGIN EXTENSION DEFINITION ---------
def p_extension(p):
    '''extension : COLON ID'''
#---- END EXTENSION DEFINITION ---------

#---- BEGIN ASSIGNATION DEFINITION ---------
def p_assignation(p):
    '''assignation : ID EQUALS assignation_1'''
def p_assignation_1(p):
    '''assignation_1    : expression
                        | array_dec'''
#---- END ASSIGNATION DEFINITION ---------

#---- BEGIN DECLARATION DEFINITION ---------
def p_declaration(p):
    '''declaration : type declaration_1 SEMICOLON'''
def p_declaration_1(p):
    '''declaration_1    : ID declaration_2
                        | ID EQUALS declaration_3'''
def p_declaration_2(p):
    '''declaration_2    : COMMA ID declaration_2
                        | empty'''
def p_declaration_3(p):
    '''declaration_3    : expression
                        | array_dec'''
#---- END DECLARATION DEFINITION ---------

#---- BEGIN ARRAY_DEC DEFINITION ---------
def p_array_dec(p):
    '''array_dec    : OPEN_BRACKET array_ind array_dec_1 CLOSED_BRACKET
                    | array_ind'''
def p_array_dec_1(p):
    '''array_dec_1  : COMMA array_ind array_dec_1
                    | empty'''
#---- END ARRAY_DEC DEFINITION ---------

#---- BEGIN ARRAY_IND DEFINITION ---------
def p_array_ind(p):
    '''array_ind    : OPEN_BRACKET var_cte array_ind_1 CLOSED_BRACKET'''
def p_array_ind_1(p):
    '''array_ind_1  : COMMA var_cte array_ind_1
                    | empty'''
#---- END ARRAY_IND DEFINITION ---------

#---- BEGIN PRINTING DEFINITION ---------
def p_printing(p):
    '''printing : PRINT OPEN_PARENTHESIS expression CLOSED_PARENTHESIS SEMICOLON'''
#---- END PRINTING DEFINITION ---------

#---- BEGIN CONDITION DEFINITION ---------
def p_condition(p): 
    '''condition : IF OPEN_PARENTHESIS expression CLOSED_PARENTHESIS block condition_1'''
def p_condition_1(p):
    '''condition_1 : ELSE block 
                   | empty'''
#---- END PRINTING DEFINITION ---------

#---- BEGIN LOOP DEFINITION ---------
def p_loop(p):
    '''loop : LOOP OPEN_PARENTHESIS expression CLOSED_PARENTHESIS block'''
#---- END LOOP DEFINITION ---------

#---- BEGIN EXPRESSION DEFINITION ---------
def p_expression(p):
    '''expression : exp_l expression_1'''
def p_expression_1(p):
    '''expression_1 : expression_2 expression
                    | empty'''
def p_expression_2(p):
    '''expression_2 : AND
                    | OR'''
#---- END EXPRESSION DEFINITION ---------

#---- BEGIN EXP_L DEFINITION ---------
def p_exp_l(p):
    '''exp_l : exp exp_l_1'''
def p_exp_l_1(p):
    '''exp_l_1  : exp_l_2 exp
                | empty'''
def p_exp_l_2(p):
    '''exp_l_2  : GREATER_THAN
                | LOWER_THAN
                | NOT_EQUAL
                | EQUALITY'''
#---- END EXP_L DEFINITION ---------

#---- BEGIN EXP DEFINITION ---------
def p_exp(p):
    '''exp : term exp_1'''
def p_exp_1(p):
    '''exp_1    : exp_2 exp
                | empty'''
def p_exp_2(p):
    '''exp_2    : PLUS
                | MINUS'''
#---- END EXP DEFINITION ---------

#---- BEGIN TERM DEFINITION ---------
def p_term(p):
    '''term : factor term_1'''
def p_term_1(p):
    '''term_1   : term_2 term
                | empty'''
def p_term_2(p):
    '''term_2   : TIMES
                | DIVIDE'''
#---- END TERM DEFINITION ---------

#---- BEGIN FACTOR DEFINITION ---------
def p_factor(p):
    '''factor   : OPEN_PARENTHESIS expression CLOSED_PARENTHESIS
                | factor_1 var_cte'''
def p_factor_1(p):
    '''factor_1 : PLUS
                | MINUS
                | empty'''
#---- END FACTOR DEFINITION ---------

#---- BEGIN VAR_CTE DEFINITION ---------
def p_var_cte(p):
    '''var_cte  : ID
                | CTE_I
                | CTE_F
                | CTE_S
                | TRUE
                | FALSE'''
#---- END VAR_CTE DEFINITION ---------

#---- BEGIN TYPE_ATOMIC DEFINITION ---------
def p_type_atomic(p):
    '''type_atomic  : INT
                    | FLOAT
                    | DOUBLE
                    | STRING
                    | BOOL'''
#---- END TYPE_ATOMIC DEFINITION ---------

#---- BEGIN TYPE DEFINITION ---------
def p_type(p):
    '''type : tp type_1'''

def p_type_1(p):
    '''type_1   : arr_dim type_2
                | empty'''
def p_type_2(p):
    '''type_2   : arr_dim
                | empty'''
#---- END TYPE DEFINITION ---------

#---- BEGIN TP DEFINITION ---------
def p_tp(p):
    '''tp   : type_atomic
            | ID'''
#---- END TP DEFINITION ---------

#---- BEGIN ARR_DIM DEFINITION ---------
def p_arr_dim(p):
    '''arr_dim  : OPEN_SQRT_BRACKET CTE_I CLOSED_SQRT_BRACKET'''
#---- END ARR_DIM DEFINITION ---------

def p_empty(p):
    'empty :'

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")
 
# Build the parser
parser = yacc.yacc()

# Validate if a file was passed through the command line arguments.
if(len(sys.argv) > 1):
    with open(sys.argv[1], 'r') as file:
        file_content = file.read().replace('\n',' ')

    # Parse the file content.
    result = parser.parse(file_content)
    print(result)
