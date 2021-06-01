# ------------------------------------------------------------
# variable_table.py
# A01364749 Gustavo Hernandez Sanchez
# A01364701 Luis Miguel Maawad Hinojosa
# ------------------------------------------------------------
import math
from components.mem_manager import MemoryManager


# Definition of variable tables
class VariableTable:
    # Class must manage its table, variable id queue, variable type, array state and dimension queue
    def __init__(self):
        self.table = {}
        self.queue = []
        self.type_var = None
        self.is_array = []
        self.dims = []

    # Function register takes in the scope of variables to register and the current cte_table
    # Then proceeds to deque every variable that has been sent in for registry and checks if they
    # Already exist in the table, afterwards it assigns their memory value and in the case of arrays
    # It dequeues its dimensions from the dims queue and assignees them to the variable upon registry
    # And adds their values to the cte_table. Finally it resets all registry variables.
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
                        m = m // dim
                        m_dir = cte_table.insert_cte(m, 'int')
                        dim_dir = cte_table.insert_cte(dim - 1, 'int')
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

    # Function receives variable id and stores it on the queue
    def store_id(self, id):
        self.queue.append(id)

    # Function receives type and sets the value on the table accordingly
    def set_type(self, type_var):
        self.type_var = type_var

    # Function revives a variable id and returns its registered id
    def get_type(self, id):
        if id in self.table:
            return self.table[id]['type']
        else:
            raise KeyError("Cannot get type for nonexistent id")

    # Dev function to print all of the variable table
    def print(self):
        print(self.table)

    # Function receives array state (boolean) and appends it to the queue
    def set_array(self, state):
        self.is_array.append(state)

    # Function receives array dimensions and appends them to the queue
    def set_dims(self, dims):
        self.dims.append(dims)

    # Function returns boolean state for any variable id
    def get_is_array(self, val):
        if val in self.table:
            return self.table[val]['is_array']
        else:
            raise KeyError("Variable " + val + " is not defined")

    # Function requests memory space for a defined array, using its scope, variable type and size
    def requestArrayAddress(self, scope, type_var, size):
        virtual_address = MemoryManager().request_address_block(scope, type_var, size)
        return virtual_address

    # Function requests memory to Memory Manager using its scope and type
    def requestAddress(self, scope, type_var):
        virtual_address = MemoryManager().request_address(scope, type_var)
        return virtual_address

    # Function used only for the registry of constants in a separate table. If received constant has been registered
    # The function will return its memory space, if not it will allocate memory to it and return said address
    def insert_cte(self, val, tp):
        if val in self.table:
            return self.table[val]['virtual_address']
        else:
            mem = MemoryManager().request_address('const', tp)
            self.table[val] = {'virtual_address': mem}
            return mem
