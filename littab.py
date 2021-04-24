class Littab:
	"""Class representing literal table"""

	def __init__(self):
		"""init table"""

		self.table = {}


	def addLit(self, label, value, length, address):
		"""Add a literal to the table"""

		self.table[label] = [value, length, address]


	def searchLit(self, label):
		"""Search the table for a literal"""

		for name in self.table.keys():
			if name == label:
				return True
		return False


	def assignAddress(self, label, address):
		"""Assign an address to an existing literal."""

		self.table[label][2] = address

