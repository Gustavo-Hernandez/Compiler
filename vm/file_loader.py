# ------------------------------------------------------------
# function_dir.py
# A01364749 Gustavo Hernandez Sanchez
# A01364701 Luis Miguel Maawad Hinojosa
# ------------------------------------------------------------

import re


# Class file loader used to read parser output file
class FileLoader:
    # Class utilizes dictionaries for all 'paragraphs' of output file
    # Class uses regex to process integers and floats
    def __init__(self, filepath):
        self.__float_regex = re.compile(r'^-?\d*[.,]?\d*$')
        self.__int_regex = re.compile(r'^-?[0-9]+$')
        self.__quads = []
        self.__functions = {}
        self.__ret_module_address = {}
        self.__func_memory = {}
        self.__class_memory = {}
        self.__class_exe = {}
        self.__const = {}
        self.__load_obj_file(filepath)

    # Function used to read output file and process data cording to the current 'paragraph'
    # Function receives output file path
    def __load_obj_file(self, filepath):
        sections = ["quads", "signatures",
                    "ret_modules_address", "function_memory",
                    "class_signatures",
                    "class_memory", "const"]
        section_counter = 0
        r = open(filepath, 'r')
        for line in r:
            line = line.strip("\n").split(" ")
            if len(line) < 2:
                section_counter += 1
            elif sections[section_counter] == "quads":
                line = self.__format_quad(line)
                self.__quads.append(line)
            elif sections[section_counter] == "signatures":
                self.__functions[line[0] + '.' + line[1]] = {
                    'type': line[2], 'position': int(line[3]), 'params': line[4:len(line) - 1]}
            elif sections[section_counter] == "ret_modules_address":
                self.__ret_module_address[line[0] + '.' + line[1]] = int(line[2])
            elif sections[section_counter] == "function_memory":
                self.__func_memory[line[0] + '.' + line[1]] = self.__process_func_size(line)
            elif sections[section_counter] == "class_signatures":
                self.__class_exe[line[0]] = self.__process_size(line)
            elif sections[section_counter] == "class_memory":
                self.__class_memory[line[0]] = self.__process_size(line)
            elif sections[section_counter] == "const":
                if len(line) > 2:
                    for i in range(2, len(line)):
                        line[1] += " " + line[i]
                self.__const[int(line[0])] = self.__process_const(line[1])

    # Function used to process quadruple lines
    # Function receives line
    def __format_quad(self, list):
        for i in range(1, 4):
            if list[i] == '$':
                list[i] = None
            elif self.__int_regex.match(list[i]):
                list[i] = int(list[i])
        return list

    # Function used to process constants table
    # Function receives line
    def __process_const(self, const):
        if self.__int_regex.match(const):
            n_const = int(const)
        elif self.__float_regex.match(const):
            n_const = float(const)
        elif const == 'true':
            n_const = True
        elif const == "false":
            n_const = False
        else:
            n_const = const.strip('"')
        return n_const

    # Function used to process size lines
    # Function receives line
    def __process_size(self, line):
        return list(map(lambda x: int(x), (line[1:len(line)])))

    # Function used to process function sizes
    # Function receives line
    def __process_func_size(self, line):
        return list(map(lambda x: int(x), (line[2:len(line) - 1])))

    # Function used to read data form virtual machine
    def get_data(self):
        return self.__quads, self.__functions, self.__ret_module_address, self.__func_memory, \
               self.__class_exe, self.__class_memory, self.__const
