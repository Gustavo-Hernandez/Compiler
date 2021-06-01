import os
import re
from components.variable_table import VariableTable
from components.function_dir import FunctionDirectory
from components.mem_manager import MemoryManager
from components.code_gen import CodeGenerator


class Semantics:
    def __init__(self):
        self.var_tables = {}
        self.cte_table = VariableTable()
        self.global_var_table = VariableTable()
        self.var_table = None
        self.current_func_dir = None
        self.current_table = None
        self.called_function = None
        self.current_function = None
        self.current_function_types = None
        self.current_function_ret = None
        self.current_arr = None
        self.object_queue = []
        self.current_arr_id = ''
        self.code_gen = CodeGenerator()
        self.class_dir = {}
        self.program_vars = {}
        self.interfaces = {}
        self.current_interface = {}

    def end_program(self):
        self.code_gen.end_prog()
        self.program_vars['program'] = self.program_vars['program'].directory
        val = self.program_vars['program']['main']
        self.code_gen.add_main_dir(val['position'])

    def init_program(self, program_name):
        self.current_func_dir = FunctionDirectory()
        self.current_func_dir.add_function(program_name, 'program', 0)
        self.program_vars['program'] = self.current_func_dir
        self.var_table = self.program_vars['program'].get_var_table()
        self.current_table = self.global_var_table

    def store_global_statements(self):
        self.code_gen.add_main()
        self.var_tables['global'] = self.program_vars['program'].store_global_vars(
            'program')
        self.code_gen.current_scope = "interfaces"

    def set_current_function_directory_as_global(self):
        self.current_func_dir = self.program_vars['program']

    def store_interface(self, interface_name):
        self.interfaces[interface_name] = self.current_interface.directory

    def init_current_interface(self):
        self.current_interface = FunctionDirectory()

    def store_class(self, id, visibility, extension, class_temporals, implemented_id, code_counter, exe_list):
        # Class size calculation
        class_size = {}
        class_size.update(MemoryManager().get_class_vars())
        class_size.update(class_temporals)

        class_address = MemoryManager().request_class_address(id, visibility)
        exe = exe_list + [code_counter]
        self.class_dir[id] = {"visibility": visibility, "extension": extension,
                              'functions': self.current_func_dir.directory,
                              'var_table': self.var_table.table, 'size': class_size,
                              'address': class_address, 'execution': exe}
        # Validate class implementation
        if implemented_id:
            for fn in self.interfaces[implemented_id]:
                if fn in self.current_func_dir.directory:
                    assert self.interfaces[implemented_id][fn]['return_type'] == self.current_func_dir.directory[
                        fn]['return_type'], "Implemented function " + fn + " has a different return type"
                    assert self.interfaces[implemented_id][fn]['params'] == self.current_func_dir.directory[
                        fn]['params'], "Implemented function " + fn + " has a different parameters"
                else:
                    raise ValueError(
                        "Class " + id + " does not implement '" + fn + "' function from interface: " + implemented_id)
        # Clear context
        MemoryManager().reset_class_context()

    def init_class(self, id):
        # Class Function Directory reset.
        if id in self.class_dir:
            raise KeyError("Class " + id + " has already been declared.")
        if id in self.interfaces:
            raise KeyError("Identifier " +
                           id + " has already been declared as an interface.")
        self.code_gen.current_scope = "class"
        self.current_func_dir = FunctionDirectory()
        self.current_func_dir.global_vartable = self.global_var_table
        self.var_table = VariableTable()
        self.current_func_dir.class_vartable = self.var_table
        self.current_table = self.var_table

    def store_class_temporals(self):
        self.code_gen.reset_t_counter()
        self.code_gen.current_scope = 'local'
        self.code_gen.end_class()

    def handle_class_extension(self, id_extended_class):
        if id_extended_class not in self.class_dir:
            raise KeyError(
                "Can not extend from non existent class: " + id_extended_class)
        elif self.class_dir[id_extended_class]['visibility'] == 'blocked':
            raise KeyError(
                "Can not extend from blocked class: " + id_extended_class)
        else:
            self.current_func_dir.directory = self.class_dir[id_extended_class]['functions'].copy(
            )
            self.var_table.table = self.class_dir[id_extended_class]['var_table'].copy(
            )
            size = self.class_dir[id_extended_class]['size'].copy()
            MemoryManager().class_counter_offset(
                size['c_int'], size['c_float'], size['c_string'], size['c_bool'])
        return self.class_dir[id_extended_class]['execution'].copy()

    def set_current_scope(self, scope):
        self.code_gen.current_scope = scope

    def end_main(self):
        self.var_tables['main'] = self.current_func_dir.delete_var_table(
            'main')
        self.code_gen.reset_t_counter()

    def init_main(self):
        self.current_func_dir.add_function(
            'void', 'main', self.code_gen.counter)
        self.code_gen.current_scope = 'local'
        self.current_table = self.current_func_dir.get_var_table()

    def solve_statement(self):
        self.code_gen.final_solve()

    def end_function(self):
        self.code_gen.end_func()

    def module_vartable_export(self, id):
        # Release Memory and Store clean vartable
        self.var_tables[id] = self.current_func_dir.delete_var_table(id)
        # Reset temporal Counters
        self.code_gen.reset_t_counter()

    def process_void_module_declaration(self, id):
        if self.code_gen.current_scope != 'interfaces':
            self.current_func_dir.add_function(
                'void', id, self.code_gen.counter)
            self.current_table = self.current_func_dir.get_var_table()
        else:
            self.current_interface.add_function(
                'void', id, self.code_gen.counter)
            self.current_interface.params = {}

    def end_return_module(self, module_type):
        self.code_gen.final_solve()
        self.code_gen.add_return(module_type)

    def process_module_ret_declaration(self, type_atomic, id):
        if self.code_gen.current_scope != 'interfaces':
            self.current_func_dir.add_function(
                type_atomic, id, self.code_gen.counter)
            self.var_table.set_array(False)
            self.var_table.set_type(type_atomic)
            self.var_table.store_id(id)
            self.var_table.register('class', self.cte_table)
            self.current_table = self.current_func_dir.get_var_table()
        else:
            self.current_interface.add_function(
                type_atomic, id, self.code_gen.counter)
            self.current_interface.params = {}

    def process_param(self, type_atomic, id):
        if self.code_gen.current_scope != 'interfaces':
            self.current_func_dir.store_param(type_atomic, id)
        else:
            self.current_interface.store_param(type_atomic, id)

    def process_object_call(self, id, address):
        if self.current_function:
            tp = len(self.current_function_types)
            self.code_gen.validate_params(tp)
            self.code_gen.go_sub(self.current_function)
            self.code_gen.end_call()
            ret_type = self.current_function_ret
            if ret_type != "void":
                mem_dir = self.class_dir[id]['var_table'][self.current_function]['virtual_address']
                result = self.code_gen.call_return(
                    str(address) + '.' + str(mem_dir), ret_type)  # Doubt Comment Luis
                self.code_gen.addOperand(result)
            else:
                result = self.current_function_ret
            self.current_function = None
            self.current_function_types = None
            self.current_function_ret = None
            self.code_gen.operators.pop()
        else:
            result = 'attribute'
        return result

    def validate_object_call(self, obj, element):  # Comment Luis
        if obj in self.current_table.table:
            if self.current_table.table[obj]['type'] not in ['int', 'float', 'bool', 'string']:
                class_name = self.current_table.table[obj]['type']
                address = self.current_table.table[obj]['virtual_address']
            else:
                raise TypeError("Variable " + obj + " is not an object")
        elif obj in self.var_table.table:
            if self.var_table.table[obj]['type'] not in ['int', 'float', 'bool', 'string']:
                class_name = self.var_table.table[obj]['type']
                address = self.var_table.table[obj]['virtual_address']
            else:
                raise TypeError("Variable " + obj + " is not an object")
        else:
            raise NameError("Unknown variable " + obj)

        v_list = self.class_dir[class_name]['var_table']
        f_list = self.class_dir[class_name]['functions']

        if element in f_list:
            self.current_function = element
            self.code_gen.add_mem(address, class_name)
            self.current_function_types = list(
                f_list[element]['params'].values())
            self.current_function_ret = f_list[element]['return_type']
            self.code_gen.generate_era(element)
        elif element in v_list:
            self.code_gen.types.push(v_list[element]['type'])
            self.code_gen.addOperand(str(address) + '.' +
                                     str(v_list[element]['virtual_address']))
        else:
            raise NameError(
                class_name + " objects have no attribute or method " + element)

        return class_name, address

    def validate_class_function_call(self):
        if not self.current_function:
            raise TypeError("Object attribute is not function")

    def validate_function_params(self):
        self.code_gen.param_solve()
        tp = self.current_function_types
        if len(tp) > self.code_gen.par_counter:
            self.code_gen.param(tp[self.code_gen.par_counter]['type'],
                                tp[self.code_gen.par_counter]['virtual_address'])
        else:
            raise TypeError("Function parameters exceed expected parameters")

    def end_function_call(self):
        tp = len(self.current_function_types)
        self.code_gen.validate_params(tp)
        self.code_gen.go_sub(self.current_function)
        ret_type = self.current_function_ret
        if ret_type != "void":
            mem_dir = self.var_table.table[self.current_function]['virtual_address']
            address = self.code_gen.call_return(mem_dir, ret_type)
            self.code_gen.addOperand(address)
        else:
            address = self.current_function_ret
        self.current_function = None
        self.current_function_types = None
        self.current_function_ret = None
        self.code_gen.operators.pop()
        return address

    def validate_function_existance(self, function_id):
        if function_id in self.current_func_dir.directory:
            self.code_gen.generate_era(function_id)
            self.current_function = function_id
            self.current_function_types = list(
                self.current_func_dir.directory[self.current_function]['params'].values())
            self.current_function_ret = self.current_func_dir.directory[
                self.current_function]['return_type']
        else:
            raise NameError(
                "Function call to undefined function: " + function_id)

    def process_declaration(self):
        tp = self.current_table.type_var
        self.current_table.register(
            self.code_gen.current_scope, self.cte_table)
        for obj in self.object_queue:
            self.code_gen.add_object(
                tp, self.current_table.table[obj]['virtual_address'])
        self.object_queue = []

    def process_id_array(self, id_array):
        elm = []
        for e in re.split("\[(.*?)\]", id_array):
            if e != '':
                elm.append(e)
        self.current_table.store_id(elm[0])
        dims = []
        for i in range(1, len(elm)):
            dims.append(int(elm[i]))
        self.current_table.set_array(True)
        self.current_table.set_dims(dims)

    def register_id(self, id):
        self.current_table.store_id(id)
        self.current_table.set_array(False)

    def process_initialized_declaration(self, id, operator):
        self.register_id(id)
        self.code_gen.operators.push(operator)
        self.current_table.register(
            self.code_gen.current_scope, self.cte_table)
        self.code_gen.types.push(self.current_table.table[id]['type'])
        self.code_gen.addOperand(
            self.current_table.table[id]['virtual_address'])

    def enqueue_object(self):
        self.object_queue = self.current_table.queue

    def validate_object_declaration(self, class_id, id):
        if class_id in self.class_dir:
            self.current_table.set_type(class_id)
        else:
            raise TypeError("Class " + class_id + " does not exist")
        self.register_id(id)

    def end_printing_statement(self):
        self.code_gen.printing()

    def end_reading_statement(self):
        self.code_gen.reading()

    def validate_if_statement(self):
        self.code_gen.final_solve()
        self.code_gen.condition_1()

    def end_if_statement(self):
        self.code_gen.condition_2()

    def process_else_block(self):
        self.code_gen.condition_3()

    def init_loop(self):
        self.code_gen.loop_1()

    def validate_loop(self):
        self.code_gen.final_solve()
        self.code_gen.loop_2()

    def end_loop(self):
        self.code_gen.loop_3()

    def add_operator_and_or(self, operator):
        self.code_gen.addOperator_4(operator)

    def add_operator_comparison(self, operator):
        self.code_gen.addOperator_3(operator)

    def add_operator_addition(self, operator):
        self.code_gen.addOperator_1(operator)

    def add_operator_multiplication(self, operator):
        self.code_gen.addOperator_2(operator)

    def add_operator(self, operator):
        self.code_gen.addOperator(operator)

    def solve_factor(self):
        self.code_gen.factor_solve()

    def store_constant(self, value, type_atomic):
        var_cte = self.cte_table.insert_cte(value, type_atomic)
        self.code_gen.types.push(type_atomic)
        self.code_gen.addOperand(var_cte)

    def store_current_type(self, type_atomic):
        self.current_table.set_type(type_atomic)

    def set_array_dims(self):
        if self.current_arr:
            self.code_gen.set_dim(
                self.current_arr['dims'], self.cte_table.insert_cte(0, 'int'))
        else:
            raise TypeError("Variable is not array")

    def solve_array_expression(self):
        self.code_gen.arr_solve()
        self.code_gen.operators.pop()

    def validate_array(self, id):
        if id not in self.current_table.table and self.current_table != self.var_table and self.current_table != self.global_var_table:
            if id not in self.var_table.table:
                if self.global_var_table.get_is_array(id):
                    self.current_arr = self.global_var_table.table[id]
                    self.current_arr_id = id
                else:
                    self.code_gen.types.push(
                        self.global_var_table.get_type(id))
                    self.code_gen.addOperand(
                        self.global_var_table.table[id]['virtual_address'])
            else:
                if self.var_table.get_is_array(id):
                    self.current_arr = self.var_table.table[id]
                    self.current_arr_id = id
                else:
                    self.code_gen.types.push(self.var_table.get_type(id))
                    self.code_gen.addOperand(
                        self.var_table.table[id]['virtual_address'])
        else:
            if self.current_table.get_is_array(id):
                self.current_arr = self.current_table.table[id]
                self.current_arr_id = id
            else:
                self.code_gen.types.push(self.current_table.get_type(id))
                self.code_gen.addOperand(
                    self.current_table.table[id]['virtual_address'])

    def array_declaration(self, id):
        if self.current_arr and id == self.current_arr_id:
            cte_mem = self.cte_table.insert_cte(
                self.current_arr['virtual_address'], 'int')
            self.code_gen.final_arr(
                cte_mem, self.current_arr['type'], self.current_arr['dims'])
            self.current_arr = None

    def export_quads(self):
        quads = ""
        for quad in self.code_gen.quadruples:
            arr = [str(p) if p is not None else '$' for p in quad]
            quads += arr[0] + " " + arr[1] + " " + arr[2] + " " + arr[3] + "\n"
        return quads

    def export_classes_size(self):
        size_export = ""
        for key in self.class_dir:
            size_export += key
            for dim_size in self.class_dir[key]['size']:
                size_export += " " + str(self.class_dir[key]['size'][dim_size])
            size_export += "\n"
        for var in self.program_vars['program']:
            size_export += var
            for dim_size in self.program_vars['program'][var]['size']:
                size_export += " " + \
                    str(self.program_vars['program'][var]['size'][dim_size])
            size_export += "\n"
        return size_export

    def export_class_signature(self):
        size_export = ""
        for key in self.class_dir:
            size_export += key
            for exe in self.class_dir[key]['execution']:
                size_export += " " + str(exe)
            size_export += "\n"
        return size_export

    def export_functions_size(self):
        size_export = ""
        for key in self.class_dir:
            for fn in self.class_dir[key]['functions']:
                rc = " "
                for dim_size in self.class_dir[key]['functions'][fn]['size']:
                    rc += str(self.class_dir[key]['functions'][fn]
                              ['size'][dim_size]) + " "
                size_export += key + " " + fn + rc + "\n"
        return size_export

    def export_functions_signature(self):
        signatures_export = ""
        for key in self.class_dir:
            for fn in self.class_dir[key]['functions']:
                rc = " " + self.class_dir[key]['functions'][fn]['return_type'] + \
                    " " + str(self.class_dir[key]
                              ['functions'][fn]['position']) + " "
                for param in self.class_dir[key]['functions'][fn]['params']:
                    rc += str(self.class_dir[key]['functions'][fn]
                              ['params'][param]['type']) + " "
                signatures_export += key + " " + fn + rc + "\n"
        return signatures_export

    def export_ret_functions_address(self):
        addresses = ""
        for key in self.class_dir:
            for fn in self.class_dir[key]['functions']:
                if fn in self.class_dir[key]['var_table']:
                    addresses += key + " " + fn + " " + \
                        str(self.class_dir[key]['var_table']
                            [fn]['virtual_address']) + "\n"
        return addresses

    def export_constants(self):
        constants = ""
        for cte in self.cte_table.table:
            constants += str(self.cte_table.table[cte]
                             ['virtual_address']) + " " + str(cte) + "\n"
        return constants

    def generateObj(self, dir_path):
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
        output = self.export_quads() + "\n" + self.export_functions_signature() + "\n" + self.export_ret_functions_address() + "\n" + \
            self.export_functions_size() + "\n" + self.export_class_signature() + "\n" + self.export_classes_size() + "\n" \
            + self.export_constants()
        filewriter = open(dir_path + "/out.obj", 'w')
        filewriter.write(output)
