from components.mem_manager import MemoryManager


class VariableTable:
    def __init__(self):
        self.table = {}
        self.queue = []
        self.value = None
        self.type_var = None

    def register(self, scope):
        for v in self.queue:
            if v in self.table:
                print("[Error] Duplicate Variable: " + v)
            else:
                self.table[v] = {
                    'scope': scope, 'type': self.type_var}
        self.queue = []
        self.type_var = None

    def store_id(self, id):
        self.queue.append(id)

    def set_type(self, type_var):
        self.type_var = type_var

    def get_type(self, id):
        if id in self.table:
            return self.table[id]['type']
        else:
            raise KeyError("Cannot get type for nonexitent id")

    def requestAddress(self):
        if(self.type_var == 'int'):
            return self.mem_manager.request_global_int()
        return 'Invalid'

    def print(self):
        print(self.table)
