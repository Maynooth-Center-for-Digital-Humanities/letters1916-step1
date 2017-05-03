from EditLogger import EditLogger
from Processor import Processor
import dateparser

editLogger = EditLogger()

class BuildCollectionIdnos(Processor):
	def __init__(self, inputFilePath, outputFilePath):
		self.resolve = self._addIdnos
		self.transform = self._addIdnos
		self.dict_key = 'Letter'
		self.inputFilePath = inputFilePath
		self.outputFilePath = outputFilePath
		super().__init__()

	@editLogger('Extract collection idnos', 'PythonScript')
	def _addIdnos(self, row):
		print('Extracting IDnos, letter ', row["Letter"])
		new_row = row
		#print(row["DocCollection"])
		new_row["Document_Collection"] = self.extracted(row["DocCollection"])
		new_row["Document_Number"] = self.subextracted(row["DocCollection"])

		#print(new_row["Document_Collection"], new_row["Document_Number"])
		# AND going to add a date function here for no reason #
		try:
			date_parsed = dateparser.parse(row["DATE_created"])
			new_row["DATE_created_as_words"] = date_parsed.strftime('%d %B %Y')[1:] if date_parsed.strftime('%d %B %Y')[0] == '0' else date_parsed.strftime('%d %B %Y')
		except Exception as e:
			pass
			print(e, row["Letter"])

		return new_row

	def extracted(self, line):
		#print(line)
		line = str(line)

		if "Private Collection" in line:
			return "private collection"


		if ";" in line:
			line = line.split(";")[0]
			#print(line)

			if ":" in line:
				line = line.split(":")[0]
				#print(line)



		elif ":" in line:
				line = line.split(":")[0]
				#print(line)

		elif ", " in line:
			#line = "".join(line.split(",")[0:])
			line = line.split(",")[0]


		'''if line.endswith("."):
			line = line[0]'''

		

		line = line.lstrip().rstrip()

		
		'''if line.count(',') > 1:
			extracted(line)'''

		return line

	def subextracted(self, line):
		#print(line)
		#line = line.lstrip().rstrip()
		line = str(line)

		if "Private Collection" in line:
			return "private collection"


		if ";" in line:
			line = line.split(";")[-1]
			#print(line)

			if ":" in line:
				line = line.split(":")[-1]
				#print(line)

		elif ":" in line:
				line = line.split(":")[-1]
				#print(line)

		elif ", " in line:
			line = "".join(line.split(",")[-1:])


		if line.endswith("."):
			line = line[:-1]

		line = line.lstrip().rstrip()

		
		if line.count(',') > 1:
			subextracted(line)

		return line
	
"""

for k, item in sorted(collection):
	collection = item["Document_Collection_Number"]
	letter = str(item["Letter"])
	print(letter+(extracted(item["Document_Collection_Number"])+subextracted(item["Document_Collection_Number"])), file=f)
"""