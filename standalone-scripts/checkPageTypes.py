import re
import sys
sys.path.append('Extractor')
import Stream

stream = Stream.Stream('shelve_files/MLP.shelve', 'Letter')

def extractTagContents(text,tag):
	return re.findall(r'(?<=<' + tag + r'>)[\s\S]*(?=</' + tag + r'>)', text)


def looks_like_envelope(text):
	address_contents = extractTagContents(text, 'address')
	#print(address_contents)
	if address_contents:
		print(len(address_contents[0]))
		print(len(text) * 0.8 - 100)

		if len(address_contents[0]) > (len(text) * 0.8 - 100):
			if '<address>' not in address_contents[0]:
				print("ENVELOPE\n")
				print(text)
			else:
				print('NOT ENVELOPE--contains paragraph\n')
				print(text)
		else:
			print('NOT ENVELOPE--not enough address\n')
			print(text)
	else:
		print('NOT ENVELOPE--no address\n')
		print(text)







for k, item in stream.stream():
	if k == '141':
		for i, page in sorted(item["Pages"].items()):
			print('\n---------------------\n')
			looks_like_envelope(page["Translation"])