def extracted(line):
	print(line)
	line = line.lstrip().rstrip()
	

	if "Private Collection" in line:
		return None


	if ";" in line:
		line = line.split(";")[-1]
		print(line)

		if ":" in line:
			line = line.split(":")[-1]
			print(line)



	elif ":" in line:
			line = line.split(":")[-1]
			print(line)

	elif ", " in line:
		line = "".join(line.split(",")[-1:])


	if line.endswith("."):
		line = line[:-1]

	

	line = line.lstrip().rstrip()

	
	if line.count(',') > 1:
		extracted(line)

	return line



with open('spreadsheets/variantsCollections.txt') as f:
	for l in f.readlines():
		print(extracted(l))
		print('----------')