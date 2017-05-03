import os
import shelve
import sys

from Stream import Stream
from EditLogger import EditLogger

editLogger = EditLogger()

class Filter:
	def __init__(self, inputFilePath, outputFilePath):
		self.inclusionList = []
		self.exclusionList = []
		self.stream = Stream(inputFilePath, 'Letter')
		self.new_shelve_file = outputFilePath

	def inclusionListAdd(self, filterList):
		self.inclusionList += filterList()

	def exclusionListAdd(self, filterList):
		self.exclusionList += filterList()


	def filter(self):

		print(len(self.inclusionList))
		with ShelveManager(self.new_shelve_file) as new_shelf:
			for index, fields in self.stream.stream():
				#print(str(index)+'.0', str(index)+'.0' in self.inclusionList)
				if str(index)+'.0'  in self.inclusionList and str(index)+'.0' not in self.exclusionList:
					print('Filtering letter, included ,', index)
					new_shelf[index] = self._get_fields(fields)
				else:
					print('Filtering letter, removed ,', index)

	@editLogger('Filtered from Completed List', 'PythonScript')
	def _get_fields(self, fields):
		return fields

class Processor:
	def __init__(self): # f, outputFilePath):
		self.stream = Stream(self.inputFilePath, self.dict_key)
		self.new_shelf_file = self.outputFilePath


	def process(self):
		with ShelveManager(self.new_shelf_file) as new_shelf:
			for index, fields in self.stream.stream():

				if index in new_shelf:

					#print('index in new shelf')
					### Some sort of check whether self.resolve.. returns anything, otherwise don't set the index?

					new_shelf[index] = self.resolve(new_shelf[index], fields)
				else:
				
					#print('index not in new shelf')
					new_shelf[index] = self.transform(fields)
				
					#print(index, new_shelf[index])
		
		
class ShelveManager:
	def __init__(self, shelfFile, auto=False):
		self.shelfFile = shelfFile
		

	def __enter__(self):
		self.manageFile()
		
		# Set and return shelf object
		self.shelf = shelve.open(self.shelfFile)
		return self.shelf

	def __exit__(self, type, value, traceback):
		self.shelf.close()
	
	def manageFile(self):
		if os.path.isfile(self.shelfFile):
			if input("\nDo you wish to overwrite data file '%s'? (y/n): " % self.shelfFile) == 'y':
				os.remove(self.shelfFile)
				print('\nFile overwriting')
			else:
				sys.exit('\nProcess stopped to prevent data file overwrite')


if __name__ == '__main__':
	print("\nThis file contains class definitions for processing which must be implemented. \
		\nThere is no option to call this script from the command line.")