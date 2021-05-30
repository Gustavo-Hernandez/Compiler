from components.mem_manager import MemoryManager
from .variable_table import VariableTable  # pylint: disable=relative-beyond-top-level


class FunctionDirectory:

    def __init__(self):
        self.directory = {}
        self.var_table = None
        self.params = {}
        self.global_vartable = VariableTable()
        self.class_vartable = VariableTable()

    def add_function(self, return_type, id, pos):
        if not id in self.directory:
            if not id in self.class_vartable.table:
                if not id in self.global_vartable.table:
                    self.var_table = VariableTable()
                    if id == 'program':
                        self.global_vartable = self.var_table
                    self.directory[id] = {
                        'return_type': return_type, 'params': self.params, 'position': pos}
                    for param in self.params:
                        type_atomic = self.params[param]['type']
                        address = self.params[param]['virtual_address']
                        self.var_table.table[param] = {
                            'type': type_atomic, 'virtual_address': address, 'is_array': False}
                else:
                    raise KeyError("Duplicate identifier: " + id)
            else:
                raise KeyError(
                    "Duplicate identifier, declared in class: " + id)
        else:
            raise KeyError("Duplicate function: " + id)

    def store_param(self, type_atomic, id):
        if not id in self.params:
            address = MemoryManager().request_address('local', type_atomic)
            self.params[id] = {'type': type_atomic, "virtual_address": address}
        else:
            raise KeyError("Duplicate parameter: " + id)

    def get_var_table(self):
        return self.var_table

    def delete_var_table(self, id):
        self.directory[id]['size'] = MemoryManager().get_module_counter()
        clean_vartable = self.clean_export()
        self.var_table = None
        self.params = {}
        return clean_vartable

    def store_global_vars(self, id):
        self.directory[id]['size'] = MemoryManager().get_global_counter()
        clean_vartable = self.clean_export()
        self.var_table = None
        self.params = {}
        return clean_vartable

    def print(self):
        for f in self.directory:
            print("\n-------" + f + "---------")
            print("Func info: ", self.directory[f])

    # Cleans var table before export.
    # Returns only the data needed by VM.
    def clean_export(self):
        clean_table = {}
        if self.var_table != None:
            for var in self.var_table.table:
                clean_var = {}
                clean_var['type'] = self.var_table.table[var]['type']
                clean_var['virtual_address'] = self.var_table.table[var]['virtual_address']
                clean_table[var] = clean_var
            return clean_table
