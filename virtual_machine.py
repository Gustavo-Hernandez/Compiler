import sys
from typing import runtime_checkable
from components.mem_manager import MemoryManager
from components.stack import Stack
from vm.file_loader import FileLoader

# Declaration for global manipulation variables
quad_pointer = 0
const_table = None
global_memory = None
funcs = None
class_signatures = None
function_memories = None
class_memories = None
call_stack = Stack()
modules_addresses = None
idle_memory = None
idle_object = None
class_type = Stack()
class_address = Stack()
class_vars = {}
class_vars_stack = Stack()
object_subroutines = []
memory_stack = Stack()
quad_pointer_stack = Stack()


# Function get values makes use of an address to search for its value on all available memories
def get_value(address):
    global const_table, global_memory, memory_stack, class_vars
    current_memory = memory_stack.top()
    if address in current_memory:
        value = current_memory[address]
    elif address in const_table:
        value = const_table[address]
    elif address in class_vars:
        value = class_vars[address]
    elif address in global_memory:
        value = global_memory[address]
    else:
        raise RuntimeError("Invalid Address: " + str(address)+ " at quad ", quad_pointer)
    if value == None:
        print("[ERROR] Uninitialized value at " + str(address) + " at quad ", quad_pointer)
        sys.exit()
    return value


# Function get compound uses the address of an object and a variable to obtain the value of a specific variable in
# an existing object
def get_compound(obj, address):
    global const_table, global_memory, memory_stack, class_vars
    current_memory = memory_stack.top()
    if obj in current_memory:
        value = current_memory[obj][address]
    elif obj in class_vars:
        value = class_vars[obj][address]
    else:
        raise RuntimeError("Invalid Address: " + str(address))
    if value is None:
        print("[ERROR] Uninitialized value at " + str(address) + " at quad ", quad_pointer)
        sys.exit()
    return value


# Function store value takes an address and a value and overwrites the value in said address with the new input value
def store_value(value, address):
    global const_table, global_memory, memory_stack, class_vars
    current_memory = memory_stack.top()
    if address in current_memory:
        current_memory[address] = value
    elif address in class_vars:
        class_vars[address] = value
    elif address in global_memory:
        global_memory[address] = value
    else:
        raise RuntimeError("Invalid Address: " + str(address) + " at quad ", quad_pointer)


# Function appends object memory to current memory
def generate_object(memory, address):
    current_memory = memory_stack.top()
    current_memory[address] = memory


# Function store param is used to store values on a function variable
def store_param(value, address):
    global idle_memory
    if address in idle_memory:
        idle_memory[address] = value
    else:
        raise RuntimeError("Invalid Address: " + str(address) + " at quad ", quad_pointer)


# Function takes a compound address like '40000.2020' and separates it to send to get_compound
# however if the address is not compound the value is sent to get_value instead
def process_object_attribute(address):
    if type(address) == str:
        parts = address.split('.')
        return get_compound(int(parts[0]), int(parts[1]))
    else:
        return get_value(address)


