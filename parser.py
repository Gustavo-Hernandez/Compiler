# ------------------------------------------------------------
# parser.py
# A01364749 Gustavo Hernandez Sanchez
# A01364701 Luis Miguel Maawad Hinojosa
# ------------------------------------------------------------
from components.mem_manager import MemoryManager
import ply.yacc as yacc
import sys

# Get the token map from the lexer.  This is required.
from lexer import tokens
from components.variable_table import VariableTable
from components.function_dir import FunctionDirectory
from components.code_gen import CodeGenerator
from components.semantics import Semantics

semantics = Semantics()
err = False

# Grammars Definition
# ---- BEGIN PROGRAM DEFINITION --------


def p_program(p):
    '''program : programAux programAux1 program_3 main CLOSED_BRACKET'''
    semantics.end_program()


def p_programAux(p):
    '''programAux : PROGRAM ID'''
    semantics.init_program(p[2])


def p_programAux1(p):
    '''programAux1 : programAux1_1 program_2'''


def p_programAux1_1(p):
    '''programAux1_1 : OPEN_BRACKET program_1'''
    semantics.store_global_statements()


def p_program_1(p):
    '''program_1    : statementAux program_1
                    | empty'''


def p_program_2(p):
    '''program_2    : interface program_2
                    | empty'''


def p_program_3(p):
    '''program_3    : class program_3
                    | empty'''
    if not p[1]:
        semantics.set_current_function_directory_as_global()


# ---- END PROGRAM DEFINITION --------


# ---- BEGIN INTERFACE DEFINITION ---------
def p_interface(p):
    '''interface    :   interfaceAux module_signature CLOSED_BRACKET'''
    semantics.store_interface(p[1])


def p_interfaceAux(p):
    '''interfaceAux : INTERFACE ID OPEN_BRACKET'''
    semantics.init_current_interface()
    p[0] = p[2]


def p_module_signature(p):
    '''module_signature :   module_signatureAux module_signature
                        |   empty'''


def p_module_signatureAux(p):
    '''module_signatureAux  :   FUNC module_retAux SEMICOLON
                            |   FUNC module_voidAux SEMICOLON'''

# ---- END INTERFACE DEFINITION --------

# ---- BEGIN CLASS DEFINITION ---------


def p_class(p):
    '''class    : classAux class_1'''
    # p[1][0] is id
    # p[1][1] is visibility
    # p[2][0] is extension
    # p[2][2] class_temporals
    # [2][3] is implemented_id
    # p[1][2] is codegen.counter
    # p[2][1] is exe
    semantics.store_class(p[1][0], p[1][1], p[2][0],
                          p[2][2], p[2][3], p[1][2], p[2][1])
    p[0] = p[1]


def p_classAux(p):
    '''classAux    : visibility CLASS ID'''
    semantics.init_class(p[3])
    # Pushing visibility and id value upwards
    p[0] = [p[3], p[1], semantics.code_gen.counter]


def p_class_1(p):
    '''class_1  : class_1Aux class_5 CLOSED_BRACKET'''
    # Pushing extension value, class temps and implementation upwards
    p[0] = p[1]


def p_class_1Aux(p):
    '''class_1Aux  : class_2 class_3 OPEN_BRACKET class_4'''
    class_temp = MemoryManager().get_class_temps()
    semantics.store_class_temporals()
    # Pushing extension value, class temps and implementation upwards
    p[0] = p[1] + [class_temp] + [p[2]]


def p_class_2(p):
    '''class_2  : extension
                | empty'''
    # Pushing extension value upwards
    if p[1]:
        exe = semantics.handle_class_extension(p[1])
    else:
        exe = []
    p[0] = [p[1], exe]


def p_class_3(p):
    '''class_3  : implementation
                | empty'''
    if p[1]:
        p[0] = p[1]


def p_class_4(p):
    '''class_4  : statementAux class_4
                | empty'''


def p_class_5(p):
    '''class_5  : module class_5
                | empty'''
    semantics.set_current_scope('local')


# ---- END CLASS DEFINITION ---------

# ---- BEGIN MAIN DEFINITION ---------


def p_main(p):
    '''main : mainAux OPEN_PARENTHESIS CLOSED_PARENTHESIS block'''
    semantics.end_main()


def p_mainAux(p):
    '''mainAux : MAIN'''
    semantics.init_main()
    p[0] = p[1]


# ---- END MAIN DEFINITION ---------

# ---- BEGIN VISIBILITY DEFINITION ---------


