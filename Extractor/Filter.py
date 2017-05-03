import argparse
import dateparser
import datetime
import os
import shelve
import sys

from Processor import Filter
from Stream import Stream		

### Filterlist should inherit from list type --- self=values...
class FilterList:
	def __init__(self):
		pass

	def __call__(self):
		return self.values

	def __iter__(self):
		return iter(self.values)

	def __len__(self):
		return len(self.values)


class ListFromDirectory(FilterList):
	def __init__(self,path):
		if os.path.isdir(path):
			self.path = path
			self.values = self.getValuesFromDirFiles()
			super().__init__()
		else:
			raise TypeError("'%s' is not a directory" % path)

	def getValuesFromDirFiles(self):
		return [str(f[:-4]) + ".0" for f in os.listdir(self.path) if f.endswith('.xml')]


class ListFromExcel(FilterList):
	def __init__(self,filePath, column, date=None):
		if os.path.isfile(filePath) and filePath.endswith('xlsx'):
			self.filePath = filePath
			self.column = column
			try:
				self.date = dateparser.parse(date) 
			except AttributeError:
				#print('attrerror')
				self.date = datetime.datetime.now()
			self.values = list(self.getValuesFromFile())
			super().__init__()
		else:
 			raise TypeError("'%s' is not an Excel file" % filePath)

	def getValuesFromFile(self):
 		stream = Stream(self.filePath, self.column, sheet="ID")
 		
 		for k, v in stream.stream():
 			
 			#print(k)

 			if k != 'None' and v["DATE"] < self.date:
	 			yield str(k) + '.0'


class ListFromURL(FilterList):
	def __init__(self, url):
		self.url = url
		self.values = self.getValuesFromURL()
		super().__init__()

	def getValuesFromURL(self):
		import re
		import urllib.request
		import json


		#########GOT TO FIX THIS!!!
		r = urllib.request.urlopen(self.url)
		leted = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
		urlList = [f.strip('href="').strip('.xml"')+'.0' for f in leted]
		#print(urlList)
		if len(urlList) != 0:
			return urlList
		else:
			pass


if __name__ == "__main__":



	message = """
	This script allows the filtering of a shelve files by passing an additional list of numbers.

	View --help for more info on running from
	the command line.
	"""

	parser = argparse.ArgumentParser(description=message)
	parser.add_argument('--inputFilePath', '-i', help="Specify the path of an input file.")
	parser.add_argument('--outputFilePath', '-o', help="Specify the path to output file")
	parser.add_argument('--inclusionFilePath', '-f', help="Specify a file to use as includsion list")
	parser.add_argument('--inclusionColumnHeader', '-k', help="Specify the column header of column containing file ID")
	parser.add_argument('--cutoffDate', '-c', help="Specify a date of extracted data limit filtering")
	parser.add_argument('--exclusionDirectory', '-e', help="Specify a directory of previously-generated XML files to exclude")

	inputFilePath = parser.parse_args().inputFilePath
	outputFilePath = parser.parse_args().outputFilePath
	inclusionFilePath = parser.parse_args().inclusionFilePath
	inclusionColumnHeader = parser.parse_args().inclusionColumnHeader
	cutoffDate = parser.parse_args().cutoffDate
	exclusionDirectory = parser.parse_args().exclusionDirectory

	if not (inputFilePath and outputFilePath and inclusionFilePath and inclusionColumnHeader):
		raise ValueError('You are missing an argument. Run with --help for more information.')

	if cutoffDate:
		incList = ListFromExcel(inclusionFilePath, inclusionColumnHeader, date=cutoffDate)
	else:
		incList = ListFromExcel(inclusionFilePath, inclusionColumnHeader)
	
	f = Filter(inputFilePath, outputFilePath)
	f.inclusionListAdd(incList)


	if exclusionDirectory:
		exList = ListFromDirectory('xmlfiles')
		f.exclusionListAdd(exList)

	f.filter()

	print("Data has been extracted to the shelf file '%s'" % outputFilePath)
