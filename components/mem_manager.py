class MemoryManagerMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class MemoryManager (metaclass=MemoryManagerMeta):

    def __init__(self):
        self.INT_GLOBAL_OFFSET = 1000
        self.FLOAT_GLOBAL_OFFSET = 1500
        self.DOUBLE_GLOBAL_OFFSET = 2500
        self.STR_GLOBAL_OFFSET = 3000
        self.BOOL_GLOBAL_OFFSET = 3500

        self.INT_TEMP_OFFSET = 4000
        self.FLOAT_TEMP_OFFSET = 4500
        self.DOUBLE_TEMP_OFFSET = 5000
        self.STR_TEMP_OFFSET = 5500
        self.BOOL_TEMP_OFFSET = 6000

        self.INT_CONST_OFFSET = 7000
        self.FLOAT_CONST_OFFSET = 7500
        self.DOUBLE_CONST_OFFSET = 8000
        self.STR_CONST_OFFSET = 8500
        self.BOOL_CONST_OFFSET = 9000

        self.global_int = 0
        self.global_float = 0
        self.global_double = 0
        self.global_str = 0
        self.global_bool = 0

        self.temp_int = 0
        self.temp_float = 0
        self.temp_double = 0
        self.temp_str = 0
        self.temp_bool = 0

        self.const_int = 0
        self.const_float = 0
        self.const_double = 0
        self.const_str = 0
        self.const_bool = 0

    def next_global_int(self):
        return self.global_int + self.INT_GLOBAL_OFFSET

    def request_global_int(self):
        self.global_int += 1
        return self.global_int + self.INT_GLOBAL_OFFSET

    def next_temp_int(self):
        return self.temp_int + self.INT_TEMP_OFFSET

    def request_temp_int(self):
        self.temp_int += 1
        return self.const_int + self.INT_TEMP_OFFSET

    def next_const_int(self):
        return self.const_int + self.INT_CONST_OFFSET

    def request_const_int(self):
        self.const_int += 1
        return self.const_int + self.INT_CONST_OFFSET

    def next_global_float(self):
        return self.global_float + self.FLOAT_GLOBAL_OFFSET

    def request_global_float(self):
        self.global_float += 1
        return self.global_float + self.FLOAT_GLOBAL_OFFSET

    def next_temp_float(self):
        return self.temp_float + self.FLOAT_TEMP_OFFSET

    def request_temp_float(self):
        self.temp_float += 1
        return self.const_float + self.FLOAT_TEMP_OFFSET

    def next_const_float(self):
        return self.const_float + self.FLOAT_CONST_OFFSET

    def request_const_float(self):
        self.const_float += 1
        return self.const_float + self.FLOAT_CONST_OFFSET

    def next_global_double(self):
        return self.global_double + self.DOUBLE_GLOBAL_OFFSET

    def request_global_double(self):
        self.global_double += 1
        return self.global_double + self.DOUBLE_GLOBAL_OFFSET

    def next_temp_double(self):
        return self.temp_double + self.DOUBLE_TEMP_OFFSET

    def request_temp_double(self):
        self.temp_double += 1
        return self.const_double + self.DOUBLE_TEMP_OFFSET

    def next_const_double(self):
        return self.const_double + self.DOUBLE_CONST_OFFSET

    def request_const_double(self):
        self.const_double += 1
        return self.const_double + self.DOUBLE_CONST_OFFSET

    def next_global_str(self):
        return self.global_str + self.STR_GLOBAL_OFFSET

    def request_global_str(self):
        self.global_str += 1
        return self.global_str + self.STR_GLOBAL_OFFSET

    def next_temp_str(self):
        return self.temp_str + self.STR_TEMP_OFFSET

    def request_temp_str(self):
        self.temp_str += 1
        return self.const_str + self.STR_TEMP_OFFSET

    def next_const_str(self):
        return self.const_str + self.STR_CONST_OFFSET

    def request_const_str(self):
        self.const_str += 1
        return self.const_str + self.STR_CONST_OFFSET

    def next_global_bool(self):
        return self.global_bool + self.BOOL_GLOBAL_OFFSET

    def request_global_bool(self):
        self.global_bool += 1
        return self.global_bool + self.BOOL_GLOBAL_OFFSET

    def next_temp_bool(self):
        return self.temp_bool + self.BOOL_TEMP_OFFSET

    def request_temp_bool(self):
        self.temp_bool += 1
        return self.const_bool + self.BOOL_TEMP_OFFSET

    def next_const_bool(self):
        return self.const_bool + self.BOOL_CONST_OFFSET

    def request_const_bool(self):
        self.const_bool += 1
        return self.const_bool + self.BOOL_CONST_OFFSET