def p_implementation(p):
    '''implementation   : IMPLEMENTS ID'''
    p[0] = p[2]


# ---- END VISIBILITY DEFINITION ---------

# ---- BEGIN IMPLEMENTATION DEFINITION ---------


def p_visibility(p):
    '''visibility   : PUBLIC
                    | BLOCKED'''
    p[0] = p[1]


# ---- END IMPLEMENTATION DEFINITION ---------

# ---- BEGIN STATEMENT DEFINITION ---------


def p_statement(p):
    '''statement    : statementAux
                    | condition
                    | printing
                    | loop
                    | void_call
                    | reading
                    | void_object_call'''


def p_statementAux(p):
    '''statementAux : assignation
                    | declaration'''
    semantics.solve_statement()


# ---- END STATEMENT DEFINITION ---------

# ---- BEGIN BLOCK DEFINITION ---------


def p_block(p):
    '''block   : OPEN_BRACKET block_1 CLOSED_BRACKET'''


def p_block_1(p):
    '''block_1 : statement block_1
                | empty'''


# ---- END BLOCK DEFINITION ---------

# ---- BEGIN MODULE DEFINITION ---------


def p_module(p):
    '''module   : FUNC module_1'''
    semantics.end_function()


def p_module_1(p):
    '''module_1 : module_ret
                | module_void'''
    semantics.module_vartable_export(p[1])


# ---- END MODULE DEFINITION ---------

# ---- BEGIN MODULE_VOID DEFINITION ---------


def p_module_void(p):
    '''module_void  : module_voidAux block'''
    p[0] = p[1]


def p_module_voidAux(p):
    '''module_voidAux  : VOID ID params'''
    p[0] = p[2]
    semantics.process_void_module_declaration(p[2])

# ---- END MODULE_VOID DEFINITION ---------

# ---- BEGIN MODULE_RET DEFINITION ---------


def p_module_ret(p):
    '''module_ret  : module_retAux OPEN_BRACKET module_ret_1 RETURN expression SEMICOLON CLOSED_BRACKET'''
    semantics.end_return_module(p[1][0])
    p[0] = p[1][1]


def p_module_retAux(p):
    '''module_retAux  : type_atomic ID params'''
    p[0] = [p[1], p[2]]
    semantics.process_module_ret_declaration(p[1], p[2])


def p_module_ret_1(p):
    '''module_ret_1 : statement module_ret_1
                    | empty'''


# ---- END MODULE_RET DEFINITION ---------

# ---- BEGIN PARAMS DEFINITION ---------


def p_params(p):
    '''params  : OPEN_PARENTHESIS params_1 CLOSED_PARENTHESIS'''


def p_paramsAux(p):
    '''paramsAux : type_atomic ID'''
    semantics.process_param(p[1], p[2])


def p_params_1(p):
    '''params_1 : paramsAux params_2
                | empty'''


def p_params_2(p):
    '''params_2 : COMMA paramsAux params_2
                | empty'''


# ---- END PARAMS DEFINITION ---------

# ---- BEGIN EXTENSION DEFINITION ---------


def p_extension(p):
    '''extension : COLON ID'''
    p[0] = p[2]


# ---- END EXTENSION DEFINITION ---------

# ---- BEGIN CALL DEFINITIONS ----

def p_void_object_call(p):
    '''void_object_call : object_call SEMICOLON'''
    if p[1] != 'void':
        raise TypeError("Can only call void methods outside of expressions")


def p_object_call(p):
    '''object_call : object_callAux object_call_1'''
    p[0] = semantics.process_object_call(p[1][0], p[1][1])


def p_object_callAux(p):
    '''object_callAux : ID POINT ID'''
    class_name, address = semantics.validate_object_call(p[1], p[3])
    p[0] = [class_name, address]


def p_object_call_2(p):
    '''object_call_1    : object_callAux2 object_call_3 CLOSED_PARENTHESIS
                        | empty'''


def p_object_callAux2(p):
    '''object_callAux2 : OPEN_PARENTHESIS'''
    semantics.validate_class_function_call()


def p_object_call_3(p):
    '''object_call_3    : object_callAux1 object_call_4
                        | empty'''


def p_object_call_4(p):
    '''object_call_4    : COMMA object_callAux1 object_call_4
                        | empty'''


def p_object_callAux1(p):
    '''object_callAux1 : expression'''
    semantics.validate_function_params()


