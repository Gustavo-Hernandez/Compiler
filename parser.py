# ------------------------------------------------------------
# parser.py
# A01364749 Gustavo Hernandez Sanchez
# A01364701 Luis Miguel Maawad Hinojosa
# ------------------------------------------------------------
from components.mem_manager import MemoryManager
import ply.yacc as yacc
import sys
import re
import csv
import os

# Get the token map from the lexer.  This is required.
from lexer import tokens
from components.variable_table import VariableTable
from components.function_dir import FunctionDirectory
from components.code_gen import CodeGenerator

var_tables = {}
cte_table = VariableTable()
global_var_table = VariableTable()
var_table = None
current_func_dir = None
current_table = None
called_function = None
current_function = None
current_function_types = None
current_function_ret = None
current_arr = None
object_queue = []
current_arr_id = ''
code_gen = CodeGenerator()
err = False
class_dir = {}
program_vars = {}


# Grammars Definition

# ---- BEGIN PROGRAM DEFINITION --------


def p_program(p):
    '''program : programAux programAux1 program_2 main CLOSED_BRACKET'''
    code_gen.end_prog()
    program_vars['program'] = program_vars['program'].directory
    val = program_vars['program']['main']
    code_gen.add_main_dir(val['position'])


def p_programAux(p):
    '''programAux : PROGRAM ID'''
    global var_table, current_func_dir, current_table
    current_func_dir = FunctionDirectory()
    current_func_dir.add_function(p[2], 'program', 0)
    program_vars['program'] = current_func_dir
    var_table = program_vars['program'].get_var_table()
    current_table = global_var_table


def p_programAux1(p):
    '''programAux1 : OPEN_BRACKET program_1'''
    code_gen.add_main()
    var_tables['global'] = program_vars['program'].store_global_vars('program')


def p_program_1(p):
    '''program_1    : statementAux program_1
                    | empty'''


def p_program_2(p):
    '''program_2    : class program_2
                    | empty'''
    if not p[1]:
        global current_func_dir
        current_func_dir = program_vars['program']


# ---- END PROGRAM DEFINITION --------

# ---- BEGIN CLASS DEFINITION ---------


def p_class(p):
    '''class    : classAux class_1'''
    # p[1] is visibility and id, p[2] is extension and class_temps

    # Class size calculation
    class_size = {}
    class_size.update(MemoryManager().get_class_vars())
    class_size.update(p[2][2])

    class_address = MemoryManager().request_class_address(p[1][0], p[1][1])
    exe = p[2][1] + [p[1][2]]
    class_dir[p[1][0]] = {"visibility": p[1][1], "extension": p[2][0],
                          'functions': current_func_dir.directory,
                          'var_table': var_table.table, 'size': class_size,
                          'address': class_address, 'execution': exe}

    # Clear context
    MemoryManager().reset_class_context()
    p[0] = p[1]


def p_classAux(p):
    '''classAux    : visibility CLASS ID'''
    # Class Function Directory reset.
    if p[3] in class_dir:
        raise KeyError("Class " + p[3] + " has already been declared.")
    global current_func_dir, var_table, current_table, code_gen
    code_gen.current_scope = "class"
    current_func_dir = FunctionDirectory()
    current_func_dir.global_vartable = global_var_table
    var_table = VariableTable()
    current_func_dir.class_vartable = var_table
    current_table = var_table
    # Pushing visibility and id value upwards
    p[0] = [p[3], p[1], code_gen.counter]


def p_class_1(p):
    '''class_1  : class_1Aux class_4 CLOSED_BRACKET'''
    # Pushing extension value and class temps upwards
    p[0] = p[1]


def p_class_1Aux(p):
    '''class_1Aux  : class_2 OPEN_BRACKET class_3'''
    # TODO: MOVE =>
    # Get class size
    class_temp = MemoryManager().get_class_temps()
    code_gen.reset_t_counter()
    code_gen.current_scope = 'local'
    code_gen.end_class()
    # Pushing extension value and class temps upwards
    p[0] = p[1] + [class_temp]


