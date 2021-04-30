class Converter:
    """Utility class for converting"""

    def _toBinary(self, num, e_bit):
        """Returns a binary string"""

        newString = ''
        string = ''

        #extended format?
        offset = 12 + (e_bit * 8)

        if num >= 0:

            string = bin(num)[2:]

            #leading zeroes     
            for i in range(0, offset-len(string)):
                newString += '0'
            newString += string

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
            newString = ('1' * (offset - len(newString))) + newString
            
            return newString


    def _addOne(self, yeet, length):
        """Adds one to a binary string"""

        for val in range(length, 0, -1):
            if yeet[val-1] == 0:
                yeet[val-1] = 1
                return yeet
            else: 
                yeet[val-1] = 0
                length-=1
        return 0

    def _convertConst(self, operand):
        """Converts a character or hexadecimal constant to object code"""

        hexString = ''

        #character constant
        if operand[0] == 'C':
            for char in operand[1:].rstrip():
                if char != "'":
                    hexString += hex(ord(char))[2:]

            return hex(int(hexString, 16))[2:]

        #hex constant
        else:
            for char in operand[1:]:
                if char != "'":
                    hexString += char

            constStr = hex(int(hexString, 16))
            return '0' * (len(constStr) % 2) + constStr[2:]
            
            
    def _toHalfByte(self, num):
        """Returns a single hex character"""

        if isinstance(num, int):
            hexChar = hex(num)
            hexChar = hexChar[2:]
        else:
            hexChar = hex(int(num, 2))
            hexChar = hexChar[2:]

        return hexChar


    def _toString(self, arr):
        """Function to make intermediate file easier to understand"""

        string = ''
        for element in arr:
            if '.' not in str(element):
                string += str(element).rstrip() 
                if len(str(element)) <= 7:
                    string += '\t'
            else:
                if element == arr[2]:
                    return ""

        string += '\n'

        return string