def p_func_call(p):
    '''func_call : func_call_aux OPEN_PARENTHESIS func_call_1 CLOSED_PARENTHESIS'''
    p[0] = semantics.end_function_call()


def p_func_call_aux(p):
    '''func_call_aux : ID'''
    semantics.validate_function_existance(p[1])
    p[0] = p[1]


def p_func_call_1(p):
    '''func_call_1  : func_call_aux_2 func_call_2
                    | empty'''


def p_func_call_2(p):
    '''func_call_2  : COMMA func_call_aux_2 func_call_2
                    | empty'''


def p_func_call_aux_2(p):
    '''func_call_aux_2 : expression'''
    semantics.validate_function_params()


def p_void_call(p):
    '''void_call : func_call SEMICOLON'''
    if p[1] != 'void':
        raise TypeError("Can only call void functions outside of expressions")


# ---- END CALL DEFINITIONS ----

# ---- BEGIN ASSIGNATION DEFINITION ---------


def p_assignation(p):
    '''assignation : assignationAux assignation_1 SEMICOLON'''


def p_assignationAux(p):
    '''assignationAux : id_arr_var EQUALS'''
    semantics.add_operator(p[2])


def p_assignation_1(p):
    '''assignation_1    : expression
                        | array_dec'''
    p[0] = p[1]


# ---- END ASSIGNATION DEFINITION ---------

# ---- BEGIN DECLARATION DEFINITION ---------


def p_declaration(p):
    '''declaration  : type_atomic declaration_1 SEMICOLON
                    | object_declaration'''
    semantics.process_declaration()


def p_declaration_1(p):
    '''declaration_1    : declaration_1Aux declaration_2
                        | declaration_1Aux2 declaration_3'''


def p_declaration_1Aux(p):
    '''declaration_1Aux    : id_arr'''
    if '[' in p[1]:
        semantics.process_id_array(p[1])
    else:
        semantics.register_id(p[1])
        p[0] = p[1]


def p_declaration_1Aux2(p):
    '''declaration_1Aux2    : ID EQUALS'''
    semantics.process_initialized_declaration(p[1], p[2])


def p_declaration_2(p):
    '''declaration_2    : COMMA declaration_1Aux declaration_2
                        | empty'''


def p_declaration_3(p):
    '''declaration_3    : expression
                        | array_dec'''


# ---- END DECLARATION DEFINITION ---------

# ---- BEGIN OBJECT_DECLARATION DEFINITION -------


def p_object_declaration(p):
    '''object_declaration : object_declarationAux object_declaration_1 SEMICOLON'''
    semantics.enqueue_object()


def p_object_declaration_1(p):
    '''object_declaration_1 : COMMA ID object_declaration_1
                            | empty'''
    if len(p) > 2:
        semantics.register_id(p[2])


def p_object_declarationAux(p):
    '''object_declarationAux : ID ID'''
    semantics.validate_object_declaration(p[1], p[2])


# ---- END OBJECT_DECLARATION DEFINITION -------

# ---- BEGIN ARRAY_DEC DEFINITION ---------


def p_array_dec(p):
    '''array_dec    : OPEN_BRACKET array_ind array_dec_1 CLOSED_BRACKET
                    | array_ind'''
    if p[1] == '{':
        if p[3]:
            p[0] = p[1] + p[2] + p[3] + p[4]
        else:
            p[0] = p[1] + p[2] + p[4]
    else:
        p[0] = p[1]


def p_array_dec_1(p):
    '''array_dec_1  : COMMA array_ind array_dec_1
                    | empty'''
    if p[1]:
        if p[3]:
            p[0] = p[1] + p[2] + p[3]
        else:
            p[0] = p[1] + p[2]


# ---- END ARRAY_DEC DEFINITION ---------

# ---- BEGIN ARRAY_IND DEFINITION ---------


def p_array_ind(p):
    '''array_ind    : OPEN_BRACKET var_cte array_ind_1 CLOSED_BRACKET'''
    if p[3]:
        p[0] = p[1] + p[2] + p[3] + p[4]
    else:
        p[0] = p[1] + p[2] + p[4]


def p_array_ind_1(p):
    '''array_ind_1  : COMMA var_cte array_ind_1
                    | empty'''
    if p[1]:
        if p[3]:
            p[0] = p[1] + p[2] + p[3]
        else:
            p[0] = p[1] + p[2]


# ---- END ARRAY_IND DEFINITION ---------

# ---- BEGIN PRINTING DEFINITION ---------