def p_class_2(p):
    '''class_2  : extension
                | empty'''
    # Pushing extension value upwards
    if p[1]:
        global class_dir, current_func_dir
        if p[1] not in class_dir:
            raise KeyError("Can not extend from non existent class: " + p[1])
        elif class_dir[p[1]]['visibility'] == 'private':
            raise KeyError("Can not extend from private class: " + p[1])
        else:
            current_func_dir.directory = class_dir[p[1]]['functions'].copy()
            var_table.table = class_dir[p[1]]['var_table'].copy()
            exe = class_dir[p[1]]['execution'].copy()
            size = class_dir[p[1]]['size'].copy()
            MemoryManager().class_counter_offset(size['c_int'], size['c_float'], size['c_string'], size['c_bool'])
    else:
        exe = []
    p[0] = [p[1], exe]


def p_class_3(p):
    '''class_3  : statementAux class_3
                | empty'''


def p_class_4(p):
    '''class_4  : module class_4
                | empty'''
    code_gen.current_scope = 'local'


# ---- END CLASS DEFINITION ---------

# ---- BEGIN MAIN DEFINITION ---------


def p_main(p):
    '''main : mainAux OPEN_PARENTHESIS CLOSED_PARENTHESIS block'''
    var_tables['main'] = current_func_dir.delete_var_table(p[1])
    code_gen.reset_t_counter()


def p_mainAux(p):
    '''mainAux : MAIN'''
    global current_table, code_gen
    current_func_dir.add_function('void', p[1], code_gen.counter)
    code_gen.current_scope = 'local'
    current_table = current_func_dir.get_var_table()
    p[0] = p[1]


# ---- END MAIN DEFINITION ---------

# ---- BEGIN VISIBILITY DEFINITION ---------


def p_visibility(p):
    '''visibility   : PUBLIC
                    | PRIVATE'''
    p[0] = p[1]


# ---- END VISIBILITY DEFINITION ---------

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
    global code_gen
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
    # Release Memory and Store clean vartable
    var_tables[p[1]] = current_func_dir.delete_var_table(p[1])
    # Reset temporal Counters
    code_gen.reset_t_counter()


# ---- END MODULE DEFINITION ---------

# ---- BEGIN MODULE_VOID DEFINITION ---------


def p_module_void(p):
    '''module_void  : module_voidAux block'''
    p[0] = p[1]


def p_module_voidAux(p):
    '''module_voidAux  : VOID ID params'''
    p[0] = p[2]
    current_func_dir.add_function(p[1], p[2], code_gen.counter)
    global current_table
    current_table = current_func_dir.get_var_table()


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
    current_func_dir.add_function(p[1], p[2], code_gen.counter)
    var_table.set_array(False)
    var_table.set_type(p[1])
    var_table.store_id(p[2])
    var_table.register('class', cte_table)
    global current_table
    current_table = current_func_dir.get_var_table()


def p_module_ret_1(p):
    '''module_ret_1 : statement module_ret_1
                    | empty'''


# ---- END MODULE_RET DEFINITION ---------

# ---- BEGIN PARAMS DEFINITION ---------


def p_params(p):
    '''params  : OPEN_PARENTHESIS params_1 CLOSED_PARENTHESIS'''


def p_paramsAux(p):
    '''paramsAux : type_atomic ID'''
    current_func_dir.store_param(p[1], p[2])


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
    global current_function, current_function_types, current_function_ret
    if current_function:
        tp = len(current_function_types)
        code_gen.validate_params(tp)
        code_gen.go_sub(current_function)
        code_gen.end_call()
        ret_type = current_function_ret
        if ret_type != "void":
            mem_dir = class_dir[p[1][0]]['var_table'][current_function]['virtual_address']
            p[0] = code_gen.call_return(str(p[1][1]) + '.' + str(mem_dir), ret_type)
            code_gen.addOperand(p[0])
        else:
            p[0] = current_function_ret
        current_function = None
        current_function_types = None
        current_function_ret = None
        code_gen.operators.pop()
    else:
        p[0] = 'attribute'