# Function contains a large series of elif's in order to process all the possible instructions for a quadruple
def process_quad(param_quad):
    global quad_pointer, modules_addresses, call_stack, idle_memory, object_subroutines, \
        class_type, class_address, class_vars, idle_object, class_vars_stack
    quad = param_quad.copy()

    for i in range(1, 4):
        if type(quad[i]) == str and "(" in quad[i]:
            quad[i] = process_object_attribute(int(quad[i].replace("(", "").replace(")", "")))

    if quad[0] == "goto":
        quad_pointer = quad[3] - 1
    elif quad[0] == "+":
        izq = process_object_attribute(quad[1])
        der = process_object_attribute(quad[2])
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
        izq = process_object_attribute(quad[1])
        der = process_object_attribute(quad[2])
        result = izq - der
        store_value(result, quad[3])
        quad_pointer += 1
    elif quad[0] == "*":
        izq = process_object_attribute(quad[1])
        der = process_object_attribute(quad[2])
        result = izq * der
        store_value(result, quad[3])
        quad_pointer += 1
    elif quad[0] == "/":
        izq = process_object_attribute(quad[1])
        der = process_object_attribute(quad[2])
        result = izq / der
        store_value(result, quad[3])
        quad_pointer += 1
    elif quad[0] == "=":
        value = process_object_attribute(quad[1])
        store_value(value, quad[3])
        quad_pointer += 1
    elif quad[0] == "print":
        text = process_object_attribute(quad[3])
        print(text)
        quad_pointer += 1
    elif quad[0] == ">":
        izq = process_object_attribute(quad[1])
        der = process_object_attribute(quad[2])
        store_value(izq > der, quad[3])
        quad_pointer += 1
    elif quad[0] == "<":
        izq = process_object_attribute(quad[1])
        der = process_object_attribute(quad[2])
        store_value(izq < der, quad[3])
        quad_pointer += 1
    elif quad[0] == "==":
        izq = process_object_attribute(quad[1])
        der = process_object_attribute(quad[2])
        store_value(izq == der, quad[3])
        quad_pointer += 1
    elif quad[0] == "!=":
        izq = process_object_attribute(quad[1])
        der = process_object_attribute(quad[2])
        store_value(izq != der, quad[3])
        quad_pointer += 1
    elif quad[0] == "and":
        izq = process_object_attribute(quad[1])
        der = process_object_attribute(quad[2])
        store_value(izq and der, quad[3])
        quad_pointer += 1
    elif quad[0] == "or":
        izq = process_object_attribute(quad[1])
        der = process_object_attribute(quad[2])
        store_value(izq or der, quad[3])
        quad_pointer += 1
    elif quad[0] == "gotoF":
        var = process_object_attribute(quad[1])
        if var:
            quad_pointer += 1
        else:
            quad_pointer = quad[3] - 1
    elif quad[0] == "ERA":
        func = class_type.top() + '.' + quad[1]
        idle_memory = MemoryManager().request_localmemory(function_memories[func])
        if funcs[func]['type'] != 'void':
            call_stack.push(quad[1])
        quad_pointer += 1
    elif quad[0] == "PARAM":
        value = process_object_attribute(quad[1])
        store_param(value, quad[3])
        quad_pointer += 1
    elif quad[0] == "GOSUB":
        if idle_object:
            memory_stack.push(idle_object)
            idle_object = None
        memory_stack.push(idle_memory)
        idle_memory = None
        quad_pointer_stack.push(quad_pointer)
        quad_pointer = funcs[class_type.top() + '.' + quad[3]]['position'] - 1
    elif quad[0] == "ENDFUNC":
        memory_stack.pop()
        quad_pointer = quad_pointer_stack.pop()
        quad_pointer += 1
    elif quad[0] == "VER":
        index = process_object_attribute(quad[1])
        lim_inf = process_object_attribute(quad[2])
        lim_sup = process_object_attribute(quad[3])
        if index < lim_inf or index > lim_sup:
            print("[ERROR] Index out of range ", index, lim_inf, lim_sup)
            sys.exit()
        quad_pointer += 1
    elif quad[0] == "RETURN":
        value = process_object_attribute(quad[3])
        fn_id = call_stack.pop()
        address = modules_addresses[class_type.top() + '.' + fn_id]
        store_value(value, address)
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
    elif quad[0] == "OBJ":
        class_name = quad[1]
        address = quad[3]
        memory = MemoryManager().request_classmemory(class_memories[class_name])
        memory_stack.push(memory)
        class_address.push(address)
        class_type.push(class_name)
        object_subroutines = class_signatures[class_name].copy()
        quad_pointer += 1
    elif quad[0] == "OBJSUB":
        if object_subroutines:
            quad_pointer_stack.push(quad_pointer)
            quad_pointer = object_subroutines.pop(0) - 1
        else:
            generate_object(memory_stack.pop(), class_address.top())
            class_address.pop()
            class_type.pop()
            quad_pointer += 1
    elif quad[0] == "ENDCLS":
        quad_pointer = quad_pointer_stack.pop()
    elif quad[0] == "MEM":
        current_mem = memory_stack.top()
        class_type.push(quad[1])
        class_address.push(quad[3])
        if class_address.top() in current_mem:
            class_vars = current_mem[class_address.top()]
        else:
            class_vars_stack.push(class_vars)
            class_vars = class_vars[class_address.top()]
        idle_object = class_vars.copy()
        quad_pointer += 1
    elif quad[0] == "ENDCLL":
        if class_vars_stack.top():
            class_vars = class_vars_stack.pop()
        else:
            class_vars = {}
        class_type.pop()
        class_address.pop()
        memory_stack.pop()
        quad_pointer += 1
    else:
        raise RuntimeError("Unimplemented Action Code: " + quad[0])


# Virtual machine reads file out.obj and stores its information, then begins the cycle of processing quadruples
# until the current quadruple contains de instruction 'END'
def main():
    global const_table, global_memory, memory_stack, funcs, function_memories, \
        modules_addresses, class_memories, class_signatures

    file_loader = FileLoader("./output/out.obj")
    (quadruples, functions, ret_modules_address,
     func_memory, class_exe, class_memory, constants) = file_loader.get_data()

    funcs = functions
    function_memories = func_memory
    modules_addresses = ret_modules_address
    class_memories = class_memory
    class_signatures = class_exe

    const_table = constants

    global_memory = MemoryManager().request_globalmemory(class_memories['program'])

    main_memory = MemoryManager().request_localmemory(class_memories['main'])
    memory_stack.push(main_memory)

    while True:
        if quadruples[quad_pointer][0] == "END":
            print("Process terminated")
            break
        process_quad(quadruples[quad_pointer])


if __name__ == "__main__":
    main()
