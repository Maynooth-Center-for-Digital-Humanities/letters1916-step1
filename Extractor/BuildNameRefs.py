import re
import sys
from Processor import Processor
import Stream
from fuzzywuzzy import fuzz, process

from EditLogger import EditLogger

editLogger = EditLogger()

class BuildNameRefs(Processor):
	def __init__(self, inputFilePath, outputFilePath, personsFile, personsSheet='persName'):
		self.resolve = self._addPersonRefs
		self.transform = self._addPersonRefs
		self.dict_key = 'Letter'
		self.inputFilePath = inputFilePath
		self.outputFilePath = outputFilePath

		pers = Stream.Stream(personsFile, 'Person Name', sheet=personsSheet)
		self.personsDict = {k: v for k, v in pers.stream()}
		self.choices = [k for k, v in self.personsDict.items()]


		super().__init__()

	@editLogger('Try to normalise sender and recipient names and refs', 'PythonScript')
	def _addPersonRefs(self, row):
		new_row = row
		if 'Creator' in row and row['Creator'] != 'NULL':
			new_row['CreatorRefs'] = self.getPersonsRef(row['Creator'])
		else:
			new_row['CreatorRefs'] =  None
		
		if 'Recipient' in row and row['Recipient'] != 'NULL':
			new_row['RecipientRefs'] = self.getPersonsRef(row['Recipient'])
		else:
			new_row['RecipientRefs'] = None

		print(new_row['CreatorRefs'], new_row['RecipientRefs'])

		return new_row

	def getPersonsRef(self, person):
		match = process.extractOne(person, self.choices)
		if match[1] > 90:
			ref = self.personsDict[match[0]]['Person ID']
			if not ref:
				ref = 'MISSING'

			return {'name': match[0], 'ref': ref, 'matchPercent': match[1] }
		else:
			return None


	



if __name__ == "__main__":

	b = BuildInstitutionRefs('TEST2016-02-18/shelves/ExtractorRPD_ExtractorMLP_FilterComplete_OmekaEditsLogged_TagsCleaned_PageTypesLogged_WrapOpener_FixAddrDateLines_BuildCollectionIdnos.shelve',
		'shelve_files/addedPersons.shelve', 'spreadsheets/person_ID.xlsx')
	b.process()
