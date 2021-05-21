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
                raise NameError("Selected name " + v + " is already in use")
            else:
                if(scope == 'global'):
                    self.table[v] = {
                        'type': self.type_var, 'virtual_address': MemoryManager().request_address(scope, self.type_var)}
                else:
                    self.table[v] = {
                        'type': self.type_var, 'virtual_address': MemoryManager().request_address('local', self.type_var)}
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

    def print(self):
        print(self.table)