def p_object_callAux(p):
    '''object_callAux : ID POINT ID'''
    obj = p[1]
    if obj in current_table.table:
        if current_table.table[obj]['type'] not in ['int', 'float', 'bool', 'string']:
            class_name = current_table.table[obj]['type']
            memory = current_table.table[obj]['virtual_address']
        else:
            raise TypeError("Variable " + obj + " is not an object")
    elif obj in var_table.table:
        if var_table.table[obj]['type'] not in ['int', 'float', 'bool', 'string']:
            class_name = var_table.table[obj]['type']
            memory = var_table.table[obj]['virtual_address']
        else:
            raise TypeError("Variable " + obj + " is not an object")
    else:
        raise NameError("Unknown variable " + obj)

    element = p[3]
    v_list = class_dir[class_name]['var_table']
    f_list = class_dir[class_name]['functions']

    p[0] = [class_name, memory]

    if element in f_list:
        global current_function, current_function_types, current_function_ret
        current_function = element
        code_gen.add_mem(memory, class_name)
        current_function_types = list(f_list[element]['params'].values())
        current_function_ret = f_list[element]['return_type']
        code_gen.generate_era(element)
    elif element in v_list:
        code_gen.types.push(v_list[element]['type'])
        code_gen.addOperand(str(memory) + '.' + str(v_list[element]['virtual_address']))
    else:
        raise NameError(
            class_name + " objects have no attribute or method " + element)


def p_object_call_2(p):
    '''object_call_1    : object_callAux2 object_call_3 CLOSED_PARENTHESIS
                        | empty'''


def p_object_callAux2(p):
    '''object_callAux2 : OPEN_PARENTHESIS'''
    if not current_function:
        raise TypeError("Object attribute is not function")


def p_object_call_3(p):
    '''object_call_3    : object_callAux1 object_call_4
                        | empty'''


def p_object_call_4(p):
    '''object_call_4    : COMMA object_callAux1 object_call_4
                        | empty'''


def p_object_callAux1(p):
    '''object_callAux1 : expression'''
    code_gen.param_solve()
    tp = current_function_types
    if len(tp) > code_gen.par_counter:
        code_gen.param(tp[code_gen.par_counter]['type'],
                       tp[code_gen.par_counter]['virtual_address'])
    else:
        raise TypeError(
            "Function parameters exceed expected parameters")


def p_func_call(p):
    '''func_call : func_call_aux OPEN_PARENTHESIS func_call_1 CLOSED_PARENTHESIS'''
    global current_function, current_function_types, current_function_ret
    tp = len(current_function_types)
    code_gen.validate_params(tp)
    code_gen.go_sub(current_function)
    ret_type = current_function_ret
    if ret_type != "void":
        mem_dir = var_table.table[current_function]['virtual_address']
        p[0] = code_gen.call_return(mem_dir, ret_type)
        code_gen.addOperand(p[0])
    else:
        p[0] = current_function_ret
    current_function = None
    current_function_types = None
    current_function_ret = None
    code_gen.operators.pop()


def p_func_call_aux(p):
    '''func_call_aux : ID'''
    p[0] = p[1]
    if p[1] in current_func_dir.directory:
        code_gen.generate_era(p[1])
        global current_function, current_function_types, current_function_ret
        current_function = p[1]
        current_function_types = list(current_func_dir.directory[current_function]['params'].values())
        current_function_ret = current_func_dir.directory[current_function]['return_type']
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
    code_gen.param_solve()
    tp = current_function_types
    if len(tp) > code_gen.par_counter:
        code_gen.param(tp[code_gen.par_counter]['type'],
                       tp[code_gen.par_counter]['virtual_address'])
    else:
        raise TypeError(
            "Function parameters exceed expected parameters")


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
    code_gen.addOperator(p[2])


def p_assignation_1(p):
    '''assignation_1    : expression
                        | array_dec'''
    p[0] = p[1]


# ---- END ASSIGNATION DEFINITION ---------

# ---- BEGIN DECLARATION DEFINITION ---------


def p_declaration(p):
    '''declaration  : type_atomic declaration_1 SEMICOLON
                    | object_declaration'''
    tp = current_table.type_var
    current_table.register(code_gen.current_scope, cte_table)
    global object_queue
    for obj in object_queue:
        code_gen.add_object(tp, current_table.table[obj]['virtual_address'])
    object_queue = []


def p_declaration_1(p):
    '''declaration_1    : declaration_1Aux declaration_2
                        | declaration_1Aux2 declaration_3'''


def p_declaration_1Aux(p):
    '''declaration_1Aux    : id_arr'''
    if '[' in p[1]:
        elm = []
        for e in re.split("\[(.*?)\]", p[1]):
            if e != '':
                elm.append(e)
        current_table.store_id(elm[0])
        dims = []
        for i in range(1, len(elm)):
            dims.append(int(elm[i]))
        current_table.set_array(True)
        current_table.set_dims(dims)
    else:
        current_table.store_id(p[1])
        current_table.set_array(False)
        p[0] = p[1]


