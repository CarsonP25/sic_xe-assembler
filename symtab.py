class Symtab:
    """Symbol tables containing labels and addresses"""

    def __init__(self):
        """Init table"""

        self.table = {}


    def addSym(self, label, value):
        """Add an entry to the SYMTAB"""

        self.table[label] = value


    def searchSym(self, label):

        for name in self.table.keys():
            if name == label:
                return True
        return False

        
        


        
