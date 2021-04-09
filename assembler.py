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
        self.x = 0

        #init tables and other variables
        self.optab = Optab()
        self.symtab = Symtab()

        self.locctr = 0
        self.progCounter = 0x0
        self.baseReg = 0x0
        self.progStart = 0x0
        self.progLine = 0
        self.progLength = 0x0

        #flag bits
        self.b = 0b0
        self.p = 0b1
        self.e = 0b0
        
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


    def assemble(self, content):
        """Assemble file and convert to object code"""
        self.passTwo(self.passOne(content))
        
        
    def passOne(self, content):
        """Assign addresses to each instruction and fill SYMTAB"""


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
        while self.progLine < len(splitContent)-1 and 'END' not in splitContent[self.progLine]:

            print(self.progLine)

            #reset e bit & tempLoc
            self.e = 0b0
            tempLoc = 0
            
            #ignore comment lines, still increment line counter
            print(splitContent[self.progLine])
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
                    print(self.e)
                    
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
                    tempLoc = int(self.getConstLength(operand))
                else:
                    print("Error. Invalid opcode. Halting conversion.")


            #insert line num and locctr to line
            splitContent[self.progLine].insert(0, self.progLine)
            print(self.locctr)
            splitContent[self.progLine].insert(1, hex(self.locctr))

            #write line to intermediate file
            iFile.write(str(splitContent[self.progLine]))
            iFile.write('\n')
            self.progLine += 1
            self.locctr += tempLoc

        #insert line num and locctr to last line
        splitContent[self.progLine].insert(0, self.progLine)
        splitContent[self.progLine].insert(1, hex(self.locctr))

        #write last line to intermediate file
        iFile.write(str(splitContent[self.progLine]))
        iFile.write('\n')

        #save locctr as program length
        self.progLength = self.locctr
    
        iFile.close()

        print(self.symtab.table)

    def getConstLength(self, const):
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
                    
                                                               
    def passTwo(self, intermediate):
        """Perform object code conversions"""
        print("Yeet")
        

    def show_commands(self):
        """lists commands upon user request"""
        print('-h\t--lists all commands')
        print('-o filename\t--opens file for assembling')
        print('-q\t--terminates program')

        
        
                


#end class def

#-----MAIN PROG-----#
a = Assembler()
a.run()
