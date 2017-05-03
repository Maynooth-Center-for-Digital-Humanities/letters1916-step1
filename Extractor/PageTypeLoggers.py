import argparse

from Processor import Processor as Processor
from EditLogger import EditLogger
from HelperFunctions import extractTagContents

editLogger = EditLogger()

class PageTypeLogger(Processor):

	def __init__(self, inputFilePath, outputFilePath):
		self.resolve = self._log_types
		self.transform = self._log_types
		self.dict_key = 'Letter'
		self.inputFilePath = inputFilePath
		self.outputFilePath = outputFilePath
		super().__init__()

	@editLogger('Page types determined', 'PythonScript')
	def _log_types(self, row):
		new_row = row

		new_row["Type"] = self._get_corresp_type(row)

		if new_row["Type"] == 'Letter':
			for k, page in row["Pages"].items():
				new_row["Pages"][k]["PageType"] = self._get_letter_page_type(page["Translation"])[0]
		
		if new_row["Type"] == 'Postcard':
			new_row = self._get_postcard_type_and_page_types(new_row)

		return new_row


	def _get_corresp_type(self, row):
		title = row["Title"].lower()
		if 'letter' in title:
			return 'Letter'
		elif 'collection' in title and 'postcard' in title:
			return 'PostcardCollection'
		elif 'collection' in title:
			return 'Collection'
		elif 'postcard 'in title:
			return 'Postcard'
		elif 'telegraph'in  title or 'telegram' in title :
			return 'Telegram'
		elif 'card'in title:
			return 'Card'
		elif 'photo' in title:
			return 'Photograph'
		else:
			return 'Unknown'



	def _get_letter_page_type(self, text):
		"""
		This function returns a tuple!!!
		"""

		# Throws an error for pages with no text -- assumes ImageType
		try:
			address_contents = extractTagContents(text, 'address')
		except:
			return ('ImageType', 'debug--address pc less than threshold')	
		

		# Now try to find whether it's an address
		if address_contents:
			#print(address_contents)
			#print(text)
			#print('addrlength:', len(address_contents[0]))
			#print('thresh:', len(text) * 0.6)

			if len(address_contents[0]) > (len(text) * 0.8 - 100):
				if '<address>' not in address_contents[0]:
					return ('EnvelopeType', 'debug--envelope found')
				else:
					return ('PageType', 'debug--contains another address from greedy regex')

			else:
				return ('PageType', 'debug--address pc less than threshold')	
		else:
			return ('PageType', 'debug--no address found')

	def _get_postcard_type_and_page_types(self, row):
		new_row = row
		page_types = []
		for k, page in row["Pages"].items():
			if self._get_letter_page_type(page["Translation"])[0] == 'EnvelopeType':
				new_row["Pages"][k]['PageType'] = 'AddressSide'
				page_types.append('AddressSide')
			elif '<salute>' in page["Translation"] or '<date>' in page["Translation"]:
				new_row["Pages"][k]['PageType'] = 'TextSide'
				page_types.append('TextSide')
			elif page["Translation"] is not None:
				new_row["Pages"][k]['PageType'] = 'ImageCaptionSide'
				page_types.append('ImageCaptionSide')
			else:
				new_row["Pages"][k]['PageType'] = 'ImageSide'
				page_types.append('ImageSide')

		if 'AddressSide' in page_types:
			new_row["Type"] = 'PostcardAM' # Type 1 -- Address and message
		else:
			new_row["Type"] = 'PostcardIM' # Type 2 -- Image and address/message

		return new_row


if __name__ == '__main__':
	message = """

		Tries to differentiate between page types and envelopes;
		logs result in Letter["Pages"][id]["Type"]
	"""

	parser = argparse.ArgumentParser(description=message)
	parser.add_argument('--inputFilePath', '-i', help="Specify the path of an input file.")
	parser.add_argument('--outputFilePath', '-o', help="Specify the path to output file")


	inputFilePath = parser.parse_args().inputFilePath
	outputFilePath = parser.parse_args().outputFilePath
	
	if not inputFilePath or not outputFilePath:
		raise ValueError('An input file [-i] and output file path [-o] must be specified.')

	logger = PageTypeLogger(inputFilePath, outputFilePath)
	logger.process()