def p_declaration_1Aux2(p):
    '''declaration_1Aux2    : ID EQUALS'''
    current_table.store_id(p[1])
    current_table.set_array(False)
    code_gen.operators.push(p[2])
    current_table.register(code_gen.current_scope, cte_table)
    code_gen.types.push(current_table.table[p[1]]['type'])
    code_gen.addOperand(current_table.table[p[1]]['virtual_address'])


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
    global object_queue
    object_queue = current_table.queue


def p_object_declaration_1(p):
    '''object_declaration_1 : COMMA ID object_declaration_1
                            | empty'''
    if len(p) > 2:
        current_table.store_id(p[2])
        current_table.set_array(False)


def p_object_declarationAux(p):
    '''object_declarationAux : ID ID'''
    if p[1] in class_dir:
        current_table.set_type(p[1])
    else:
        raise TypeError("Class " + p[1] + " does not exist")
    current_table.store_id(p[2])
    current_table.set_array(False)


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
    code_gen.printing()


def p_printingAux(p):
    '''printingAux : PRINT OPEN_PARENTHESIS expression CLOSED_PARENTHESIS'''
    code_gen.final_solve()


# ---- END PRINTING DEFINITION ---------

# ---- BEGIN READING DEFINITION ---------


def p_reading(p):
    '''reading : READ OPEN_PARENTHESIS id_arr_var CLOSED_PARENTHESIS SEMICOLON'''
    code_gen.reading()


# ---- END READING DEFINITION ---------

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
    var_cte = cte_table.insert_cte(int(p[1]), 'int')
    code_gen.types.push("int")
    code_gen.addOperand(var_cte)


def p_var_cteAuxFLOAT(p):
    '''var_cteAuxFLOAT  : CTE_F'''
    p[0] = p[1]
    var_cte = cte_table.insert_cte(float(p[1]), 'float')
    code_gen.types.push("float")
    code_gen.addOperand(var_cte)


def p_var_cteAuxSTRING(p):
    '''var_cteAuxSTRING  : CTE_S'''
    p[0] = p[1]
    var_cte = cte_table.insert_cte(p[1], 'string')
    code_gen.types.push("string")
    code_gen.addOperand(var_cte)


def p_var_cteAuxBOOL(p):
    '''var_cteAuxBOOL   : TRUE
                        | FALSE '''
    p[0] = p[1]
    var_cte = cte_table.insert_cte(p[1], 'bool')
    code_gen.types.push("bool")
    code_gen.addOperand(var_cte)


# ---- END VAR_CTE DEFINITION ---------

# ---- BEGIN TYPE_ATOMIC DEFINITION ---------


def p_type_atomic(p):
    '''type_atomic  : INT
                    | FLOAT
                    | STRING
                    | BOOL'''
    p[0] = p[1]
    current_table.set_type(p[1])


# ---- END TYPE_ATOMIC DEFINITION ---------

# ---- BEGIN TYPE DEFINITION ---------


# def p_type(p):
#     '''type : type_atomic
#             | ID'''
#     p[0] = p[1]


# ---- END TYPE DEFINITION ---------

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
    if current_arr:
        code_gen.set_dim(current_arr['dims'], cte_table.insert_cte(0, 'int'))
    else:
        raise TypeError("Variable is not array")


def p_arr_exp(p):
    '''arr_exp  : arr_expAux expression CLOSED_SQRT_BRACKET'''
    p[0] = p[1] + p[2] + p[3]
    code_gen.arr_solve()
    code_gen.operators.pop()


def p_arr_expAux(p):
    '''arr_expAux  : OPEN_SQRT_BRACKET'''
    p[0] = p[1]
    code_gen.operators.push('ARR')


# ---- END ARR_DIM DEFINITION ---------

# ---- BEGIN ID_ARR DEFINITION --------


def p_id_arr_var(p):
    '''id_arr_var : id_arr_varAuxID arr_exp_loop'''
    global current_arr, current_arr_id
    if current_arr and p[1] == current_arr_id:
        cte_mem = cte_table.insert_cte(current_arr['virtual_address'], 'int')
        code_gen.final_arr(cte_mem, current_arr['type'], current_arr['dims'])
        current_arr = None
    p[0] = p[1]


