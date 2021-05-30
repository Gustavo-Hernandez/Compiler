import math
from components.mem_manager import MemoryManager


class VariableTable:
    def __init__(self):
        self.table = {}
        self.queue = []
        self.value = None
        self.type_var = None
        self.is_array = []
        self.dims = []

    def register(self, scope, cte_table):
        for v in self.queue:
            if v in self.table:
                raise NameError("Selected name " + v + " is already in use")
            else:
                is_array = self.is_array.pop(0)
                if is_array:
                    d = self.dims.pop(0)
                    size = math.prod(d)
                    m = size
                    dims = []
                    for dim in d:
                        m = m//dim
                        m_dir = cte_table.insert_cte(m, 'int')
                        dim_dir = cte_table.insert_cte(dim-1, 'int')
                        dims.append([dim_dir, m_dir])

                    virtualAddress = self.requestArrayAddress(
                        scope, self.type_var, size)
                else:
                    dims = None
                    virtualAddress = self.requestAddress(scope, self.type_var)

                self.table[v] = {
                    'type': self.type_var,
                    'virtual_address': virtualAddress,
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

    def requestArrayAddress(self, scope, type_var, size):
        virtual_address = MemoryManager().request_address_block(scope, type_var, size)
        return virtual_address

    def requestAddress(self, scope, type_var):
        virtual_address = MemoryManager().request_address(scope, type_var)
        return virtual_address

    def insert_cte(self, val, tp):
        if val in self.table:
            return self.table[val]['virtual_address']
        else:
            mem = MemoryManager().request_address('const', tp)
            self.table[val] = {'virtual_address': mem}
            return mem
