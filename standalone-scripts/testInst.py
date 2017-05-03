import re
import sys
sys.path.append('Extractor')

import Stream
from fuzzywuzzy import fuzz, process



ins = Stream.Stream('spreadsheets/institution_ID.xlsx', 'NAME', sheet='Foglio1')

institutionsDict = {k: v for k, v in ins.stream()}
choices = [k for k, v in institutionsDict.items()]




def getInstitutionRef(inst):
	inst = inst.lower().replace('family', '')
		#match = process.extractOne(inst, choices)
	match = process.extractOne(inst, choices)
	if match[1] > 90:
		return match[0], institutionsDict[match[0]]['REF'], match[1]
	else:
		return match[0], institutionsDict[match[0]]['REF'], match[1], '!---MISSING---!!'




files = Stream.Stream('Processed2016-02-16/shelves/ExtractorRPD_ExtractorMLP_FilterComplete_OmekaEditsLogged_TagsCleaned_PageTypesLogged_WrapOpener_FixAddrDateLines_BuildCollectionIdnos.shelve', 'Letter')

for k, i in files.stream():

		print(i['Source'], '---', getInstitutionRef(i['Source']))


