#TITLE: SIC/XE Assembler
#PURPOSE: Given an SIC/XE assembly program, create object code and file. 
#AUTHOR: Carson Panduku 
#DATE OF CREATION: March 24, 2021

#imports
from optab import Optab
from symtab import Symtab

#class declaration
class Assembler:
    """Main class controlling the SIC/XE assembler."""

    def __init__(self):
        """Initialize assembler attributes"""

        #tables
        self.optab = Optab()
        self.symtab = Symtab()
        
        #program information
        self.locctr = 0
        self.progCounter = 0x0
        self.baseReg = 0x0
        self.progStart = 0x0
        self.progLine = 0
        self.progLength = 0x0

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
        

    def run(self):
        """Main loop that the user will interact with."""

        #greet user
        print("***-------SIC/XE Assembler Ver. 0.1-------***")
        print("Welcome! Please enter you command.",
         "(type '-h' for a list of commands)")

        #run code based on command entered
        while True:
            command = input()
            
            #quit
            if command == '-q':
                break

            #open file
            elif command[0:2] == '-o':
                if '.txt' in command[3:]:
                    self.open_file(command[3:])
                    print("Done!")
                    
            #print all commands
            elif command[0:2] == '-h':
                self.show_commands()

            #invalid input
            else:
                print(f"{command} is not a supported command")


    def open_file(self, filename):
        """Open files given by the user."""

        #open the file
        try:
            with open(filename) as file_obj:
                content = file_obj.readlines()         
        #if file not found
        except FileNotFoundError:
            print("File not found. Please make sure filepath is correct.")
        file_obj.close()

        
        print("Beginning assembly process.")
        self.assemble(content)
        print("Assembly complete.")


    def assemble(self, content):
        """Assemble file and convert to object code"""
        self.passTwo(self.passOne(content))
        
        
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

        print(splitContent)

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
                    self.e = 0b1
                    
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
                    print(length)
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
        self.n = 0
        self.i  = 0
        self.x = 0   
        self.p = 1
        self.b = 0
        self.e = 0

        #init object code variables
        current_opcode = 0
        target_address = 0

        #process first line
        if 'START' in intermediate[0]:
            progTitle = intermediate[0][self.OPERAND]
            self.progLine += 1
        #IMPLEMENT HEADER RECORD HERE
        #IMPLEMENT FIRST TEXT RECORD
        #main iteration
        while self.progLine < len(intermediate)-1 and 'END' not in intermediate[self.progLine]:

            #init flag bits
            self.n = 0
            self.i  = 0
            self.x = 0   
            self.p = 1
            self.b = 0
            self.e = 0

            #if line is not a comment
            if intermediate[2] != '.':

                #increment PC
                self._incrementPC(intermediate)

                #var definition for easy reference (should only happen if not a comment line)
                symbol = intermediate[self.progLine][self.SYMBOL+2]
                operation = intermediate[self.progLine][self.OPCODE+2]
                operand = intermediate[self.progLine][self.OPERAND+2]
                tempOp = operation

                #check for extended format instruction
                if operation[0] == '+':
                    self.e = 1
                    operation = operation[1:]

                #search optab for opcode
                if self.optab.search(operation):

                    current_opcode = self.optab.table[operation][0]

                    #find addressing mode and format operand
                    operand = self._determineAddressingMode(operand)

                    #is operand a symbol or a constant?
                    if self._isSymbol(operand):

                        #search symtab for symbol
                        
                        if self.symtab.searchSym(operand):
                            target_address = int(self.symtab.table[operand])
                        else:
                            target_address = 0
                            print(operand)
                            print("Error. Undefined symbol.")


                    else:
                        target_address = 0

                    print(self._createObjCode(current_opcode, target_address))

                elif operation == 'BYTE' or operation == 'WORD':

                    #CONVERT CONSTANT TO OBJECT CODE
                    print("yeet")
            self.progLine += 1

    def _determineAddressingMode(self, operand):
        """Uses the operand to set the n, i and x bits"""

        #set n and i bis
        #immediate
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

        return operand
            
                        
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

        print(self.progCounter)


    def _createObjCode(self, opcode, address):
        """Returns a hexadecimal string representing the object code of a single instruction"""

        #init string
        objCode = ''

        #convert opcode to binary string
        opcode = bin(opcode)[2:]

        #add to output string, leaving off last two bits for the n and i bit
        objCode += opcode[:-2]

        #calculate disp

        #immediate
        if self.i == 1 and self.n == 0:
            disp = address
        else:
            disp = address - self.progCounter

        #determine if base addressing should be used
        if disp > 2048 or disp < -2047:
            self.p = 0
            self.b = 1

            #calculate new disp
            disp = address - self.baseReg
            
        else:
            self.p = 1
            self.b = 0

        #convert disp to object code
        disp = self._toBinary(disp)

        #add flag bits
        objCode = objCode + str(self.n) + str(self.i) + str(self.x) + str(self.b) + str(self.p) + str(self.e)

        #add disp
        objCode = objCode + disp

        return hex(int(objCode, 2))


    def _toBinary(self, num):
        """Returns a binary string"""

        newString = ''
        string = ''

        #extended format?
        offset = 12 + (self.e * 8)

        if num >= 0:

            string = bin(num)[2:]

            #leading zeroes     
            for i in range(0, offset-len(string)):
                newString += '0'
            newString += string

            print(newString)

            return newString
            
        else:

            #convert to binary using two's compliment
            #create list of ones and zeros
            string = bin(num)[3:]
            arr =[]
            
            for val in range(0, len(string)):
                arr.append(int(string[val]))


            for char in range(0, len(arr)):
                if arr[char] == 0:
                    arr[char] = 1
                else:
                    arr[char] = 0

            arr = self._addOne(arr, len(arr))

            #convert back to string
            for bit in arr:
                newString += str(bit)

            #leading ones
            for i in range(0, offset-len(string)):
                newString += '1'
            newString += string
            
            return newString


    def _addOne(self, yeet, length):

        for val in range(length, 0, -1):
            if yeet[val-1] == 0:
                yeet[val-1] = 1
                return yeet
            else: 
                yeet[val-1] = 0
                length-=1
        return 0
 

    def show_commands(self):
        """lists commands upon user request"""
        print('-h\t--lists all commands')
        print('-o filename\t--opens file for assembling')
        print('-q\t--terminates program')

        
        
                


#end class def

#-----MAIN PROG-----#
a = Assembler()
a.run()
