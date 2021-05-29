import sys
from typing import runtime_checkable
from components.mem_manager import MemoryManager
from components.stack import Stack
from vm.file_loader import FileLoader

quad_pointer = 0
const_table = None
global_memory = None
funcs = None
memories = None
call_stack = Stack()
modules_addresses = None
idle_memory = None
memory_stack = Stack()
quad_pointer_stack = Stack()


def get_value(address):
    global const_table, global_memory, memory_stack
    current_memory = memory_stack.top()
    if address in global_memory:
        value = global_memory[address]
    elif address in const_table:
        value = const_table[address]
    elif address in current_memory:
        value = current_memory[address]
    else:
        raise RuntimeError("Invalid Address: " + str(address))
    if value == None:
        print("[ERROR] Uninitialized value at " + str(address) + " at quad ", quad_pointer)
        sys.exit()
    return value


def store_value(value, address):
    global const_table, global_memory, memory_stack
    current_memory = memory_stack.top()
    if address in global_memory:
        global_memory[address] = value
    elif address in current_memory:
        current_memory[address] = value
    else:
        raise RuntimeError("Invalid Address: " + str(address) + " at quad ", quad_pointer)


def store_param(value, address):
    global idle_memory
    if address in idle_memory:
        idle_memory[address] = value
    else:
        raise RuntimeError("Invalid Address: " + str(address) + " at quad ", quad_pointer)


def process_quad(param_quad):
    global quad_pointer, modules_addresses, call_stack, idle_memory
    quad = param_quad.copy()

    for i in range(1, 4):
        if type(quad[i]) == str and "(" in quad[i]:
            quad[i] = get_value(int(quad[i].replace("(", "").replace(")", "")))

    if quad[0] == "goto":
        quad_pointer = quad[3] - 1
    elif quad[0] == "+":
        izq = get_value(quad[1])
        der = get_value(quad[2])
        if type(der) == str and type(izq) == str:
            result = izq.strip('"') + der.strip('"')
        elif type(izq) == str:
            result = izq.strip('"') + str(der)
        elif type(der) == str:
            result = str(izq) + der.strip('"')
        else:
            result = izq + der
        store_value(result, quad[3])
        quad_pointer += 1
    elif quad[0] == "-":
        izq = get_value(quad[1])
        der = get_value(quad[2])
        result = izq - der
        store_value(result, quad[3])
        quad_pointer += 1
    elif quad[0] == "*":
        izq = get_value(quad[1])
        der = get_value(quad[2])
        result = izq * der
        store_value(result, quad[3])
        quad_pointer += 1
    elif quad[0] == "/":
        izq = get_value(quad[1])
        der = get_value(quad[2])
        result = izq / der
        store_value(result, quad[3])
        quad_pointer += 1
    elif quad[0] == "=":
        value = get_value(quad[1])
        store_value(value, quad[3])
        quad_pointer += 1
    elif quad[0] == "print":
        text = get_value(quad[3])
        print(text)
        quad_pointer += 1
    elif quad[0] == ">":
        izq = get_value(quad[1])
        der = get_value(quad[2])
        store_value(izq > der, quad[3])
        quad_pointer += 1
    elif quad[0] == "<":
        izq = get_value(quad[1])
        der = get_value(quad[2])
        store_value(izq < der, quad[3])
        quad_pointer += 1
    elif quad[0] == "==":
        izq = get_value(quad[1])
        der = get_value(quad[2])
        store_value(izq == der, quad[3])
        quad_pointer += 1
    elif quad[0] == "!=":
        izq = get_value(quad[1])
        der = get_value(quad[2])
        store_value(izq != der, quad[3])
        quad_pointer += 1
    elif quad[0] == "and":
        izq = get_value(quad[1])
        der = get_value(quad[2])
        store_value(izq and der, quad[3])
        quad_pointer += 1
    elif quad[0] == "or":
        izq = get_value(quad[1])
        der = get_value(quad[2])
        store_value(izq or der, quad[3])
        quad_pointer += 1
    elif quad[0] == "gotoF":
        var = get_value(quad[1])
        if var:
            quad_pointer += 1
        else:
            quad_pointer = quad[3] - 1
    elif quad[0] == "ERA":
        idle_memory = MemoryManager().request_localmemory(memories[quad[1]])
        call_stack.push(quad[1])
        quad_pointer += 1
    elif quad[0] == "PARAM":
        value = get_value(quad[1])
        store_param(value, quad[3])
        quad_pointer += 1
    elif quad[0] == "GOSUB":
        memory_stack.push(idle_memory)
        idle_memory = None
        quad_pointer_stack.push(quad_pointer)
        quad_pointer = funcs[quad[3]]['position'] - 1
    elif quad[0] == "ENDFUNC":
        quad_pointer = quad_pointer_stack.pop()
        quad_pointer += 1
    elif quad[0] == "VER":
        index = get_value(quad[1])
        lim_inf = get_value(quad[2])
        lim_sup = get_value(quad[3])
        if index < lim_inf or index > lim_sup:
            print("[ERROR] Index out of range ", index, lim_inf, lim_sup)
            sys.exit()
        quad_pointer += 1
    elif quad[0] == "RETURN":
        value = get_value(quad[3])
        fn_id = call_stack.pop()
        address = modules_addresses[fn_id]
        store_value(value, address)
        memory_stack.pop()
        quad_pointer += 1
    elif quad[0] == "READ":
        address = quad[3]
        value = input()

        try:
            if quad[1] == 'string':
                value = str(value)
            elif quad[1] == 'int':
                value = int(value)
            elif quad[1] == 'float':
                value = float(value)
            elif quad[1] == 'bool':
                value = bool(value)
            else:
                print("[ERROR] Variable type not recognized on READ")
                sys.exit()
        except ValueError:
            print("[ERROR] Read input type does not match var type " + quad[1])
            sys.exit()

        store_value(value, address)
        quad_pointer += 1
    else:
        raise RuntimeError("Unimplemented Action Code: " + quad[0])


def main():
    global const_table, global_memory, memory_stack, funcs, memories, modules_addresses

    file_loader = FileLoader("./output/out.obj")
    (quadruples, functions, ret_modules_address,
     memory, constants) = file_loader.get_data()

    funcs = functions
    memories = memory
    modules_addresses = ret_modules_address

    const_table = constants
    global_memory = MemoryManager().request_globalmemory(memory['program'])
    if 'main' in memory:
        main_memory = MemoryManager().request_localmemory(memory['main'])
        memory_stack.push(main_memory)

    while True:
        if quadruples[quad_pointer][0] == "END":
            print("Process terminated")
            break
        process_quad(quadruples[quad_pointer])


if __name__ == "__main__":
    main()