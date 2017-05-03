import re
import sys
from Processor import Processor
import Stream
from fuzzywuzzy import fuzz, process

from EditLogger import EditLogger

editLogger = EditLogger()

class BuildInstitutionRefs(Processor):
	def __init__(self, inputFilePath, outputFilePath, instListFile, instSheet='MAIN', instColumn='NAME'):
		self.resolve = self._addInstitutionRef
		self.transform = self._addInstitutionRef
		self.dict_key = 'Letter'
		self.inputFilePath = inputFilePath
		self.outputFilePath = outputFilePath

		ins = Stream.Stream(instListFile, instColumn, sheet=instSheet)
		self.institutionsDict = {k: v for k, v in ins.stream()}
		self.choices = [k for k, v in self.institutionsDict.items()]


		super().__init__()

	def _getInstitutionRef(self, inst):
		inst = inst.lower().replace('family', '')
			#match = process.extractOne(inst, choices)
		match = process.extractOne(inst, self.choices)
		if match[1] > 90:
			return {'name': match[0], 'ref': self.institutionsDict[match[0]]['REF'], 'matchPercent': match[1]}
		else:
			return {'name': 'MISSING', 'ref': 'MISSING', 'matchPercent': match[1]}

	@editLogger('Try to normalise institution refs', 'PythonScript')
	def _addInstitutionRef(self, row):
		new_row = row
		if 'Source' in new_row:
			new_row['InstitutionRefs'] = self._getInstitutionRef(row['Source'])
		#print(new_row['InstitutionRefs'])
		return new_row



if __name__ == "__main__":

	b = BuildInstitutionRefs('TEST2016-02-16/shelves/ExtractorRPD_ExtractorMLP_FilterComplete_OmekaEditsLogged_TagsCleaned_PageTypesLogged_WrapOpener_FixAddrDateLines_BuildCollectionIdnos.shelve',
		'shelve_files/addedInst.shelve', 'spreadsheets/institution_ID.xlsx')
	b.process()
