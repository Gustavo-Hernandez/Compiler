from components.mem_manager import MemoryManager


class VariableTable:
    def __init__(self):
        self.table = {}
        self.queue = []
        self.value = None
        self.type_var = None
        self.is_array = []
        self.dims = []

    def register(self, scope):
        for v in self.queue:
            if v in self.table:
                raise NameError("Selected name " + v + " is already in use")
            else:
                is_array = self.is_array.pop(0)
                if is_array:
                    dims = self.dims.pop(0)
                else:
                    dims = None

                if(scope == 'global'):
                    self.table[v] = {
                        'type': self.type_var,
                        'virtual_address': MemoryManager().request_address(scope, self.type_var),
                        'is_array': is_array,
                        'dims': dims
                    }
                else:
                    self.table[v] = {
                        'type': self.type_var,
                        'virtual_address': MemoryManager().request_address('local', self.type_var),
                        'is_array': is_array,
                        'dims': dims
                    }
        self.queue = []
        self.type_var = None
        self.is_array = []
        self.dims = []

    def store_id(self, id):
        self.queue.append(id)

    def set_type(self, type_var):
        self.type_var = type_var

    def get_type(self, id):
        if id in self.table:
            return self.table[id]['type']
        else:
            raise KeyError("Cannot get type for nonexitent id")

    def print(self):
        print(self.table)

    def set_array(self, state):
        self.is_array.append(state)

    def set_dims(self, dims):
        self.dims.append(dims)

    def get_is_array(self, val):
        if val in self.table:
            return self.table[val]['is_array']
        else:
            raise KeyError("Variable " + val + " is not defined")
