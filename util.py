class Util:
	"""Class to handle small utility functions"""

	def _getConstLength(self, const):
	    """Returns the length in bytes of an integer or hex constant"""

	    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

	    length = 0
	    if const[0] == 'C':
	        for char in const[2:]:
	            if char in letters:
	                length += 1
	        return length
	            
	    elif const[0] == 'X':
	        for char in const[2:-1]:
	            if char != "'":
	                length += 1
	        return int(length/2)                   
	        return length



	def _isSymbol(self, operand):
	    """Returns true if operand is a symbol, returns false otherwise"""

	    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

	    if operand[0] == '=':
	    	return False

	    for char in operand:
	        if char in letters:
	            return True

	    return False

