# ------------------------------------------------------------
# mem_manager.py
# A01364749 Gustavo Hernandez Sanchez
# A01364701 Luis Miguel Maawad Hinojosa
# ------------------------------------------------------------

# Class used for implementing the Singleton Design Pattern.
class MemoryManagerMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

# Memory Manager Class Definition.


class MemoryManager(metaclass=MemoryManagerMeta):
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
            'class': {
                'int': [4000, 4499],
                'float': [4500, 4999],
                'string': [5500, 5999],
                'bool': [6000, 6999]
            },
            'local': {
                'int': [7000, 7499],
                'float': [7500, 7999],
                'string': [8500, 8999],
                'bool': [9000, 9499]
            },
            'temp': {
                'int': [9500, 9699],
                'float': [9750, 9999],
                'string': [10000, 10249],
                'bool': [10250, 10499]
            },
            'const': {
                'int': [10500, 10999],
                'float': [11000, 11499],
                'string': [11500, 11999],
                'bool': [12000, 12499]
            },
            'pointers': {
                'int': [20000, 21999]
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
            'class': {
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

        # Dictionary to keep track of the registered classes
        # and their base addresses.
        self.class_bases = {}

        # Keeps track of the declared objects and their
        # virtual addresses.
        self.object_counter = {}

        # Class map definition
        self.class_map = {
            'blocked': 30000,
            'public': 40000,
        }

        # Dictionary that keeps track of the registered classes
        # depending on their visibility.
        self.class_counter = {
            'blocked': 0,
            'public': 0,
        }
        self.class_offset = 100

    # Resets the context for each module declaration.
    # Allows the reuse of virtual addresses.
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
        self.counter['pointers'] = {
            'int': 0
        }

    # Resets the context for each class declaration.
    # Allows the reuse of virtual addresses
    def reset_class_context(self):
        self.counter['class'] = {
            'int': 0,
            'float': 0,
            'string': 0,
            'bool': 0
        }
        self.counter['temp'] = {
            'int': 0,
            'float': 0,
            'string': 0,
            'bool': 0
        }
        self.counter['pointers'] = {
            'int': 0
        }

    # Calculates the offset for each class declaration.
    # Used for preventing the overwriting of addresses
    # while extending a class.
    def class_counter_offset(self, i, f, s, b):
        self.counter['class']['int'] += i
        self.counter['class']['float'] += f
        self.counter['class']['string'] += s
        self.counter['class']['bool'] += b

    # Handles the request of a class address
    # Calculates the new address based on the current
    # number of declared classes and the visibility of
    # the new class.
    # Stores the class and its address as a base to assign
    # an address to an object.
    def request_class_address(self, id, visibility):
        new_address = self.class_map[visibility] + \
            self.class_counter[visibility]
        self.class_map[visibility] += self.class_offset
        self.object_counter[id] = new_address
        self.class_bases[id] = new_address
        return new_address

    # Handles the request of a virtual address
    # to an object.
    def request_object_address(self, classname):
        new_address = self.object_counter[classname]
        self.object_counter[classname] += 1
        return new_address

    # Returns the total number of assigned addresses
    # of each variable type that are part of the class
    # scope.
    def get_class_vars(self):
        mem_space = {
            'c_int': self.counter['class']['int'],
            'c_float': self.counter['class']['float'],
            'c_string': self.counter['class']['string'],
            'c_bool': self.counter['class']['bool'],
        }
        return mem_space

    # Returns the total number of assigned addresses
    # of each variable type that are part of the temporals
    # scope.
    def get_class_temps(self):
        mem_space = {
            't_int': self.counter['temp']['int'],
            't_float': self.counter['temp']['float'],
            't_string': self.counter['temp']['string'],
            't_bool': self.counter['temp']['bool'],
            'pointers': self.counter['pointers']['int']
        }
        return mem_space

    # Returns the total number of assigned addresses
    # of each variable type that are part of the module
    # scope.
    def get_module_counter(self):
        mem_space = {
            'l_int': self.counter['local']['int'],
            'l_float': self.counter['local']['float'],
            'l_string': self.counter['local']['string'],
            'l_bool': self.counter['local']['bool'],
            't_int': self.counter['temp']['int'],
            't_float': self.counter['temp']['float'],
            't_string': self.counter['temp']['string'],
            't_bool': self.counter['temp']['bool'],
            'pointers': self.counter['pointers']['int']
        }
        return mem_space

    # Returns the total number of assigned addresses
    # of each variable type that are part of the global
    # scope.
    def get_global_counter(self):
        mem_space = {
            'g_int': self.counter['global']['int'],
            'g_float': self.counter['global']['float'],
            'g_string': self.counter['global']['string'],
            'g_bool': self.counter['global']['bool'],
            't_int': self.counter['temp']['int'],
            't_float': self.counter['temp']['float'],
            't_string': self.counter['temp']['string'],
            't_bool': self.counter['temp']['bool'],
            'pointers': self.counter['pointers']['int']
        }
        return mem_space

    # Request and Address given a scope and type
    # The return value is an available address as an integer.
    def request_address(self, scope, tp):
        if tp in ['int', 'bool', 'float', 'string']:
            nextAddress = self.map[scope][tp][0] + self.counter[scope][tp]
            if (nextAddress <= self.map[scope][tp][1]):
                self.counter[scope][tp] += 1
                return nextAddress
            raise MemoryError("Insuficient memory to assign a new address")
        if self.object_counter[tp] + 1 < self.class_bases[tp] + 100:
            return self.request_object_address(tp)
        raise MemoryError("Insuficient memory to assign a new address")

    # Request and Address block given a scope, type and size
    # The return value is an available address as an integer.
    def request_address_block(self, scope, tp, size):
        if size < 1:
            raise ValueError("Address block must be greater than 1.")
        nextAddress = self.map[scope][tp][0] + self.counter[scope][tp]
        if (nextAddress <= self.map[scope][tp][1]):
            self.counter[scope][tp] += size
            return nextAddress
        raise MemoryError("Insuficient memory to assign a new address")

    # Given an array of numbers, an uninitialized memory space is generated.
    # The memory space is represented as a dictionary where each address is
    # a key and all the values are equal to None.
    # The scope for this memory space contains locals, temporals and pointers.
    def request_localmemory(self, memspace):
        # Generate the virtual addresses for each scope and variable type
        l_int_space = list(
            range(self.map['local']['int'][0], self.map['local']['int'][0] + memspace[0]))
        l_float_space = list(
            range(self.map['local']['float'][0], self.map['local']['float'][0] + memspace[1]))
        l_string_space = list(
            range(self.map['local']['string'][0], self.map['local']['string'][0] + memspace[2]))
        l_bool_space = list(
            range(self.map['local']['bool'][0], self.map['local']['bool'][0] + memspace[3]))
        t_int_space = list(
            range(self.map['temp']['int'][0], self.map['temp']['int'][0] + memspace[4]))
        t_float_space = list(
            range(self.map['temp']['float'][0], self.map['temp']['float'][0] + memspace[5]))
        t_string_space = list(
            range(self.map['temp']['string'][0], self.map['temp']['string'][0] + memspace[6]))
        t_bool_space = list(
            range(self.map['temp']['bool'][0], self.map['temp']['bool'][0] + memspace[7]))
        pointer_space = list(
            range(self.map['pointers']['int'][0], self.map['pointers']['int'][0] + memspace[8]))

        # List of virtual addresses
        spaces = l_int_space + l_float_space + l_string_space + l_bool_space + \
            t_int_space + t_float_space + t_string_space + t_bool_space + pointer_space

        # List of tuples following the structure: (virtual_address, None)
        addresses = list(map(lambda x: (x, None), spaces))
        return dict(addresses)

    # Given an array of numbers, an uninitialized memory space is generated.
    # The memory space is represented as a dictionary where each address is
    # a key and all the values are equal to None.
    # The scope for this memory space contains globals, temporals and pointers.
    def request_globalmemory(self, memspace):
        # Generate the virtual addresses for each scope and variable type
        g_int_space = list(
            range(self.map['global']['int'][0], self.map['global']['int'][0] + memspace[0]))
        g_float_space = list(
            range(self.map['global']['float'][0], self.map['global']['float'][0] + memspace[1]))
        g_string_space = list(
            range(self.map['global']['string'][0], self.map['global']['string'][0] + memspace[2]))
        g_bool_space = list(
            range(self.map['global']['bool'][0], self.map['global']['bool'][0] + memspace[3]))
        t_int_space = list(
            range(self.map['temp']['int'][0], self.map['temp']['int'][0] + memspace[4]))
        t_float_space = list(
            range(self.map['temp']['float'][0], self.map['temp']['float'][0] + memspace[5]))
        t_string_space = list(
            range(self.map['temp']['string'][0], self.map['temp']['string'][0] + memspace[6]))
        t_bool_space = list(
            range(self.map['temp']['bool'][0], self.map['temp']['bool'][0] + memspace[7]))
        pointer_space = list(
            range(self.map['pointers']['int'][0], self.map['pointers']['int'][0] + memspace[8]))

        # List of virtual addresses
        spaces = g_int_space + g_float_space + g_string_space + g_bool_space + \
            t_int_space + t_float_space + t_string_space + t_bool_space + pointer_space

        # List of tuples following the structure: (virtual_address, None)
        addresses = list(map(lambda x: (x, None), spaces))
        return dict(addresses)

    # Given an array of numbers, an uninitialized memory space is generated.
    # The memory space is represented as a dictionary where each address is
    # a key and all the values are equal to None.
    # The scope for this memory space contains class variables, temporals
    # and pointers.
    def request_classmemory(self, memspace):
        # Generate the virtual addresses for each scope and variable type
        c_int_space = list(
            range(self.map['class']['int'][0], self.map['class']['int'][0] + memspace[0]))
        c_float_space = list(
            range(self.map['class']['float'][0], self.map['class']['float'][0] + memspace[1]))
        c_string_space = list(
            range(self.map['class']['string'][0], self.map['class']['string'][0] + memspace[2]))
        c_bool_space = list(
            range(self.map['class']['bool'][0], self.map['class']['bool'][0] + memspace[3]))
        t_int_space = list(
            range(self.map['temp']['int'][0], self.map['temp']['int'][0] + memspace[4]))
        t_float_space = list(
            range(self.map['temp']['float'][0], self.map['temp']['float'][0] + memspace[5]))
        t_string_space = list(
            range(self.map['temp']['string'][0], self.map['temp']['string'][0] + memspace[6]))
        t_bool_space = list(
            range(self.map['temp']['bool'][0], self.map['temp']['bool'][0] + memspace[7]))
        pointer_space = list(
            range(self.map['pointers']['int'][0], self.map['pointers']['int'][0] + memspace[8]))

        # List of virtual addresses
        spaces = c_int_space + c_float_space + c_string_space + c_bool_space + \
            t_int_space + t_float_space + t_string_space + t_bool_space + pointer_space

        # List of tuples following the structure: (virtual_address, None)
        addresses = list(map(lambda x: (x, None), spaces))
        return dict(addresses)
