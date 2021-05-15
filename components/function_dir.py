from .variable_table import VariableTable  # pylint: disable=relative-beyond-top-level


class FunctionDirectory:
    def __init__(self):
        self.directory = {}
        self.var_table = None
        self.params = {}

    def add_function(self, return_type, id, pos):
        if not id in self.directory:
            self.directory[id] = {
                'return_type': return_type, 'params': self.params, 'position': pos, 'var_table': VariableTable()}
        else:
            print("[Error] Duplicate function: " + id)
        self.params = {}

    def store_param(self, type_atomic, id):
        if not id in self.params:
            self.params[id] = {'type': type_atomic}
        else:
            print("[Error] Duplicate function: " + id)

    def get_var_table(self, id):
        return self.directory[id]['var_table']

    def print(self):
        for f in self.directory:
            print("\n-------" + f + "---------")
            print("Func info: ", self.directory[f])
            print("Func Vartable: ", end=" ")
            self.directory[f]['var_table'].print()
