import sys
sys.path.append('Extractor')
import Stream

f = open("collection_id.txt", "w")
print ("Collections and ID", file=f)

stream = Stream.Stream('shelve_files/letterPagesMerged.shelve', 'Letter', 'Translations')


def extracted(line):
	print(line)
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

	return "* collection: "+line

def subextracted(line):
	print(line)
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

	return " * ID= "+line
	
collection = stream.stream()

for k, item in sorted(collection):
	collection = item["Document_Collection_Number"]
	letter = str(item["Letter"])
	print(letter+(extracted(item["Document_Collection_Number"])+subextracted(item["Document_Collection_Number"])), file=f)
