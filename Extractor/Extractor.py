import argparse
from datetime import datetime
import os
import sys

from Processor import Processor as Processor
from EditLogger import EditLogger
from HelperFunctions import commentise

editLogger = EditLogger()



class RemovePageDuplicates(Processor):
	def __init__(self, inputFilePath, outputFilePath):
		self.resolve = self.pageDuplicatesResolve
		self.transform = self.pageDuplicatesTransform
		self.dict_key = 'Page'
		self.inputFilePath = inputFilePath
		self.outputFilePath = outputFilePath
		super().__init__()

	#@editLogger('Old page dublicate removed', 'PythonScript_pageDublicatesResolve')
	def pageDuplicatesResolve(self, old, new):
		print('Extracting from Spreadsheet, logging duplicate, page: ', old["Page"], " Letter: ", old["Letter"])
		if old['Translation_Timestamp'] >= new['Translation_Timestamp']:
			#print('old')
			letter = old
			letter["Contributor_List"] + [new["Contributor"], new["revID"]]
			letter["Contributor_List"] = list(set(letter["Contributor_List"]))
			#print(letter["Contributor_List"])
			edit_per = {'datetime': str(new["Translation_Timestamp"]).replace(" ","T"), 
					'Omeka_RevisionPageNo': new["Page"], 
					"Omeka_Translation": commentise(new["Translation"]),  
					'editType': 'Revision in Omeka', 
					'editor': new["revID"] 
				}
			edit_py = {
					'Duplicate_pageTimestamp': str(new["Translation_Timestamp"]).replace(" ","T"),
					'Duplicate_pageNo': new["Page"],   
					'editType': 'Old page duplicate removed', 
					'editor': "PythonScript", 
					'datetime': str(datetime.now())[:-7].replace(" ", "T")}
			letter["Edits"].append(edit_per)
			letter["Edits"].append(edit_py)
			#print(letter["Edits"], len(letter['Edits']))

		elif new['Translation_Timestamp'] >= old['Translation_Timestamp']:
			#print('new')
			letter = new
			letter["Contributor_List"] = list(set(old["Contributor_List"] + [new["Contributor"], new["revID"]]))
			#print(letter["Contributor_List"])
			edit_per = {'datetime': str(old["Translation_Timestamp"]).replace(" ","T"), 
					'Omeka_RevisionPageNo': old["Page"], 
					"Omeka_Translation": commentise(old["Translation"]),  
					'editType': 'Revision in Omeka', 
					'editor': old["revID"] 
				}
			edit_py = {
					'Duplicate_pageTimestamp': str(old["Translation_Timestamp"]).replace(" ","T"),
					'Duplicate_pageNo': old["Page"],   
					'editType': 'Old page duplicate removed', 
					'editor': "PythonScript", 
					'datetime': str(datetime.now())[:-7].replace(" ", "T")}
			letter["Edits"] = old["Edits"] + [edit_per, edit_py]
			#print(letter["Edits"], len(letter['Edits']))
		return letter

	#@editLogger('New page instance created', 'PythonScript')
	def pageDuplicatesTransform(self, field):
		print('Extracting from spreadsheet, new, page: ', field["Page"], " Letter: ", field["Letter"])
		field["Contributor_List"] = [field["Contributor"], field["revID"]]
		#print(field["Contributor_List"])
		edit_py = {
					'New_pageTimestamp': str(field["Translation_Timestamp"]).replace(" ","T"),
					'New_pageNo': field["Page"],   
					'editType': 'New page instance created', 
					'editor': "PythonScript", 
					'datetime': str(datetime.now())[:-7].replace(" ", "T")}
		edit_init =  {  
					'editType': 'Object initialised', 
					'editor': field["Contributor"], 
					'datetime': str(field["Translation_Timestamp"]).replace(" ","T")}
		field["Edits"] = [edit_py, edit_init]
		#print(field["Edits"], len(field['Edits']))
		return field




