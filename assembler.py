#imports
from optab import Optab
from symtab import Symtab
from converter import Converter

#class declaration
class Assembler:
    """Main class controlling the SIC/XE assembler."""

    def __init__(self):
        """Initialize assembler attributes"""

        #tables
        self.optab = Optab()
        self.symtab = Symtab()

        #util
        self.conv = Converter()
        
        #program information
        self.locctr = 0
        self.progCounter = 0
        self.baseReg = 0
        self.progStart = 0
        self.progLine = 0
        self.progLength = 0

        #flag bits
        self.n = 0
        self.i = 0
        self.x = 0
        self.b = 0
        self.p = 0
        self.e = 0
        
        #constants (not actaully constant)
        self.SYMBOL = 0
        self.OPCODE = 1
        self.OPERAND = 2
        self.COMMENT = 3

        #registers
        self.registers = {
            'A': 0,
            'X': 1,
            'L': 2,
            'B': 3,
            'S': 4,
            'T': 5,
            'F': 6
        }
    
    def assemble(self, content):
        """Assemble file and convert to object code"""
        file = self.passOne(content)
        self.passTwo(file)
        
        
    def passOne(self, content):
        """Assign addresses to each instruction and fill SYMTAB"""

        endFlag = True


        #open intermediate file for writing
        iFile = open('intermdiate.txt', 'w')

        splitContent = []
        tempLoc = 0
        
        #organize file content to make processing easier
        for line in content:
            splitLine = line.split('\t')
            for string in splitLine:
                string.strip()
            splitContent.append(splitLine)

        #process first line
        firstLine = splitContent[0]

        #check for START directive
        if firstLine[self.OPCODE] == 'START':
            self.progStart = int(firstLine[self.OPERAND])
            self.locctr = self.progStart
            self.progLine += 1
        else:
            self.locctr = 0

        #init function vars
        symbol = ''
        operation = ''
        tempOp = ''
        
        #main iteration
        while 'END' not in splitContent[self.progLine]:

            #reset e bit & tempLoc
            self.e = 0b0
            tempLoc = 0
            
            #ignore comment lines, still increment line counter
            if splitContent[self.progLine][0] == '' or splitContent[self.progLine][0][0] != '.':

                #var definition for easy reference (should only happen if not a comment line)
                symbol = splitContent[self.progLine][self.SYMBOL]
                operation = splitContent[self.progLine][self.OPCODE]
                operand = splitContent[self.progLine][self.OPERAND]
                tempOp = operation

                #symbol in label column
                if splitContent[self.progLine][self.SYMBOL] != '':
                    if self.symtab.searchSym(symbol):
                        print("Error. Duplicate symbol detected. Halting conversion.")
                        #error flag???
                        break;
                    else:
                        self.symtab.addSym(symbol, self.locctr)

                #process operation column
                #check for extended format
                if operation[0] == '+':
                    tempOp = operation[1:]
                    self.e = 1
                    
                if self.optab.search(tempOp):
                    tempLoc = max(int(self.optab.table[tempOp][1]), (self.e * 4))
                elif operation == 'WORD':
                    tempLoc = 0x3
                elif operation == 'RESW':
                    tempLoc = 3 * int(operand)
                elif operation == 'RESB':
                    tempLoc = int(operand)
                elif operation == 'BYTE':
                    print(operand)
                    tempLoc = int(self._getConstLength(operand))
                elif operation == 'BASE':
                    tempLoc = 0
                else:
                    print("Error. Invalid opcode. Halting conversion.")


            #insert line num and locctr to line
            splitContent[self.progLine].insert(0, self.progLine)
            splitContent[self.progLine].insert(1, hex(self.locctr))

            #write line to intermediate file
            iFile.write(self._toString(splitContent[self.progLine]))
            self.progLine += 1
            self.locctr += tempLoc

            if self.progLine == len(splitContent):
                endFlag = False
                break;

        #only do this if END was encountered
        if endFlag:
            
            #insert line num and locctr to last line
            splitContent[self.progLine].insert(0, self.progLine)
            splitContent[self.progLine].insert(1, hex(self.locctr))

            #write last line to intermediate file
            iFile.write(self._toString(splitContent[self.progLine]))

        #save locctr as program length
        self.progLength = self.locctr
    
        iFile.close()

        return splitContent

    def _getConstLength(self, const):
        """Returns the length in bytes of an integer or hex constant"""

        length = 0

        if const[0] == 'C':
            for char in const[2:-2]:
                if char != "'":
                    length += 1
            return length
                
        elif const[0] == 'X':
            for char in const[2:-1]:
                if char != "'":
                    length += 1
            return int(length/2)                   
            return length

    def _toString(self, arr):
        """Function to make intermediate file easier to understand"""

        string = ''
        for element in arr[:-1]:
            string += str(element) + '\t'
        string += arr[-1]

        return string

                                                                 
    def passTwo(self, intermediate):
        """Perform object code conversions"""

        #reset line counter
        self.progLine = 0

        #init flag bits
        self.n = self.i = self.x = self.b = self.e = 0
        self.p = 1

        #init object code variables
        current_opcode = 0
        target_address = 0
        objCode = ''

        #process first line
        if 'START' in intermediate[0]:
            progTitle = intermediate[0][self.OPERAND]
            self.progLine += 1
        #IMPLEMENT HEADER RECORD HERE
        #IMPLEMENT FIRST TEXT RECORD
        #main iteration
        while self.progLine < len(intermediate)-1 and 'END' not in intermediate[self.progLine]:

            objCode = ''

            #init flag bits
            self.n = self.i = self.x = self.b = self.e = 0
            self.p = 1

            #if line is not a comment
            if intermediate[self.progLine][2].rstrip() != '.':

                #increment PC
                self._incrementPC(intermediate)

                #var definition for easy reference (should only happen if not a comment line)
                symbol = intermediate[self.progLine][self.SYMBOL+2]
                operation = intermediate[self.progLine][self.OPCODE+2]
                operand = intermediate[self.progLine][self.OPERAND+2]

                #check for extended format instruction
                if operation[0] == '+':
                    self.e = 1
                    self.b = 0
                    self.p = 0
                    operation = operation[1:]

                #search optab for opcode
                if self.optab.search(operation):

                    #JSUB will always generate the same objcode
                    if operation == 'RSUB':
                        print(hex(0x4f0000))
                        self.progLine += 1
                        continue

                    current_opcode = self.optab.table[operation][0]

                    #is this a format 2 or format 3/4 instruction
                    if self.optab.table[operation][1] == 2:
                        print(self._formatTwoObjCode(current_opcode, operand))
                        continue

                    #find addressing mode and format operand
                    operand = self._determineAddressingMode(operand)

                    #is operand a symbol or a constant?
                    if self._isSymbol(operand):

                        #search symtab for symbol
                        if self.symtab.searchSym(operand):
                            target_address = int(self.symtab.table[operand])
                        else:
                            target_address = 0
                            print("Error. Undefined symbol.")

                    else:
                        target_address = int(operand)
                        self.p = 0
                        self.b = 0

                    print(self._createObjCode(current_opcode, target_address))

                elif operation == 'BYTE' or operation == 'WORD':

                    #CONVERT CONSTANT TO OBJECT CODE
                    print(self.conv._convertConst(operand))

                elif operation == 'BASE':
                    if self._isSymbol(operand):
                        self.baseReg = self.symtab.table[operand]
                        
            print("----------------------------------")
            self.progLine += 1


    def _determineAddressingMode(self, operand):
        """Uses the operand to set the n, i and x bits"""

        #set n and i bis
        #immediate
        if operand == '':
            self.n == 1
            self.i == 1
            return operand
            
        if operand[0] == '#':
            self.n = 0
            self.i = 1
            operand = operand[1:]
        #indirect
        elif operand[0] == '@':
            self.n = 1
            self.i = 0
            operand = operand[1:]
        #simple
        else:
            self.n = 1
            self.i = 1

        #set x bit
        if ',X' in operand:
            self.x = 1
            operand = operand[:-2]
        else:
            self.x = 0

        return operand.rstrip()
            
                        
    def _isSymbol(self, operand):
        """Returns true if operand is a symbol, returns false otherwise"""

        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

        for char in operand:
            if char in letters:
                return True

        return False


    def _incrementPC(self, file):
        """Increments the program counter"""

        temp = self.progLine

        #comment lines and certain directives do not implement the locctr
        #and thus should not increment the program counter either
        
        while self.progCounter == int(file[temp][1][2:], 16):
            self.progCounter = int(file[temp+1][1][2:], 16)
            if self.progCounter == int(file[temp][1][2:], 16):
                temp+=1


    def _createObjCode(self, opcode, address):
        """Returns a hexadecimal string representing the object code of a single instruction"""

        #init string
        objCode = ''

        #convert opcode to binary string
        opcode = bin(opcode)[2:]
        offset = 8 - len(opcode)
        opcode = ('0' * offset) + opcode

        #add to output string, leaving off last two bits for the n and i bit
        objCode += opcode[:-2]

        #calculate disp
        if self.i == 1 and self.n == 0:
            if self.p == 1:
                disp = address - self.progCounter
            else:
                disp = address
        elif self.e == 1:
            self.b = 0
            self.p = 0
            disp = address                 
        else:
            disp = address - self.progCounter

        #determine if base addressing should be used
        if (disp > 2048 or disp < -2047) and self.e == 0:
            self.p = 0
            self.b = 1

            #calculate new disp
            disp = address - self.baseReg   

        #convert disp to object code
        disp = self.conv._toBinary(disp, self.e)
        
        #add flag bits
        objCode = objCode + str(self.n) + str(self.i) + str(self.x) + str(self.b) + str(self.p) + str(self.e)

        #add disp
        objCode = objCode + disp

        hexCode = ''

        for val in range(0, len(objCode), 4):
            hexCode += self.conv._toHalfByte(objCode[val:val+4])

        return hexCode


    def _formatTwoObjCode(self, current_opcode, operand):
        """Returns object code for a format two instruction"""
        objCode = ''
        regOperands = operand.split(',')
        objCode += str(hex(current_opcode))[2:]

        for value in range(0, 2):
            try:
                objCode += self.conv._toHalfByte(self.registers[regOperands[value]])
            except IndexError:
                objCode += '0'

        self.progLine += 1
        return objCode


    def reset(self):
        """reset assembler attributes so a new file can be processed"""

        #reset flag bits
        self.n = self.i = self.x = self.b = self.e = 0
        self.p = 1

        #reset line counter and program counter
        self.progLine = 0
        self.progCounter = 0

        #clear symbol table
        self.symtab.table.clear()


#end class def

