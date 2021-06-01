# ------------------------------------------------------------
# stack.py
# A01364749 Gustavo Hernandez Sanchez
# A01364701 Luis Miguel Maawad Hinojosa
# ------------------------------------------------------------

# Class definition for Stack data structure
class Stack:
    # Class initializes a list that will serve as the stack
    def __init__(self):
        self.stack = []

    # Function returns top value of stack without popping its value
    def top(self):
        if len(self.stack) < 1:
            return None
        return self.stack[len(self.stack)-1]

    # Function returns second value form the top of the stack without popping any values
    def second(self):
        if len(self.stack) < 2:
            return None
        return self.stack[len(self.stack)-2]

    # Function returns top value of stack and removes it from stack
    def pop(self):
        if len(self.stack) < 1:
            return None
        return self.stack.pop()

    # Function adds value to the top of the stack
    def push(self, item):
        self.stack.append(item)

    # Function returns current value of stack
    def size(self):
        return len(self.stack)

    # Dev function to print stack
    def print(self):
        print(self.stack)