def p_printing(p):
    '''printing : printingAux SEMICOLON'''
    semantics.end_printing_statement()


def p_printingAux(p):
    '''printingAux : PRINT OPEN_PARENTHESIS expression CLOSED_PARENTHESIS'''
    semantics.solve_statement()


# ---- END PRINTING DEFINITION ---------

# ---- BEGIN READING DEFINITION ---------


def p_reading(p):
    '''reading : READ OPEN_PARENTHESIS id_arr_var CLOSED_PARENTHESIS SEMICOLON'''
    semantics.end_reading_statement()


# ---- END READING DEFINITION ---------

# ---- BEGIN CONDITION DEFINITION ---------


def p_condition(p):
    '''condition : conditionAux block condition_1'''
    semantics.end_if_statement()


def p_conditionAux(p):
    '''conditionAux : IF OPEN_PARENTHESIS expression CLOSED_PARENTHESIS'''
    semantics.validate_if_statement()


def p_condition_1(p):
    '''condition_1 : condition_1Aux block
                   | empty'''


def p_condition_1Aux(p):
    '''condition_1Aux : ELSE'''
    semantics.process_else_block()


# ---- END PRINTING DEFINITION ---------

# ---- BEGIN LOOP DEFINITION ---------


def p_loop(p):
    '''loop : loopAux2 block'''
    semantics.end_loop()


def p_loopAux(p):
    '''loopAux : LOOP'''
    semantics.init_loop()


def p_loopAux2(p):
    '''loopAux2 : loopAux OPEN_PARENTHESIS expression CLOSED_PARENTHESIS'''
    semantics.validate_loop()


# ---- END LOOP DEFINITION ---------

# ---- BEGIN EXPRESSION DEFINITION ---------


def p_expression(p):
    '''expression : exp_l expression_1'''
    if p[2]:
        p[0] = p[1] + p[2]
    else:
        p[0] = p[1]


def p_expression_1(p):
    '''expression_1 : expression_2 expression
                    | empty'''
    if p[1]:
        p[0] = p[1] + p[2]


def p_expression_2(p):
    '''expression_2 : AND
                    | OR'''
    p[0] = p[1]
    semantics.add_operator_and_or(p[1])


# ---- END EXPRESSION DEFINITION ---------

# ---- BEGIN EXP_L DEFINITION ---------


def p_exp_l(p):
    '''exp_l : exp exp_l_1'''
    if p[2]:
        p[0] = p[1] + p[2]
    else:
        p[0] = p[1]


def p_exp_l_1(p):
    '''exp_l_1  : exp_l_2 exp
                | empty'''
    if p[1]:
        p[0] = p[1] + p[2]


def p_exp_l_2(p):
    '''exp_l_2  : GREATER_THAN
                | LOWER_THAN
                | NOT_EQUAL
                | EQUALITY'''
    p[0] = p[1]
    semantics.add_operator_comparison(p[1])

# ---- END EXP_L DEFINITION ---------

# ---- BEGIN EXP DEFINITION ---------


def p_exp(p):
    '''exp : term exp_1'''
    if p[2]:
        p[0] = p[1] + p[2]
    else:
        p[0] = p[1]


def p_exp_1(p):
    '''exp_1    : exp_2 exp
                | empty'''
    if p[1]:
        p[0] = p[1] + p[2]


def p_exp_2(p):
    '''exp_2    : PLUS
                | MINUS'''
    p[0] = p[1]
    semantics.add_operator_addition(p[1])


# ---- END EXP DEFINITION ---------

# ---- BEGIN TERM DEFINITION ---------


def p_term(p):
    '''term : factor term_1'''
    if p[2]:
        p[0] = p[1] + p[2]
    else:
        p[0] = p[1]


def p_term_1(p):
    '''term_1   : term_2 term
                | empty'''
    if p[1]:
        p[0] = p[1] + p[2]


def p_term_2(p):
    '''term_2   : TIMES
                | DIVIDE'''
    p[0] = p[1]
    semantics.add_operator_multiplication(p[1])


# ---- END TERM DEFINITION ---------

# ---- BEGIN FACTOR DEFINITION ---------


def p_factor(p):
    '''factor   : factorAux expression factorAux2
                | factor_1 var_cte'''
    if not p[1]:
        p[0] = p[2]
    elif p[1] == '(':
        p[0] = p[1] + p[2] + p[3]
    else:
        p[0] = p[1] + p[2]


