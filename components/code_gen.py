from .stack import Stack  # pylint: disable=relative-beyond-top-level


class CodeGenerator:
    def __init__(self):
        self.operands = Stack()
        self.operators = Stack()
        self.types = Stack()
        self.jumps = Stack()
        self.quadruples = []
        self.avail = []
        self.counter = 1
        self.t_counter = 0
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
        if op_top not in ['=', None, '(', '>', '==', '!=', '<', 'and', 'or']:
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

            key = "t" + str(self.t_counter)
            self.t_counter += 1
            self.quadruples.append([operator, op_iz, op_der, key])
            self.types.push(tp_res)
            self.addOperand(key)
            self.counter += 1
        else:
            if(tp_der == tp_iz):
                self.quadruples.append([operator, op_der, None, op_iz])
                self.counter += 1
            else:
                raise TypeError("Assignation types do not match")

    def final_solve(self):
        while self.operators.size() > 0:
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
            self.jumps.push(self.counter-1)  # Adding current line
            self.counter += 1

    def condition_2(self):
        end = self.jumps.pop()
        self.fill(end, self.counter)

    def condition_3(self):
        self.quadruples.append(['goto', None, None, None])
        false_position = self.jumps.pop()
        self.jumps.push(self.counter-1)
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
            self.jumps.push(self.counter-1)  # Adding current line
            self.counter += 1

    def loop_3(self):
        end = self.jumps.pop()
        return_pos = self.jumps.pop()
        self.quadruples.append(['goto', None, None, return_pos])
        self.jumps.push(self.counter-1)  # Adding current line
        self.counter += 1
        self.fill(end, self.counter)

    def reset_t_counter(self):
        self.t_counter = 0

    def fill(self, pos, value):
        self.quadruples[pos][3] = value
