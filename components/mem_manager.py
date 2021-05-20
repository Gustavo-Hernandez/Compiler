class MemoryManagerMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class MemoryManager (metaclass=MemoryManagerMeta):
    def __init__(self):
        # This structure allows to set the upper and
        # lower limits of an address space.
        # Limits are stablished as the following:
        # scope:{datatype:[min,max]}
        self.map = {
            'global':{
                'int': [1000,1499],
                'float': [1500,1999],
                'string': [2500,3499],
                'boolean': [3500,3999]
            },
            'temp':{
                'int': [4000,4499],
                'float': [4500,4999],
                'string': [5500,5999],
                'boolean': [6000,6999]
            },
            'const':{
                'int': [7000,7499],
                'float': [7500,7999],
                'string': [8500,8999],
                'boolean': [9000,9499]
            },
            'pointers':{
                'int':[12000,13000]
            }
        }
        # This structure allows to keep track of the current
        # requested addresses
        self.counter = {
            'global':{
                'int': 0,
                'float': 0,
                'string': 0,
                'boolean': 0
            },
            'temp':{
                'int': 0,
                'float': 0,
                'string': 0,
                'boolean': 0
            },
            'const':{
                'int': 0,
                'float': 0,
                'string': 0,
                'boolean': 0
            },
            'pointers':{
                'int':0
            }
        }

    # Request and Address given a scope and type
    # The return value is an available address as an integer.
    def requestAddress(self, scope, tp):
        nextAddress = self.map[scope][tp][0] + self.counter[scope][tp]
        if(nextAddress <= self.map[scope][tp][1]):
            self.counter[scope][tp] +=1
            return nextAddress
        raise MemoryError("Insuficient memory to assign a new address")

    def getAddressType(self, memAddress):
        if memAddress >= self.map['global']['int'][0] and memAddress <= self.map['pointers']['int'][1]:
            #Get Scope of INT Address
            if memAddress in range(self.map['global']['int'][0], self.self.map['global']['int'][1]):
                return ['global','int']
            elif memAddress in range(self.map['temp']['int'][0], self.self.map['temp']['int'][1]):
                return ['temp','int']
            elif memAddress in range(self.map['const']['int'][0], self.self.map['const']['int'][1]):
                return ['const','int']
            elif memAddress in range(self.map['pointer']['int'][0], self.self.map['pointer']['int'][1]):
                return ['pointer','int']
            #Get Scope of FLOAT Address
            elif memAddress in range(self.map['global']['float'][0], self.self.map['global']['float'][1]):
                return ['global','float']
            elif memAddress in range(self.map['temp']['float'][0], self.self.map['temp']['float'][1]):
                return ['temp','float']
            elif memAddress in range(self.map['const']['float'][0], self.self.map['const']['float'][1]):
                return ['const','float'] 
            #Get Scope of STRING Address  
            elif memAddress in range(self.map['global']['string'][0], self.self.map['global']['string'][1]):
                return ['global','string']
            elif memAddress in range(self.map['temp']['string'][0], self.self.map['temp']['string'][1]):
                return ['temp','string']
            elif memAddress in range(self.map['const']['string'][0], self.self.map['const']['string'][1]):
                return ['const','string']
            #Get Scope of BOOLEAN Address
            elif memAddress in range(self.map['global']['boolean'][0], self.self.map['global']['boolean'][1]):
                return ['global','boolean']
            elif memAddress in range(self.map['temp']['boolean'][0], self.self.map['temp']['boolean'][1]):
                return ['temp','boolean']
            elif memAddress in range(self.map['const']['boolean'][0], self.self.map['const']['boolean'][1]):
                return ['const','boolean']
        #If memory address not in range return error.
        raise MemoryError("Invalid Memory Address")