from components.mem_manager import MemoryManager
from .variable_table import VariableTable  # pylint: disable=relative-beyond-top-level


class FunctionDirectory:

    def __init__(self, global_vartable):
        self.directory = {}
        self.var_table = None
        self.params = {}
        self.global_vartable = global_vartable

    def add_function(self, return_type, id, pos):
        if not id in self.directory:
            if not id in self.global_vartable.table:
                self.var_table = VariableTable()
                self.directory[id] = {
                    'return_type': return_type, 'params': self.params, 'position': pos}
            else:
                raise KeyError("Duplicate identifier: " + id)
        else:
            raise KeyError("Duplicate function: " + id)

    def store_param(self, type_atomic, id):
        if not id in self.params:
            self.params[id] = {'type': type_atomic}
            print(id, type_atomic)
            MemoryManager().request_address('local', type_atomic)
        else:
            raise KeyError("Duplicate parameter: " + id)

    def get_var_table(self):
        return self.var_table

    def delete_var_table(self, id):
        # TODO: ADD PARAMS TO SIZE CALCULATION
        self.directory[id]['size'] = MemoryManager().get_module_counter()
        self.var_table = None
        self.params = {}

    def print(self):
        for f in self.directory:
            print("\n-------" + f + "---------")
            print("Func info: ", self.directory[f])
