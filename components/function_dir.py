# ------------------------------------------------------------
# function_dir.py
# A01364749 Gustavo Hernandez Sanchez
# A01364701 Luis Miguel Maawad Hinojosa
# ------------------------------------------------------------

from components.mem_manager import MemoryManager
from .variable_table import VariableTable  # pylint: disable=relative-beyond-top-level

# Class to generate dictionaries of functions
class FunctionDirectory:
    # Class manages dictionary, params dictionary, variable table and access to class and global variable table
    def __init__(self):
        self.directory = {}
        self.var_table = None
        self.params = {}
        self.global_vartable = VariableTable()
        self.class_vartable = VariableTable()

    # Function manages function insertion, by validating that id
    # does not exist in directory and saving parameters and sizes
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

    # Function stores parameter to params dictionary
    # Function receives parameter type and id
    def store_param(self, type_atomic, id):
        if not id in self.params:
            address = MemoryManager().request_address('local', type_atomic)
            self.params[id] = {'type': type_atomic, "virtual_address": address}
        else:
            raise KeyError("Duplicate parameter: " + id)

    # Function used to obtain current variable table
    def get_var_table(self):
        return self.var_table

    # Function resets variable table and generates size for function
    # Function receives function id
    def delete_var_table(self, id):
        self.directory[id]['size'] = MemoryManager().get_module_counter()
        clean_vartable = self.clean_export()
        self.var_table = None
        self.params = {}
        return clean_vartable

    # Function used to store global variables on function
    # Function receives function id
    def store_global_vars(self, id):
        self.directory[id]['size'] = MemoryManager().get_global_counter()
        clean_vartable = self.clean_export()
        self.var_table = None
        self.params = {}
        return clean_vartable

    # Dev function used to neatly print directory
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
