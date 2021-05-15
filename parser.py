# ------------------------------------------------------------
# parser.py
# A01364749 Gustavo Hernandez Sanchez
# A01364701 Luis Miguel Maawad Hinojosa
# ------------------------------------------------------------
import ply.yacc as yacc
import sys

# Get the token map from the lexer.  This is required.
from lexer import tokens
from components.variable_table import VariableTable
from components.function_dir import FunctionDirectory
from components.code_gen import CodeGenerator

var_table = None
func_dir = None
current_table = None
called_function = None
current_function = None
code_gen = CodeGenerator()
current_scope = "global"
# Grammars Definition

# ---- BEGIN CLASS DEFINITION ---------


def p_class(p):
    '''class    : classAux class_1'''
    func_dir.print()
    code_gen.operands.print()
    code_gen.types.print()
    code_gen.operators.print()
    print("VarTable")
    var_table.print()
    print(code_gen.quadruples)


def p_classAux(p):
    '''classAux    : visibility CLASS ID'''
    global var_table, func_dir, current_table
    var_table = VariableTable()
    func_dir = FunctionDirectory(var_table)
    current_table = var_table
    code_gen.add_main()


def p_class_1(p):
    '''class_1  : class_2 OPEN_BRACKET class_3 class_4 class_5 CLOSED_BRACKET'''
    code_gen.end_prog()
    val = func_dir.directory.get('main', None)
    if val:
        code_gen.add_main_dir(val['position'])
    else:
        code_gen.add_main_dir(code_gen.counter)


def p_class_2(p):
    '''class_2  : extension
                | empty'''


def p_class_3(p):
    '''class_3  : statement class_3
                | empty'''


def p_class_4(p):
    '''class_4  : module class_4
                | empty'''


def p_class_5(p):
    '''class_5  : main
                | empty'''


# ---- END CLASS DEFINITION ---------

# ---- BEGIN MAIN DEFINITION ---------

def p_main(p):
    '''main : mainAux OPEN_PARENTHESIS CLOSED_PARENTHESIS block'''


def p_mainAux(p):
    '''mainAux : MAIN'''
    func_dir.add_function('void', p[1], code_gen.counter)
    global current_table
    current_table = func_dir.get_var_table()
    code_gen.reset_t_counter()


# ---- END MAIN DEFINITION ---------

# ---- BEGIN VISIBILITY DEFINITION ---------


def p_visibility(p):
    '''visibility   : PUBLIC
                    | PRIVATE
                    | PROTECTED'''


# ---- END VISIBILITY DEFINITION ---------

# ---- BEGIN STATEMENT DEFINITION ---------


def p_statement(p):
    '''statement    : statementAux
                    | condition
                    | printing
                    | loop
                    | void_call'''


def p_statementAux(p):
    '''statementAux : assignation
                    | declaration'''
    code_gen.final_solve()


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
    code_gen.end_func()


def p_module_1(p):
    '''module_1 : module_ret
                | module_void'''
    func_dir.delete_var_table(p[1])

# ---- END MODULE DEFINITION ---------

# ---- BEGIN MODULE_VOID DEFINITION ---------


def p_module_void(p):
    '''module_void  : module_voidAux block'''
    p[0] = p[1]


def p_module_voidAux(p):
    '''module_voidAux  : VOID ID params'''
    p[0] = p[2]
    func_dir.add_function(p[1], p[2], code_gen.counter)
    global current_table
    current_table = func_dir.get_var_table()
    code_gen.reset_t_counter()


# ---- END MODULE_VOID DEFINITION ---------

# ---- BEGIN MODULE_RET DEFINITION ---------


def p_module_ret(p):
    '''module_ret  : module_retAux OPEN_BRACKET module_ret_1 RETURN expression SEMICOLON CLOSED_BRACKET'''
    code_gen.final_solve()
    code_gen.add_return(p[1][0])
    p[0] = p[1][1]


def p_module_retAux(p):
    '''module_retAux  : type_atomic ID params'''
    p[0] = [p[1], p[2]]
    func_dir.add_function(p[1], p[2], code_gen.counter)
    var_table.set_type(p[1])
    var_table.store_id(p[2])
    var_table.register(current_scope)
    global current_table
    current_table = func_dir.get_var_table()
    code_gen.reset_t_counter()


