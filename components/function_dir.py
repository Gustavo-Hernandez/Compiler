from .variable_table import VariableTable  # pylint: disable=relative-beyond-top-level


class FunctionDirectory:

    def __init__(self, global_vartable):
        self.directory = {}
        self.var_table = None
        self.params = {}

    def add_function(self, return_type, id, pos):
        if not id in self.directory:
            if not id in self.global_vartable.table:
                self.var_table = VariableTable()
                self.directory[id] = {
                    'return_type': return_type, 'params': self.params, 'pos': pos}
            else:
                raise KeyError("Duplicate identifier: " + id)
        else:
            raise KeyError("Duplicate function: " + id)

    def store_param(self, type_atomic, id):
        if not id in self.params:
            self.params[id] = {'type': type_atomic}
        else:
            raise KeyError("Duplicate parameter: " + id)

    def get_var_table(self):
        return self.var_table

    def delete_var_table(self, id):
        self.directory[id]['size'] = self.calculateSize()
        self.params = {}
        self.var_table = None
        pass

    def calculateSize(self):
        total_size = 0

        for key in self.params:
            tp = self.params[key]['type']
            total_size += self.getSizeOf(tp)

        for key in self.var_table.table:
            tp = self.var_table.table[key]['type']
            total_size += self.getSizeOf(tp)

        return total_size

    def getSizeOf(self, tp):
        if tp in ['int', 'float', 'bool']:
            return 24
        elif tp in ['string', 'double']:
            return 48
        return 0

    def print(self):
        for f in self.directory:
            print("\n-------" + f + "---------")
            print("Func info: ", self.directory[f])
