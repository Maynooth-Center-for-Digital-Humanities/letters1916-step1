import re
import sys
sys.path.append('Extractor')

import Stream
from fuzzywuzzy import fuzz, process



pers = Stream.Stream('spreadsheets/person_ID.xlsx', 'Person Name', sheet='persName')

personsDict = {k: v for k, v in pers.stream()}
#print(personsDict)

choices = [k for k, v in personsDict.items()]
#(choices)


def getPersonsRef(person):

	match = process.extractOne(person, choices)
	if match[1] > 90:
		return match[0], personsDict[match[0]]['Person ID'], match[1]
	else:
		return match[0], personsDict[match[0]]['Person ID'], match[1], '-----------------!---MISSING---!!'




files = Stream.Stream('Processed2016-02-16/shelves/ExtractorRPD_ExtractorMLP_FilterComplete_OmekaEditsLogged_TagsCleaned_PageTypesLogged_WrapOpener_FixAddrDateLines_BuildCollectionIdnos.shelve', 'Letter')

for k, i in files.stream():

		print(i['Creator'], '---', getPersonsRef(i['Creator']))