def p_module_ret_1(p):
    '''module_ret_1 : statement module_ret_1
                    | empty'''
# ---- END MODULE_RET DEFINITION ---------

# ---- BEGIN PARAMS DEFINITION ---------


def p_params(p):
    '''params  : OPEN_PARENTHESIS params_1 CLOSED_PARENTHESIS'''


def p_paramsAux(p):
    '''paramsAux : type_atomic ID'''
    func_dir.store_param(p[1], p[2])


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
# ---- END EXTENSION DEFINITION ---------

# ---- BEGIN CALL DEFINITIONS ----

# def p_method_call(p):
# '''method_call : ID POINT func_call'''

# def p_method_call_void(p):
# '''method_call_void : method_call SEMICOLON'''


# def p_argument_call(p):
# '''argument_call : ID POINT ID'''


def p_func_call(p):
    '''func_call : func_call_aux OPEN_PARENTHESIS func_call_1 CLOSED_PARENTHESIS'''
    tp = len(list(func_dir.directory[current_function]['params'].values()))
    code_gen.validate_params(tp)
    code_gen.go_sub(current_function)
    ret_type = func_dir.directory[current_function]['return_type']
    if ret_type != "void":
        p[0] = code_gen.call_return(current_function, ret_type)


def p_func_call_aux(p):
    '''func_call_aux : ID'''
    p[0] = p[1]
    if p[1] in func_dir.directory:
        code_gen.generate_era(p[1])
        global current_function
        current_function = p[1]
    else:
        raise NameError(
            "Function call to undefined function: " + p[1])


def p_func_call_1(p):
    '''func_call_1  : func_call_aux_2 func_call_2
                    | empty'''


def p_func_call_2(p):
    '''func_call_2  : COMMA func_call_aux_2 func_call_2
                    | empty'''


def p_func_call_aux_2(p):
    '''func_call_aux_2 : expression'''
    code_gen.final_solve()
    tp = list(func_dir.directory[current_function]['params'].values())
    if len(tp) > code_gen.par_counter:
        code_gen.param(tp[code_gen.par_counter]['type'])
    else:
        raise TypeError(
            "Function parameters exceed expected parameters")


def p_void_call(p):
    '''void_call : func_call SEMICOLON'''


# ---- END CALL DEFINITIONS ----

# ---- BEGIN ASSIGNATION DEFINITION ---------


def p_assignation(p):
    '''assignation : assignationAux assignation_1 SEMICOLON'''


def p_assignationAux(p):
    '''assignationAux : ID EQUALS'''
    code_gen.addOperand(p[1])
    code_gen.addOperator(p[2])
    code_gen.types.push(current_table.get_type(p[1]))


def p_assignation_1(p):
    '''assignation_1    : expression
                        | array_dec'''
    p[0] = p[1]
# ---- END ASSIGNATION DEFINITION ---------

# ---- BEGIN DECLARATION DEFINITION ---------


def p_declaration(p):
    '''declaration :  declaration_1 SEMICOLON'''
    current_table.register(current_scope)


def p_declaration_1(p):
    '''declaration_1    : type declaration_1Aux declaration_2
                        | declaration_1Aux2 declaration_3'''


def p_declaration_1Aux(p):
    '''declaration_1Aux    : ID'''
    current_table.store_id(p[1])
    p[0] = p[1]


def p_declaration_1Aux2(p):
    '''declaration_1Aux2    : type declaration_1Aux EQUALS'''
    code_gen.operators.push(p[3])
    code_gen.addOperand(p[2])
    code_gen.types.push(p[1])


def p_declaration_2(p):
    '''declaration_2    : COMMA declaration_1Aux declaration_2
                        | empty'''


def p_declaration_3(p):
    '''declaration_3    : expression
                        | array_dec'''


# ---- END DECLARATION DEFINITION ---------

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
    code_gen.printing()


def p_printingAux(p):
    '''printingAux : PRINT OPEN_PARENTHESIS expression CLOSED_PARENTHESIS'''
    code_gen.final_solve()
# ---- END PRINTING DEFINITION ---------

# ---- BEGIN CONDITION DEFINITION ---------


def p_condition(p):
    '''condition : conditionAux block condition_1'''
    code_gen.condition_2()


def p_conditionAux(p):
    '''conditionAux : IF OPEN_PARENTHESIS expression CLOSED_PARENTHESIS'''
    code_gen.final_solve()
    code_gen.condition_1()


