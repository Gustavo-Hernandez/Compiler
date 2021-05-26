class Stack:
    def __init__(self):
        self.stack = []

    def top(self):
        if len(self.stack) < 1:
            return None
        return self.stack[len(self.stack)-1]

    def second(self):
        if len(self.stack) < 2:
            return None
        return self.stack[len(self.stack)-2]

    def pop(self):
        if len(self.stack) < 1:
            return None
        return self.stack.pop()

    def push(self, item):
        self.stack.append(item)

    def size(self):
        return len(self.stack)

    def print(self):
        print(self.stack)
