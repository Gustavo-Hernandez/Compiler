class VariableTable:
    def __init__(self):
        self.table = {}
        self.queue = []
        self.value = None
        self.type_var = None

    def register(self):
        for v in self.queue:
            if v in self.table:
                raise NameError("Selected name " + v + " is already in use")
            else:
                self.table[v] = {'type': self.type_var, 'value': self.value}
        self.queue = []
        self.value = None
        self.type_var = None

    def update(self, id, value):
        if id in self.table:
            self.table[id]['value'] = value
        else:
            print("[Error] Null Pointer Exception: " + id)

    def store_id(self, id):
        self.queue.append(id)

    def set_value(self, value):
        self.value = value

    def set_type(self, type_var):
        self.type_var = type_var

    def get_type(self, id):
        if id in self.table:
            return self.table[id]['type']
        else:
            raise KeyError("Cannot get type for nonexitent id")

    def print(self):
        print(self.table)
