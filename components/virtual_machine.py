

from components.mem_manager import MemoryManager


class VirtualMachine:
    def __init__(self, quadruples, func_dir, vartables):
        self.quadruples = quadruples
        self.func_dir = func_dir
        self.vartables = vartables
        self.instruction_pointer = 0
        self.global_mem = None

    def start(self):
        print("--------------------- Starting Execution ---------------------")
        # Request main memory
        memspace = self.func_dir['main']['size']
        main_memory = MemoryManager().request_localmemory(
            memspace['l_int'], memspace['l_float'], memspace['l_string'], memspace['l_bool'], memspace['t_int'], memspace['t_float'], memspace['t_string'], memspace['t_bool'], memspace['pointers'])

        print(main_memory)
        while True:
            if not self.process_instruction():
                break

    def goto(self, instruction_number):
        self.instruction_pointer = instruction_number - 1

    def process_instruction(self):
        pass
        #instruction = self.quadruples[self.instruction_pointer]
        #action_code = instruction[0]
        #left_operand = instruction[1]
        #right_operand = instruction[2]
        #destination = instruction[3]
        # if(action_code == 'goto'):
        #    self.goto(destination)
        #    return True
        # elif(action_code == "END"):
        #    return False
        # else:
        #    raise RuntimeError("Unimplemented action codes")
