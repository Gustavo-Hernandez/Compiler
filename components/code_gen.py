import math
from components.mem_manager import MemoryManager
from .stack import Stack  # pylint: disable=relative-beyond-top-level


class CodeGenerator:
    def __init__(self):
        self.operands = Stack()
        self.operators = Stack()
        self.types = Stack()
        self.jumps = Stack()
        self.quadruples = []
        self.avail = []
        self.par_counter = 0
        self.t_counter = 0
        self.counter = 1
        self.dim_counter = 0
        self.current_scope = 'global'
        self.cube = {
            'int': {
                'int': {
                    '+': 'int',
                    '-': 'int',
                    '*': 'int',
                    '/': 'float',
                    '>': 'bool',
                    '<': 'bool',
                    '==': 'bool'
                },
                'float': {
                    '+': 'float',
                    '-': 'float',
                    '*': 'float',
                    '/': 'float',
                    '>': 'bool',
                    '<': 'bool',
                    '==': 'bool'
                },
                'double': {
                    '+': 'double',
                    '-': 'double',
                    '*': 'double',
                    '/': 'double',
                    '>': 'bool',
                    '<': 'bool',
                    '==': 'bool'
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
                    '==': 'bool'
                },
                'float': {
                    '+': 'float',
                    '-': 'float',
                    '*': 'float',
                    '/': 'float',
                    '>': 'bool',
                    '<': 'bool',
                    '==': 'bool'
                },
                'double': {
                    '+': 'double',
                    '-': 'double',
                    '*': 'double',
                    '/': 'double',
                    '>': 'bool',
                    '<': 'bool',
                    '==': 'bool'
                },
                'string': {
                    '+': 'string'
                }
            },
            'double': {
                'int': {
                    '+': 'double',
                    '-': 'double',
                    '*': 'double',
                    '/': 'double',
                    '>': 'bool',
                    '<': 'bool',
                    '==': 'bool'
                },
                'float': {
                    '+': 'double',
                    '-': 'double',
                    '*': 'double',
                    '/': 'double',
                    '>': 'bool',
                    '<': 'bool',
                    '==': 'bool'
                },
                'double': {
                    '+': 'double',
                    '-': 'double',
                    '*': 'double',
                    '/': 'double',
                    '>': 'bool',
                    '<': 'bool',
                    '==': 'bool'
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

    def addOperand(self, value):
        self.operands.push(value)

    def addOperator(self, value):
        self.operators.push(value)

    def addOperator_4(self, value):
        op_top = self.operators.top()
        if op_top in ["+", "*", "-", "/", ">", "<", "==", "!="]:
            self.solve()
        self.operators.push(value)

    def addOperator_3(self, value):
        op_top = self.operators.top()
        if op_top in ["+", "*", "-", "/"]:
            self.solve()
        self.operators.push(value)

    def addOperator_2(self, value):
        op_top = self.operators.top()
        if op_top == "*" or op_top == "/":
            self.solve()
        self.operators.push(value)

    # Adding a plus or minus
    def addOperator_1(self, value):
        op_top = self.operators.top()
        if op_top not in ['=', None, '(', '>', '==', '!=', '<', 'and', 'or', 'ARR']:
            self.solve()
            self.addOperator_1(value)
        else:
            self.operators.push(value)

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

    def final_solve(self):
        while self.operators.size() > 0:
            self.solve()

    def arr_solve(self):
        while self.operators.top() != 'ARR':
            self.solve()

    def factor_solve(self):
        while self.operators.top() != '(':
            self.solve()
        self.operators.pop()

    def printing(self):
        res_type = self.types.pop()
        res_operand = self.operands.pop()
        if res_type == "string":
            self.quadruples.append(['print', None, None, res_operand])
            self.counter += 1
        else:
            raise TypeError(
                "Type mismatch: expected string, received: " + res_type)

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

    def condition_2(self):
        end = self.jumps.pop()
        self.fill(end, self.counter)

    def condition_3(self):
        self.quadruples.append(['goto', None, None, None])
        false_position = self.jumps.pop()
        self.jumps.push(self.counter - 1)
        self.counter += 1
        self.fill(false_position, self.counter)

    def loop_1(self):
        self.jumps.push(self.counter)

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

    def loop_3(self):
        end = self.jumps.pop()
        return_pos = self.jumps.pop()
        self.quadruples.append(['goto', None, None, return_pos])
        self.jumps.push(self.counter - 1)  # Adding current line
        self.counter += 1
        self.fill(end, self.counter)

    def reset_t_counter(self):
        self.t_counter = 0
        MemoryManager().reset_module_context()

    def fill(self, pos, value):
        self.quadruples[pos][3] = value

    def end_func(self):
        self.quadruples.append(['ENDFUNC', None, None, None])
        self.counter += 1

    def add_main(self):
        self.quadruples.append(['goto', None, None, None])
        self.jumps.push(self.counter-1)
        self.counter += 1

    def add_main_dir(self, val):
        pos = self.jumps.pop()
        self.fill(pos, val)

    def end_prog(self):
        self.quadruples.append(['END', None, None, None])

    def generate_era(self, func):
        self.quadruples.append(['ERA', func, None, None])
        self.counter += 1

    def param(self, tp):
        exp = self.types.pop()

        if exp != tp:
            raise TypeError(
                "Mismatch on parameter types: expected: " + tp + ", received: " + exp)
        else:
            self.quadruples.append(
                ['PARAM', self.operands.pop(), None, 'par' + str(self.par_counter)])
            self.par_counter += 1
            self.counter += 1

    def validate_params(self, length):
        if length > self.par_counter:
            raise TypeError(
                "Function missing parameters")

    def add_return(self, tp):
        res = self.types.pop()

        if res != tp:
            raise TypeError(
                "Mismatch on return type: expected: " + tp + ", received: " + res)
        else:
            self.quadruples.append(['RETURN', None, None, self.operands.pop()])
            self.counter += 1

    def go_sub(self, func):
        self.par_counter = 0
        self.quadruples.append(['GOSUB', None, None, func])
        self.counter += 1

    def call_return(self, func, tp):
        key = MemoryManager().request_address('temp', tp)
        self.t_counter += 1
        self.quadruples.append(['=', func, None, key])
        self.counter += 1
        self.types.push(tp)
        return str(key)

    def print_quads(self):
        print("\n----  Quadruples  -----")
        i = 1
        for quad in self.quadruples:
            print(i, quad)
            i += 1

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
        self.operands.push(key)
        self.types.push(tp)
        self.counter += 1
        self.dim_counter = 0

    def set_dim_mul(self, op, r):
        key = MemoryManager().request_address('temp', 'int')
        self.t_counter += 1

        self.quadruples.append(['*', op, r, key])
        self.counter += 1

        return key

    def set_dim_sum(self, r_op):
        l_op = self.operands.pop()
        self.types.pop()

        key = MemoryManager().request_address('temp', 'int')
        self.t_counter += 1

        self.quadruples.append(['+', l_op, r_op, key])
        self.counter += 1

        self.operands.push(key)
        self.types.push('int')

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
            ['VER', operand, cypher, dims[self.dim_counter][0] - 1])
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