def p_factorAux(p):
    '''factorAux   : OPEN_PARENTHESIS'''
    p[0] = p[1]
    semantics.add_operator(p[1])


def p_factorAux2(p):
    '''factorAux2   : CLOSED_PARENTHESIS'''
    p[0] = p[1]
    semantics.solve_factor()


def p_factor_1(p):
    '''factor_1 : PLUS
                | MINUS
                | empty'''
    if p[1]:
        p[0] = p[1]


# ---- END FACTOR DEFINITION ---------

# ---- BEGIN VAR_CTE DEFINITION ---------


def p_var_cte(p):
    '''var_cte  : id_arr_var
                | var_cteAuxINT
                | var_cteAuxFLOAT
                | var_cteAuxSTRING
                | var_cteAuxBOOL
                | func_call
                | object_call'''
    if p[1]:
        p[0] = p[1]


def p_var_cteAuxINT(p):
    '''var_cteAuxINT  : CTE_I'''
    p[0] = p[1]
    semantics.store_constant(int(p[1]), 'int')


def p_var_cteAuxFLOAT(p):
    '''var_cteAuxFLOAT  : CTE_F'''
    p[0] = p[1]
    semantics.store_constant(float(p[1]), 'float')


def p_var_cteAuxSTRING(p):
    '''var_cteAuxSTRING  : CTE_S'''
    p[0] = p[1]
    semantics.store_constant(p[1], 'string')


def p_var_cteAuxBOOL(p):
    '''var_cteAuxBOOL   : TRUE
                        | FALSE '''
    p[0] = p[1]
    semantics.store_constant(p[1], 'bool')

# ---- END VAR_CTE DEFINITION ---------

# ---- BEGIN TYPE_ATOMIC DEFINITION ---------


def p_type_atomic(p):
    '''type_atomic  : INT
                    | FLOAT
                    | STRING
                    | BOOL'''
    p[0] = p[1]
    semantics.store_current_type(p[1])


# ---- END TYPE_ATOMIC DEFINITION ---------


# ---- BEGIN ID_ARR DEFINITION ---------


def p_id_arr(p):
    '''id_arr : ID id_arr_1'''
    if len(p) > 2 and p[2]:
        p[0] = p[1] + p[2]
    else:
        p[0] = p[1]


def p_id_arr_1(p):
    '''id_arr_1     : arr_dim id_arr_1
                    | empty'''
    if len(p) > 2 and p[2]:
        p[0] = p[1] + p[2]
    else:
        p[0] = p[1]


# ---- END ID_ARR DEFINITION ---------

# ---- BEGIN ARR_DIM DEFINITION ---------


def p_arr_dim(p):
    '''arr_dim  : OPEN_SQRT_BRACKET CTE_I CLOSED_SQRT_BRACKET'''
    p[0] = p[1] + p[2] + p[3]


def p_arr_exp_loop(p):
    '''arr_exp_loop     : arr_aux arr_exp_loop
                        | empty'''


def p_arr_aux(p):
    '''arr_aux : arr_exp'''
    p[0] = p[1]
    semantics.set_array_dims()


def p_arr_exp(p):
    '''arr_exp  : arr_expAux expression CLOSED_SQRT_BRACKET'''
    p[0] = p[1] + p[2] + p[3]
    semantics.solve_array_expression()


def p_arr_expAux(p):
    '''arr_expAux  : OPEN_SQRT_BRACKET'''
    p[0] = p[1]
    semantics.add_operator('ARR')


# ---- END ARR_DIM DEFINITION ---------

# ---- BEGIN ID_ARR DEFINITION --------


def p_id_arr_var(p):
    '''id_arr_var : id_arr_varAuxID arr_exp_loop'''
    semantics.array_declaration(p[1])
    p[0] = p[1]


def p_id_arrID(p):
    '''id_arr_varAuxID  : ID'''
    p[0] = p[1]
    semantics.validate_array(p[1])


def p_empty(p):
    'empty :'
    pass


# Error rule for syntax errors


def p_error(p):
    global err
    err = True
    print("Syntax error in input!")


# Build the parser
parser = yacc.yacc()


def print_grammar(p):
    for v in p:
        print("grm: " + str(v))


# Validate if a file was passed through the command line arguments.
if len(sys.argv) > 1:
    with open(sys.argv[1], 'r') as file:
        file_content = file.read().replace('\n', ' ')

    # Parse the file content.
    result = parser.parse(file_content)
    if not err:
        semantics.generateObj('./output')