class MergeLetterPages(Processor):
	def __init__(self, inputFilePath, outputFilePath):
		self.resolve = self.mergeLetterPagesResolve
		self.transform = self.mergeLetterPagesTransform
		self.dict_key = 'Letter'
		self.inputFilePath = inputFilePath
		self.outputFilePath = outputFilePath
		super().__init__()


	#@editLogger('Additional page merged into Letter', 'PythonScript')
	def mergeLetterPagesResolve(self, old, new):
		print('Merging pages, page: ', new["Page"], " Letter: ", new["Letter"])
		letter = old
		letter['Pages'][new['Page']] = self._mergeLetterBuildPageDict(new)
		letter["Contributor_List"] = list(set(old["Contributor_List"] + new["Contributor_List"]))
		letter["Edits"] = old["Edits"] + new["Edits"]

		edit_py = edit_py = {
					'Merged_pageTimestamp': str(new["Translation_Timestamp"]).replace(" ","T"),
					'Merged_pageNo': new["Page"],   
					'editType': 'Additional page added to letter', 
					'editor': "PythonScript", 
					'datetime': str(datetime.now())[:-7].replace(" ", "T")}
		letter["Edits"].append(edit_py)
		return letter

	#@editLogger('New Letter created', 'PythonScript_mergeLetterPagesTransform')
	def mergeLetterPagesTransform(self, field):
		print('Merging pages, page: ', field["Page"], " Letter: ", field["Letter"])
		letter = field
		letter['Pages'] = {field['Page']: self._mergeLetterBuildPageDict(field)}
		
		edit_py = edit_py = {
					'Initial_pageTimestamp': str(field["Translation_Timestamp"]).replace(" ","T"),
					'Initial_pageNo': field["Page"],   
					'editType': 'New letter objected created', 
					'editor': "PythonScript", 
					'datetime': str(datetime.now())[:-7].replace(" ", "T")}
		letter["Edits"].append(edit_py)
		return self._mergeLetterDeleteFields(letter)

	def _mergeLetterBuildPageDict(self,field):
		return {"Translation": field['Translation'], 
				#"Original_Filename": field['Original_Filename'], 
				"Archive_Filename": field['Archive_Filename']}

	def _mergeLetterDeleteFields(self,letter):
		for key in ["Translation", "Page", "Archive_Filename"]:
			del letter[key]
		return letter







if __name__ == "__main__":

	message = """
	This script has two functions:
	RPD = Extracting Excel data to a Python object while removing page duplicates
	MLP = Merging pages into a dict object beloning to a single Letter object

	This script may be called directly with command-line arguments,
	or instances of RemovePageDuplicates and MergeLetterPages may
	be used in a script.

	View --help for more info on running from
	the command line.
	"""

	parser = argparse.ArgumentParser(description=message)
	parser.add_argument('--inputFilePath', '-i', help="Specify the path of an input file.")
	parser.add_argument('--outputFilePath', '-o', help="Specify the path to output file")
	parser.add_argument('--process', '-p', help="Specify a process (RPD or MLP).")


	inputFilePath = parser.parse_args().inputFilePath
	outputFilePath = parser.parse_args().outputFilePath
	process = parser.parse_args().process
	
	if not inputFilePath or not outputFilePath:
		raise ValueError('An input file [-i] and output file path [-o] must be specified.')


	if not process or (process != 'RPD' and process != 'MLP'):
		raise ValueError('A process [-p] (either RPD or MLP) must be specified')

	if process == 'RPD':
		r = RemovePageDuplicates(inputFilePath, outputFilePath)
		r.process()
		print("Data has been extracted to the shelf file '%s'" % outputFilePath)
	elif process == 'MLP':
		m = MergeLetterPages(inputFilePath, outputFilePath)
		m.process()
		print("Data has been extracted to the shelf file '%s'" % outputFilePath)

