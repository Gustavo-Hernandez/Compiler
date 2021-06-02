# ------------------------------------------------------------
# code_gen.py
# A01364749 Gustavo Hernandez Sanchez
# A01364701 Luis Miguel Maawad Hinojosa
# ------------------------------------------------------------

from components.mem_manager import MemoryManager
from .stack import Stack  # pylint: disable=relative-beyond-top-level


# Class definition for quadruple generator on compiler
class CodeGenerator:
    # Class needs stacks for operators, operands and types to generate quadruples
    # Class needs a stack for jumps in order to generate 'goto' quadruples
    # Class uses lists to store its quadruples
    # Class stores the position of mains 'goto' quadruple in order to give it the
    # location it must jump to once it finds main
    # Class maintains counter for function parameters in order to check with semantics if the
    # correct number of parameters have been passed
    # Class uses counter to know what is the current quadruple being worked on
    # Class maintains a dimension counter in order to check with semantics if the
    # correct number of dimensions have been called
    # Class uses semantic cube to check if the operation types are valid
    # and what is the resulting type of said operation
    def __init__(self):
        self.operands = Stack()
        self.operators = Stack()
        self.types = Stack()
        self.jumps = Stack()
        self.quadruples = []
        self.current_scope = 'global'
        self.main_quad = 0
        self.par_counter = 0
        self.t_counter = 0
        self.counter = 1
        self.dim_counter = 0
        self.cube = {
            'int': {
                'int': {
                    '+': 'int',
                    '-': 'int',
                    '*': 'int',
                    '/': 'float',
                    '>': 'bool',
                    '<': 'bool',
                    '==': 'bool',
                    '!=': 'bool'
                },
                'float': {
                    '+': 'float',
                    '-': 'float',
                    '*': 'float',
                    '/': 'float',
                    '>': 'bool',
                    '<': 'bool',
                    '==': 'bool',
                    '!=': 'bool'
                },
                'string': {
                    '+': 'string'
                }
            },
            'float': {
                'int': {
                    '+': 'float',
                    '-': 'float',
                    '*': 'float',
                    '/': 'float',
                    '>': 'bool',
                    '<': 'bool',
                    '==': 'bool',
                    '!=': 'bool'
                },
                'float': {
                    '+': 'float',
                    '-': 'float',
                    '*': 'float',
                    '/': 'float',
                    '>': 'bool',
                    '<': 'bool',
                    '==': 'bool',
                    '!=': 'bool'
                },
                'string': {
                    '+': 'string'
                }
            },
            'bool': {
                'bool': {
                    '+': 'bool',
                    '-': 'bool',
                    '*': 'bool',
                    '/': 'bool',
                    '>': 'bool',
                    '<': 'bool',
                    '==': 'bool',
                    '!=': 'bool',
                    'and': 'bool',
                    'or': 'bool'
                }
            },
            'string': {
                'string': {
                    '+': 'string',
                    '==': 'string'
                },
                'int': {
                    '+': 'string'
                },
                'float': {
                    '+': 'string'
                },
                'double': {
                    '+': 'string'
                }
            }
        }

    # Function adds memory address of sent operand to stack
    def addOperand(self, value):
        self.operands.push(value)

    # Function adds operator to stack
    def addOperator(self, value):
        self.operators.push(value)

    # Function used to solve previous operation if and/or operators are added,
    # and pushes said operator to stack
    def addOperator_4(self, value):
        op_top = self.operators.top()
        if op_top in ["+", "*", "-", "/", ">", "<", "==", "!="]:
            self.solve()
        self.operators.push(value)

    # Function used to solve previous operation if a boolean operator is added,
    # and pushes said operator to stack
    def addOperator_3(self, value):
        op_top = self.operators.top()
        if op_top in ["+", "*", "-", "/"]:
            self.solve()
        self.operators.push(value)

    # Function used to solve previous operation if a multiplication or division is added,
    # and pushes said operator to stack
    def addOperator_2(self, value):
        op_top = self.operators.top()
        if op_top == "*" or op_top == "/":
            self.solve()
        self.operators.push(value)

    # Function used to solve previous operation if a plus or minus is added,
    # and pushes said operator to stack
    def addOperator_1(self, value):
        op_top = self.operators.top()
        if op_top not in ['=', None, '(', '>', '==', '!=', '<', 'and', 'or', 'ARR', 'FUNC']:
            self.solve()
            self.addOperator_1(value)
        else:
            self.operators.push(value)

    # Function solves current operation on the top of the stack and pushes back the resulting operand back to the stack
    def solve(self):
        op_der = self.operands.pop()
        op_iz = self.operands.pop()
        operator = self.operators.pop()
        tp_der = self.types.pop()
        tp_iz = self.types.pop()

        if operator != '=':
            try:
                tp_res = self.cube[tp_iz][tp_der][operator]
            except:
                raise TypeError("Invalid operand types: " + tp_iz + " " +
                                operator + " " + tp_der)

            key = MemoryManager().request_address('temp', tp_res)
            self.t_counter += 1
            self.quadruples.append([operator, op_iz, op_der, key])
            self.types.push(tp_res)
            self.addOperand(key)
            self.counter += 1
        else:
            if tp_der == tp_iz:
                self.quadruples.append([operator, op_der, None, op_iz])
                self.counter += 1
            else:
                raise TypeError("Assignation types do not match ",
                                op_der, op_iz, operator)

    # Function used to solve before generating statement quadruple
    def final_solve(self):
        while self.operators.size() > 0:
            self.solve()

    # Function used to solve for an array dimension expression
    def arr_solve(self):
        while self.operators.top() != 'ARR':
            self.solve()

    # Function used to solve for a function parameter expression
    def param_solve(self):
        while self.operators.top() != 'FUNC':
            self.solve()

    # Function used to solve for expression inside a parenthesis
    def factor_solve(self):
        while self.operators.top() != '(':
            self.solve()
        self.operators.pop()

    # Function manages printing quadruple and only proceeds if operand is of string type
    def printing(self):
        res_type = self.types.pop()
        res_operand = self.operands.pop()
        if res_type == "string":
            self.quadruples.append(['print', None, None, res_operand])
            self.counter += 1
        else:
            raise TypeError(
                "Type mismatch: expected string, received: " + res_type)

    # Function generates 'gotoF' quadruples for if/else statements
    def condition_1(self):
        expr_type = self.types.pop()
        if expr_type != 'bool':
            raise TypeError(
                "Type mismatch: expected bool, received: " + expr_type)
        else:
            expr_res = self.operands.pop()
            self.quadruples.append(['gotoF', expr_res, None, None])
            self.jumps.push(self.counter - 1)  # Adding current line
            self.counter += 1

    # Function sets jump value for 'goto' quadruples in if/else statements
    def condition_2(self):
        end = self.jumps.pop()
        self.fill(end, self.counter)

    # Function generates 'goto' quadruple for ture portion of if/else statements
    def condition_3(self):
        self.quadruples.append(['goto', None, None, None])
        false_position = self.jumps.pop()
        self.jumps.push(self.counter - 1)
        self.counter += 1
        self.fill(false_position, self.counter)

    # Function saves beginning of loop statements in quadruples
    def loop_1(self):
        self.jumps.push(self.counter)

    # Function generates 'gotoF' quadruples for loop statements
    def loop_2(self):
        expr_type = self.types.pop()
        if expr_type != 'bool':
            raise TypeError(
                "Type mismatch expected: bool, received: " + expr_type)
        else:
            expr_res = self.operands.pop()
            self.quadruples.append(['gotoF', expr_res, None, None])
            self.jumps.push(self.counter - 1)  # Adding current line
            self.counter += 1

    # Function generates 'goto' quadruple at the end of all loops
    def loop_3(self):
        end = self.jumps.pop()
        return_pos = self.jumps.pop()
        self.quadruples.append(['goto', None, None, return_pos])
        self.counter += 1
        self.fill(end, self.counter)

    # TODO check if t counter is necessary
    def reset_t_counter(self):
        self.t_counter = 0
        MemoryManager().reset_module_context()

    # Function used to give value to all 'goto' quadruples
    def fill(self, pos, value):
        self.quadruples[pos][3] = value

    # Function adds "End of function" support quadruple
    def end_func(self):
        self.quadruples.append(['ENDFUNC', None, None, None])
        self.counter += 1

    # Function adds "End of class" support quadruple
    def end_class(self):
        self.quadruples.append(['ENDCLS', None, None, None])
        self.counter += 1

    # Function adds "End of method call" support quadruple
    def end_call(self):
        self.quadruples.append(['ENDCLL', None, None, None])
        self.counter += 1

    # Function adds 'goto' quadruple for main
    def add_main(self):
        self.quadruples.append(['goto', None, None, None])
        self.main_quad = self.counter - 1
        self.counter += 1

    # Function gives jump value for main's 'goto' quadruple
    def add_main_dir(self, val):
        self.fill(self.main_quad, val)

    # Function adds "End of program" support quadruple
    def end_prog(self):
        self.quadruples.append(['END', None, None, None])

    # Function adds "Memory Allocation (ERA)" support quadruple, and sets 'func' operator to manage parameters
    # Function receives function name
    def generate_era(self, func):
        self.quadruples.append(['ERA', func, None, None])
        self.counter += 1
        self.operators.push('FUNC')

    # Function adds 'param' quadruple and checks for mismatch in parameter types
    # Function receives parameter type and address
    def param(self, tp, address):
        exp = self.types.pop()
        if exp != tp:
            raise TypeError(
                "Mismatch on parameter types: expected: " + tp + ", received: " + exp)
        else:
            self.quadruples.append(
                ['PARAM', self.operands.pop(), None, address])
            self.par_counter += 1
            self.counter += 1

    # Function checks if all parameters form function have been sent
    # Function receives number of function parameters
    def validate_params(self, length):
        if length > self.par_counter:
            raise TypeError(
                "Function missing parameters")

    # Function sets 'return' quadruple and checks if the return type for the function matches
    # Function receives return type
    def add_return(self, tp):
        res = self.types.pop()

        if res != tp:
            raise TypeError(
                "Mismatch on return type: expected: " + tp + ", received: " + res)
        else:
            val = self.operands.pop()
            self.quadruples.append(['RETURN', None, None, val])
            self.counter += 1

    # Function adds 'gosub' support quadruple
    # Function receives function name
    def go_sub(self, func):
        self.par_counter = 0
        self.quadruples.append(['GOSUB', None, None, func])
        self.counter += 1

    # Function adds an '=' quadruple that saves the value of the function that was called into a temporal variable
    # Function receives function variable address and return type
    def call_return(self, func, tp):
        key = MemoryManager().request_address('temp', tp)
        self.t_counter += 1
        self.quadruples.append(['=', func, None, key])
        self.counter += 1
        self.types.push(tp)
        return str(key)

    # Dev function used to neatly print all quadruples
    def print_quads(self):
        print("\n----  Quadruples  -----")
        i = 1
        for quad in self.quadruples:
            print(i, quad)
            i += 1

    # Function checks if array matches its established number of dimensions
    # Function adds dimensions calculations to base memory address and appends the result as a pointer
    # Function receives array type, dimensions, and address
    def final_arr(self, va, tp, dims):
        if self.dim_counter != len(dims):
            raise IndexError(
                "Array dimensions do not match with established " + str(len(dims)) + " dimensions")

        operand = self.operands.pop()
        self.types.pop()

        key = MemoryManager().request_address('pointers', 'int')
        self.t_counter += 1

        self.quadruples.append(['+', operand, va, key])

        # Added pointer key
        self.operands.push("(" + str(key) + ")")
        self.types.push(tp)
        self.counter += 1
        self.dim_counter = 0

    # Function generates a '*' quadruple used to multiply dimension by value of m
    # Function receives index and m
    def set_dim_mul(self, op, r):
        key = MemoryManager().request_address('temp', 'int')
        self.t_counter += 1

        self.quadruples.append(['*', op, r, key])
        self.counter += 1

        return key

    # Function generates sum with previous values of indexes
    # Function receives the right operand for quadruple
    def set_dim_sum(self, r_op):
        l_op = self.operands.pop()
        self.types.pop()

        key = MemoryManager().request_address('temp', 'int')
        self.t_counter += 1

        self.quadruples.append(['+', l_op, r_op, key])
        self.counter += 1

        self.operands.push(key)
        self.types.push('int')

    # Function checks if index is an integer and if the array has exceeded the indicated dimensions
    # Function adds 'ver' quadruple using array dimensions and generates further calculation quadruples
    # Function receives array dimensions and virtual address for 0
    def set_dim(self, dims, cypher):
        d = len(dims)
        operand = self.operands.pop()
        tp = self.types.pop()

        if tp != 'int':
            raise TypeError('Index must be an integer value, received: ', tp)

        if self.dim_counter == d:
            raise IndexError(
                "Array dimensions exceed declared dimensions of ", d)

        self.quadruples.append(
            ['VER', operand, cypher, dims[self.dim_counter][0]])
        self.counter += 1

        if self.dim_counter == 0:
            if d != 1:
                res = self.set_dim_mul(operand, dims[self.dim_counter][1])
                self.operands.push(res)
            else:
                self.operands.push(operand)
            self.types.push('int')
        else:
            if self.dim_counter == d - 1:
                self.set_dim_sum(operand)
            else:
                operand = self.set_dim_mul(operand, dims[self.dim_counter][1])
                self.set_dim_sum(operand)

        self.dim_counter += 1

    # Function adds quadruple for reading, which includes address and type used by vm to validate read
    def reading(self):
        val = self.operands.pop()
        tp = self.types.pop()

        self.quadruples.append(['READ', tp, None, val])
        self.counter += 1

    # Function adds support quadruple 'obj' used to allocate memory when an object is declared
    # Function adds support quadruple 'objsub' that is used to visit all inheritance class statements
    # Function receives class name and memory address
    def add_object(self, class_name, val):
        self.quadruples.append(['OBJ', class_name, None, val])
        self.quadruples.append(['OBJSUB', None, None, None])
        self.counter += 2

    # Function adds support quadruple 'mem' used to allocate memory for an object function call
    # Function receives class name and memory address
    def add_mem(self, val, class_name):
        self.quadruples.append(['MEM', class_name, None, val])
        self.counter += 1
