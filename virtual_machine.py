from typing import runtime_checkable
from components.mem_manager import MemoryManager
from components.stack import Stack
from vm.file_loader import FileLoader

quad_pointer = 0
const_table = None
global_memory = None
memory_stack = Stack()


def get_value(address):
    global const_table, global_memory, memory_stack
    current_memory = memory_stack.top()
    if address in global_memory:
        return global_memory[address]
    elif address in const_table:
        return const_table[address]
    elif address in current_memory:
        return current_memory[address]
    else:
        raise RuntimeError("Invalid Address: " + address)


def store_value(value, address):
    global const_table, global_memory, memory_stack
    current_memory = memory_stack.top()
    if address in global_memory:
        global_memory[address] = value
    elif address in current_memory:
        current_memory[address] = value
    else:
        raise RuntimeError("Invalid Address: " + address)


def process_quad(quad):
    if(quad[0] == "goto"):
        global quad_pointer
        quad_pointer = quad[3]-1
    elif(quad[0] == "+"):
        izq = get_value(quad[1])
        der = get_value(quad[2])
        if type(izq) == str:
            result = izq.strip('"') + str(der)
        elif type(der) == str:
            result = str(izq) + der.strip('"')
        else:
            result = izq + der
        store_value(result, quad[3])
        quad_pointer += 1
    elif(quad[0] == "-"):
        izq = get_value(quad[1])
        der = get_value(quad[2])
        result = izq - der
        store_value(result, quad[3])
        quad_pointer += 1
    elif (quad[0] == "*"):
        izq = get_value(quad[1])
        der = get_value(quad[2])
        result = izq * der
        store_value(result, quad[3])
        quad_pointer += 1
    elif (quad[0] == "/"):
        izq = get_value(quad[1])
        der = get_value(quad[2])
        result = izq / der
        store_value(result, quad[3])
        quad_pointer += 1
    elif (quad[0] == "="):
        value = get_value(quad[1])
        store_value(value, quad[3])
        quad_pointer += 1
    elif(quad[0] == "print"):
        text = get_value(quad[3])
        print(text)
        quad_pointer += 1
    else:
        raise RuntimeError("Unimplemented Action Code: " + quad[0])


def main():
    global const_table, global_memory, memory_stack

    file_loader = FileLoader("./output/out.obj")
    (quadruples, functions, memory, constants) = file_loader.get_data()

    const_table = constants
    global_memory = MemoryManager().request_globalmemory(memory['program'])
    main_memory = MemoryManager().request_localmemory(memory['main'])
    memory_stack.push(main_memory)

    while True:
        if quadruples[quad_pointer][0] == "END":
            print("Process terminated")
            break
        process_quad(quadruples[quad_pointer])


if __name__ == "__main__":
    main()
