from components.mem_manager import MemoryManager


class LocalMemory():
    def __init__(self, l_int, l_float, l_string, l_boolean, t_int, t_float, t_string, t_boolean):
        self.memory = MemoryManager().request_localmemory(l_int, l_float, l_string,
                                                          l_boolean, t_int, t_float, t_string, t_boolean)
