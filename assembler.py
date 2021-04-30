#imports
from optab import Optab
from symtab import Symtab
from littab import Littab
from converter import Converter
from util import Util

#class declaration
class Assembler:
    """Main class controlling the SIC/XE assembler."""

    def __init__(self):
        """Initialize assembler attributes"""

        #tables
        self.optab = Optab()
        self.symtab = Symtab()
        self.littab = Littab()

        #util
        self.conv = Converter()
        self.util = Util()
        
        #program information
        self.locctr = 0
        self.progCounter = 0
        self.baseReg = 0
        self.progStart = 0
        self.progLine = 0
        self.progLength = 0
        self.progTitle = ''

        #flag bits
        self.n = self.i = self.x = self.b = self.p = self.e = 0
        
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
        iFile = open('intermediate.txt', 'w')

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
            self.progTitle = firstLine[self.SYMBOL]
            self.progStart = int(firstLine[self.OPERAND])
            self.locctr = self.progStart
            splitContent[self.progLine].insert(0, self.progLine)
            splitContent[self.progLine].insert(1, hex(self.locctr))
            iFile.write(self.conv._toString(splitContent[self.progLine]))
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

                        #check for literals
                        if operand[0] == '=':
                            if self.littab.searchLit(operand[1:]) == False:
                                self.littab.addLit(operand, self.conv._convertConst(operand[1:]), 
                                    self.util._getConstLength(operand[1:]), '')
                                print(operand[1:])

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
                    tempLoc = int(self.util._getConstLength(operand))
                elif operation == 'BASE':
                    tempLoc = 0
                elif operation == 'LTORG':
                    splitContent[self.progLine].insert(0, self.progLine)
                    splitContent[self.progLine].insert(1, hex(self.locctr))
                    iFile.write(self.conv._toString(splitContent[self.progLine]))
                    self.progLine += 1
                    splitContent = self._flushLitPool(iFile, splitContent)   
                    continue
                else:
                    print("Error. Invalid opcode. Halting conversion.")


            #insert line num and locctr to line
            splitContent[self.progLine].insert(0, self.progLine)
            splitContent[self.progLine].insert(1, hex(self.locctr))

            #write line to intermediate file
            iFile.write(self.conv._toString(splitContent[self.progLine]))
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
            iFile.write(self.conv._toString(splitContent[self.progLine]))
        
        splitContent = self._flushLitPool(iFile, splitContent)

        #save locctr as program length
        self.progLength = self.locctr - self.progStart
    
        iFile.close()

        #return formatted file content
        iFile_r = open('intermediate.txt', 'r')

        content = iFile_r.readlines()
        splitContent = []
        for line in content:
            splitLine = line.split('\t')
            for string in splitLine:
                string.strip()
            splitContent.append(splitLine)

        return splitContent


    def _flushLitPool(self, file, arr):
        """Assign an address for each new literal"""

        for literal in self.littab.table.keys():
            if self.littab.table[literal][2] == '':
                self.littab.assignAddress(literal, self.locctr)
                self.locctr += self.littab.table[literal][1]
                arr.insert(self.progLine, [self.progLine, hex(self.locctr), '*', literal, '\n'])
                file.write(self.conv._toString(['X', hex(self.littab.table[literal][2]), '*', literal, '\n']))
                self.progLine +=1
        return arr


    def passTwo(self, intermediate):
        """Perform object code conversions"""

        print(intermediate)

        eFile = open('prog.txt', 'w')
        oFile = open(self.progTitle.lower() + '.txt', 'w')

        #reset line counter
        self.progLine = 0

        #init flag bits
        self.n = self.i = self.x = self.b = self.e = 0
        self.p = 1

        #init object code variables
        current_opcode = 0
        target_address = 0
        objCode = ''
        curTextRecord = ''
        modRecords = ''

        #process first line
        if 'START' in intermediate[0]:
            self.progTitle = intermediate[0][self.OPERAND]
            eFile.write(self.conv._toString(intermediate[self.progLine]))
            self._headerRecord(oFile)
            curTextRecord = self._newTextRecord(oFile, intermediate[0][1])
            self.progLine += 1
        else:
            self.progTitle = 'untitled'
            curTextRecord = self._newTextRecord(oFile, intermediate[0][1])


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

                #if line is a literal definition
                if symbol == '*':
                    print(self.littab.table[operation][0][2:])
                    self.progLine +=1
                    continue

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
                        intermediate[self.progLine].append('\t' + hex(0x4f0000)[2:])
                        curTextRecord = self._addToTextRecord(oFile, hex(0x4f0000)[2:], intermediate[self.progLine][1], curTextRecord)
                        eFile.write(self.conv._toString(intermediate[self.progLine]))
                        self.progLine += 1
                        continue

                    current_opcode = self.optab.table[operation][0]

                    #is this a format 2 or format 3/4 instruction
                    if self.optab.table[operation][1] == 2:
                        objCode = self._formatTwoObjCode(current_opcode, operand)
                        intermediate[self.progLine].append('\t' + objCode)
                        curTextRecord = self._addToTextRecord(oFile, objCode, intermediate[self.progLine][1], curTextRecord)
                        eFile.write(self.conv._toString(intermediate[self.progLine]))
                        self.progLine += 1
                        continue

                    #find addressing mode and format operand
                    operand = self._determineAddressingMode(operand)

                    #is operand a symbol, constant, or literal
                    if self.util._isSymbol(operand):

                        #search symtab for symbol
                        if self.symtab.searchSym(operand):
                            target_address = int(self.symtab.table[operand])
                        else:
                            target_address = 0
                            print("Error. Undefined symbol.")
                    #literal
                    elif operand[0] == '=':
                        if self.littab.searchLit(operand):
                            target_address = self.littab.table[operand][2]
                    #constant
                    else:
                        target_address = int(operand)
                        self.p = 0
                        self.b = 0

                    objCode = self._createObjCode(current_opcode, target_address)
                    intermediate[self.progLine].append('\t' + objCode)
                    curTextRecord = self._addToTextRecord(oFile, objCode, intermediate[self.progLine][1], curTextRecord)
                    eFile.write(self.conv._toString(intermediate[self.progLine]))
                    if self.b==0 and self.p==0 and self.util._isSymbol(operand):
                        modRecords += 'M' + '0' * (6 - len(hex(int(intermediate[self.progLine][1], 16) + 1)[2:])) + hex(int(intermediate[self.progLine][1], 16) + 1)[2:] + '05' + '\n'
                    self.progLine += 1
                    continue

                elif operation == 'BYTE' or operation == 'WORD':

                    #CONVERT CONSTANT TO OBJECT CODE
                    objCode = self.conv._convertConst(operand)
                    intermediate[self.progLine].append('\t' + objCode)
                    curTextRecord = self._addToTextRecord(oFile, objCode, intermediate[self.progLine][1], curTextRecord)
                    eFile.write(self.conv._toString(intermediate[self.progLine]))
                    self.progLine += 1
                    continue

                elif operation == 'BASE':
                    if self.util._isSymbol(operand):
                        self.baseReg = self.symtab.table[operand]
                        eFile.write(self.conv._toString(intermediate[self.progLine]))
                        self.progLine += 1
                        continue

            eFile.write(self.conv._toString(intermediate[self.progLine]))
            if len(curTextRecord) != 7:
                print('yeet')
                oFile.write(curTextRecord[0:7] + hex(len(curTextRecord[7:])//2)[2:] + curTextRecord[7:] + '\n')
                curTextRecord = self._newTextRecord(oFile, intermediate[self.progLine][1])            
            self.progLine += 1

        #write last line and last text record
        eFile.write(self.conv._toString(intermediate[self.progLine]))
        if len(curTextRecord) > 7:
            oFile.write(curTextRecord[0:7] + hex(len(curTextRecord[7:])//2)[2:] + curTextRecord[7:] + '\n')
        oFile.write(modRecords)
        self._endRecord(oFile)
        eFile.close()
        oFile.close()


    def _determineAddressingMode(self, operand):
        """Uses the operand to set the n, i and x bits"""

        #set n and i bis
        if operand == '':
            self.n == 1
            self.i == 1
            return operand

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
        #simple or literal
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

        return objCode


    def _headerRecord(self, file):
        """Creates a header record and writes it to the file."""
        record = 'H'

        #add program title
        offset = 6 - len(self.progTitle)
        record += self.progTitle + ' ' * offset

        #add starting address
        offset = 6 - len(hex(self.progStart)[2:])
        record += '0' * offset + hex(self.progStart)[2:]

        #add program length 
        offset = 6 - len(hex(self.progLength)[2:])
        record += '0' * offset + hex(self.progLength)[2:]

        file.write(record + '\n')


    def _endRecord(self, file):
        """Creates an end record and writes it to the file"""
        record = 'E'

        #add address of first instruction
        offset = 6 - len(hex(self.progStart)[2:])
        record += '0' * offset + hex(self.progStart)[2:]

        file.write(record + '\n')


    def _newTextRecord(self, file, address, objCode=''):
        """Initializes a new text record"""
        record = 'T'

        #add starting address of objCode in this record
        offset = 6 - len(address[2:])
        record += '0' * offset + address[2:] + objCode

        return record


    def _addToTextRecord(self, file, objCode, address, record):
        """If there is room, add to text record."""

        print(objCode)

        #check length of text record
        if len(record) + len(objCode) > 69:
            #determine length of record
            wholeRecord = record[0:7] + hex(len(record[7:])//2)[2:] + record[7:]
            file.write(wholeRecord + '\n')
            record = self._newTextRecord(file, address, objCode)
            return record
        else:
            record += objCode
            return record




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

