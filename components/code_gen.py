from .stack import Stack  # pylint: disable=relative-beyond-top-level


class CodeGenerator:
    def __init__(self):
        self.operands = Stack()
        self.operators = Stack()
        self.types = Stack()
        self.quadruples = []
        self.avail = []
        self.counter = 0
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

    def addOperator_2(self, value):
        op_top = self.operators.top()
        if op_top == "*" or op_top == "/":
            self.solve()
            self.operators.push(value)
        else:
            self.operators.push(value)

    # Adding a plus or minus
    def addOperator_1(self, value):
        op_top = self.operators.top()
        if op_top != '=':
            self.solve()
            self.operators.push(value)
        else:
            self.operators.push(value)
        # Todo add value after solution

    def solve(self):
        op_der = self.operands.pop()
        op_iz = self.operands.pop()
        operator = self.operators.pop()
        key = "t" + str(len(self.quadruples)+1)
        self.quadruples.append([operator, op_iz, op_der, key])
        self.addOperand(key)

    def increase_counter(self):
        self.counter += 1