def p_condition_1(p):
    '''condition_1 : condition_1Aux block
                   | empty'''


def p_condition_1Aux(p):
    '''condition_1Aux : ELSE'''
    code_gen.condition_3()
# ---- END PRINTING DEFINITION ---------

# ---- BEGIN LOOP DEFINITION ---------


def p_loop(p):
    '''loop : loopAux2 block'''
    code_gen.loop_3()


def p_loopAux(p):
    '''loopAux : LOOP'''
    code_gen.loop_1()


def p_loopAux2(p):
    '''loopAux2 : loopAux OPEN_PARENTHESIS expression CLOSED_PARENTHESIS'''
    code_gen.final_solve()
    code_gen.loop_2()
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
    code_gen.addOperator_4(p[0])
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
    code_gen.addOperator_3(p[0])

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
    code_gen.addOperator_1(p[1])

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
    code_gen.addOperator_2(p[1])
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
    code_gen.addOperator(p[1])


def p_factorAux2(p):
    '''factorAux2   : CLOSED_PARENTHESIS'''
    p[0] = p[1]
    code_gen.factor_solve()


def p_factor_1(p):
    '''factor_1 : PLUS
                | MINUS
                | empty'''
    if p[1]:
        p[0] = p[1]
# ---- END FACTOR DEFINITION ---------

# ---- BEGIN VAR_CTE DEFINITION ---------


def p_var_cte(p):
    '''var_cte  : var_cteAuxID
                | var_cteAuxINT
                | var_cteAuxFLOAT
                | var_cteAuxSTRING
                | var_cteAuxBOOL
                | func_call'''
    if p[1]:
        p[0] = p[1]
        code_gen.addOperand(p[1])


def p_var_cteAuxID(p):
    '''var_cteAuxID  : ID'''
    p[0] = p[1]
    if p[1] not in current_table.table and current_table != var_table:
        code_gen.types.push(var_table.get_type(p[1]))
    else:
        code_gen.types.push(current_table.get_type(p[1]))


def p_var_cteAuxINT(p):
    '''var_cteAuxINT  : CTE_I'''
    p[0] = p[1]
    code_gen.types.push("int")


def p_var_cteAuxFLOAT(p):
    '''var_cteAuxFLOAT  : CTE_F'''
    p[0] = p[1]
    code_gen.types.push("float")


def p_var_cteAuxSTRING(p):
    '''var_cteAuxSTRING  : CTE_S'''
    p[0] = p[1]
    code_gen.types.push("string")


def p_var_cteAuxBOOL(p):
    '''var_cteAuxBOOL   : TRUE
                        | FALSE '''
    p[0] = p[1]
    code_gen.types.push("bool")

# ---- END VAR_CTE DEFINITION ---------

# ---- BEGIN TYPE_ATOMIC DEFINITION ---------


def p_type_atomic(p):
    '''type_atomic  : INT
                    | FLOAT
                    | DOUBLE
                    | STRING
                    | BOOL'''
    p[0] = p[1]
# ---- END TYPE_ATOMIC DEFINITION ---------

# ---- BEGIN TYPE DEFINITION ---------


def p_type(p):
    '''type : tp type_1'''
    if p[2]:
        p[0] = p[1] + p[2]
    else:
        p[0] = p[1]
    current_table.set_type(p[0])


def p_type_1(p):
    '''type_1   : arr_dim type_2
                | empty'''
    if len(p) > 2:
        p[0] = p[1] + p[2]
    else:
        p[0] = p[1]


def p_type_2(p):
    '''type_2   : arr_dim
                | empty'''
    p[0] = p[1]
# ---- END TYPE DEFINITION ---------

# ---- BEGIN TP DEFINITION ---------


def p_tp(p):
    '''tp   : type_atomic
            | ID'''
    p[0] = p[1]
# ---- END TP DEFINITION ---------

# ---- BEGIN ARR_DIM DEFINITION ---------


def p_arr_dim(p):
    '''arr_dim  : OPEN_SQRT_BRACKET CTE_I CLOSED_SQRT_BRACKET'''
    p[0] = p[1] + p[2] + p[3]
# ---- END ARR_DIM DEFINITION ---------


def p_empty(p):
    'empty :'
    pass

# Error rule for syntax errors


def p_error(p):
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
