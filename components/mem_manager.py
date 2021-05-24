class MemoryManagerMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class MemoryManager (metaclass=MemoryManagerMeta):
    def __init__(self):
        # This structure allows to set the upper and
        # lower limits of an address space.
        # Limits are stablished as the following:
        # scope:{datatype:[min,max]}
        self.map = {
            'global': {
                'int': [1000, 1499],
                'float': [1500, 1999],
                'string': [2500, 3499],
                'bool': [3500, 3999]
            },
            'local': {
                'int': [4000, 4499],
                'float': [4500, 4999],
                'string': [5500, 5999],
                'bool': [6000, 6999]
            },
            'temp': {
                'int': [7000, 7499],
                'float': [7500, 7999],
                'string': [8500, 8999],
                'bool': [9000, 9499]
            },
            'const': {
                'int': [9500, 9699],
                'float': [9750, 9999],
                'string': [10000, 10249],
                'bool': [10250, 10499]
            },
            'pointers': {
                'int': [12000, 13000]
            }
        }
        # This structure allows to keep track of the current
        # requested addresses
        self.counter = {
            'global': {
                'int': 0,
                'float': 0,
                'string': 0,
                'bool': 0
            },
            'local': {
                'int': 0,
                'float': 0,
                'string': 0,
                'bool': 0
            },
            'temp': {
                'int': 0,
                'float': 0,
                'string': 0,
                'bool': 0
            },
            'const': {
                'int': 0,
                'float': 0,
                'string': 0,
                'bool': 0
            },
            'pointers': {
                'int': 0
            }
        }

    def reset_module_context(self):
        self.counter['temp'] = {
            'int': 0,
            'float': 0,
            'string': 0,
            'bool': 0
        }
        self.counter['local'] = {
            'int': 0,
            'float': 0,
            'string': 0,
            'bool': 0
        }

    def get_module_counter(self):
        mem_space = {
            'l_int': self.counter['local']['int'],
            'l_float': self.counter['local']['float'],
            'l_string': self.counter['local']['string'],
            'l_bool': self.counter['local']['bool'],
            't_int': self.counter['temp']['int'],
            't_float': self.counter['temp']['float'],
            't_string': self.counter['temp']['string'],
            't_bool': self.counter['temp']['bool']
        }
        return mem_space

    # Request and Address given a scope and type
    # The return value is an available address as an integer.
    def request_address(self, scope, tp):
        nextAddress = self.map[scope][tp][0] + self.counter[scope][tp]
        if(nextAddress <= self.map[scope][tp][1]):
            self.counter[scope][tp] += 1
            return nextAddress
        raise MemoryError("Insuficient memory to assign a new address")

    def get_address_type(self, memAddress):
        if memAddress >= self.map['global']['int'][0] and memAddress <= self.map['pointers']['int'][1]:
            # Get Scope of INT Address
            if memAddress in range(self.map['global']['int'][0], self.self.map['global']['int'][1]):
                return ['global', 'int']
            elif memAddress in range(self.map['local']['int'][0], self.self.map['local']['int'][1]):
                return ['local', 'int']
            elif memAddress in range(self.map['temp']['int'][0], self.self.map['temp']['int'][1]):
                return ['temp', 'int']
            elif memAddress in range(self.map['const']['int'][0], self.self.map['const']['int'][1]):
                return ['const', 'int']
            elif memAddress in range(self.map['pointer']['int'][0], self.self.map['pointer']['int'][1]):
                return ['pointer', 'int']
            # Get Scope of FLOAT Address
            elif memAddress in range(self.map['global']['float'][0], self.self.map['global']['float'][1]):
                return ['global', 'float']
            elif memAddress in range(self.map['local']['float'][0], self.self.map['local']['float'][1]):
                return ['local', 'float']
            elif memAddress in range(self.map['temp']['float'][0], self.self.map['temp']['float'][1]):
                return ['temp', 'float']
            elif memAddress in range(self.map['const']['float'][0], self.self.map['const']['float'][1]):
                return ['const', 'float']
            # Get Scope of STRING Address
            elif memAddress in range(self.map['global']['string'][0], self.self.map['global']['string'][1]):
                return ['global', 'string']
            elif memAddress in range(self.map['local']['string'][0], self.self.map['local']['string'][1]):
                return ['local', 'string']
            elif memAddress in range(self.map['temp']['string'][0], self.self.map['temp']['string'][1]):
                return ['temp', 'string']
            elif memAddress in range(self.map['const']['string'][0], self.self.map['const']['string'][1]):
                return ['const', 'string']
            # Get Scope of BOOL Address
            elif memAddress in range(self.map['global']['bool'][0], self.self.map['global']['bool'][1]):
                return ['global', 'bool']
            elif memAddress in range(self.map['local']['bool'][0], self.self.map['local']['bool'][1]):
                return ['local', 'bool']
            elif memAddress in range(self.map['temp']['bool'][0], self.self.map['temp']['bool'][1]):
                return ['temp', 'bool']
            elif memAddress in range(self.map['const']['bool'][0], self.self.map['const']['bool'][1]):
                return ['const', 'bool']
        # If memory address not in range return error.
        raise MemoryError("Invalid Memory Address")

    def request_localmemory(self, l_int, l_float, l_string, l_bool, t_int, t_float, t_string, t_bool):
        # TODO: Validate mem in range values.
        l_int_space = list(
            range(self.map['local']['int'][0], self.map['local']['int'][0] + l_int))
        l_float_space = list(
            range(self.map['local']['float'][0], self.map['local']['float'][0] + l_float))
        l_string_space = list(
            range(self.map['local']['string'][0], self.map['local']['string'][0] + l_string))
        l_bool_space = list(
            range(self.map['local']['bool'][0], self.map['local']['bool'][0] + l_bool))
        t_int_space = list(
            range(self.map['temp']['int'][0], self.map['temp']['int'][0] + t_int))
        t_float_space = list(
            range(self.map['temp']['float'][0], self.map['temp']['float'][0] + t_float))
        t_string_space = list(
            range(self.map['temp']['string'][0], self.map['temp']['string'][0] + t_string))
        t_bool_space = list(
            range(self.map['temp']['bool'][0], self.map['temp']['bool'][0] + t_bool))

        spaces = l_int_space + l_float_space + l_string_space + l_bool_space + \
            t_int_space + t_float_space + t_string_space + t_bool_space

        addresses = list(map(lambda x: (x, None), spaces))
        return dict(addresses)

    def request_globalmemory(self, g_int, g_float, g_string, g_bool, t_int, t_float, t_string, t_bool):
        # TODO: Validate mem in range values.
        g_int_space = list(
            range(self.map['global']['int'][0], self.map['global']['int'][0] + g_int))
        g_float_space = list(
            range(self.map['global']['float'][0], self.map['global']['float'][0] + g_float))
        g_string_space = list(
            range(self.map['global']['string'][0], self.map['global']['string'][0] + g_string))
        g_bool_space = list(
            range(self.map['global']['bool'][0], self.map['global']['bool'][0] + g_bool))
        t_int_space = list(
            range(self.map['global']['int'][0], self.map['global']['int'][0] + t_int))
        t_float_space = list(
            range(self.map['global']['float'][0], self.map['global']['float'][0] + t_float))
        t_string_space = list(
            range(self.map['global']['string'][0], self.map['global']['string'][0] + t_string))
        t_bool_space = list(
            range(self.map['global']['bool'][0], self.map['global']['bool'][0] + t_bool))

        spaces = g_int_space + g_float_space + g_string_space + g_bool_space + \
            t_int_space + t_float_space + t_string_space + t_bool_space

        addresses = list(map(lambda x: (x, None), spaces))
        return dict(addresses)