def p_id_arrID(p):
    '''id_arr_varAuxID  : ID'''
    p[0] = p[1]
    global current_arr, current_arr_id

    if p[1] not in current_table.table and current_table != var_table and current_table != global_var_table:
        if p[1] not in var_table.table:
            if global_var_table.get_is_array(p[1]):
                current_arr = global_var_table.table[p[1]]
                current_arr_id = p[1]
            else:
                code_gen.types.push(global_var_table.get_type(p[1]))
                code_gen.addOperand(
                    global_var_table.table[p[1]]['virtual_address'])
        else:
            if var_table.get_is_array(p[1]):
                current_arr = var_table.table[p[1]]
                current_arr_id = p[1]
            else:
                code_gen.types.push(var_table.get_type(p[1]))
                code_gen.addOperand(
                    var_table.table[p[1]]['virtual_address'])
    else:
        if current_table.get_is_array(p[1]):
            current_arr = current_table.table[p[1]]
            current_arr_id = p[1]
        else:
            code_gen.types.push(current_table.get_type(p[1]))
            code_gen.addOperand(current_table.table[p[1]]['virtual_address'])


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


def export_quads():
    quads = ""
    for quad in code_gen.quadruples:
        arr = [str(p) if p is not None else '$' for p in quad]
        quads += arr[0] + " " + arr[1] + " " + arr[2] + " " + arr[3] + "\n"
    return quads


def export_classes_size():
    size_export = ""
    for key in class_dir:
        size_export += key
        for dim_size in class_dir[key]['size']:
            size_export += " " + str(class_dir[key]['size'][dim_size])
        size_export += "\n"
    for var in program_vars['program']:
        size_export += var
        for dim_size in program_vars['program'][var]['size']:
            size_export += " " + \
                           str(program_vars['program'][var]['size'][dim_size])
        size_export += "\n"
    return size_export


def export_class_signature():
    size_export = ""
    for key in class_dir:
        size_export += key
        for exe in class_dir[key]['execution']:
            size_export += " " + str(exe)
        size_export += "\n"
    return size_export


def export_functions_size():
    size_export = ""
    for key in class_dir:
        for fn in class_dir[key]['functions']:
            rc = " "
            for dim_size in class_dir[key]['functions'][fn]['size']:
                rc += str(class_dir[key]['functions'][fn]
                          ['size'][dim_size]) + " "
            size_export += key + " " + fn + rc + "\n"
    return size_export


def export_functions_signature():
    signatures_export = ""
    for key in class_dir:
        for fn in class_dir[key]['functions']:
            rc = " " + class_dir[key]['functions'][fn]['return_type'] + \
                 " " + str(class_dir[key]['functions'][fn]['position']) + " "
            for param in class_dir[key]['functions'][fn]['params']:
                rc += str(class_dir[key]['functions'][fn]
                          ['params'][param]['type']) + " "
            signatures_export += key + " " + fn + rc + "\n"
    return signatures_export


def export_ret_functions_address():
    addresses = ""
    for key in class_dir:
        for fn in class_dir[key]['functions']:
            if fn in class_dir[key]['var_table']:
                addresses += key + " " + fn + " " + \
                             str(class_dir[key]['var_table']
                                 [fn]['virtual_address']) + "\n"
    return addresses


def export_constants():
    constants = ""
    for cte in cte_table.table:
        constants += str(cte_table.table[cte]
                         ['virtual_address']) + " " + str(cte) + "\n"
    return constants


def generateObj():
    dir_path = 'output'
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    output = export_quads() + "\n" + export_functions_signature() + "\n" + export_ret_functions_address() + "\n" + \
             export_functions_size() + "\n" + export_class_signature() + "\n" + export_classes_size() + "\n" \
             + export_constants()
    filewriter = open(dir_path + "/out.obj", 'w')
    filewriter.write(output)


# Validate if a file was passed through the command line arguments.
if len(sys.argv) > 1:
    with open(sys.argv[1], 'r') as file:
        file_content = file.read().replace('\n', ' ')

    # Parse the file content.
    result = parser.parse(file_content)
    if not err:
        generateObj()
