
from EditLogger import EditLogger
from Processor import Processor as Processor
import WrapperUtils as WU

editLogger = EditLogger()


class WrapOpenerAndCloser(Processor):
	def __init__(self, inputFilePath, outputFilePath):
		self.resolve = self.wrap_opener_and_closer
		self.transform = self.wrap_opener_and_closer
		self.dict_key = 'Letter'
		self.inputFilePath = inputFilePath
		self.outputFilePath = outputFilePath
		
		super().__init__()


	@editLogger('Opener and closer wrapped', 'PythonScript')
	def wrap_opener_and_closer(self, row):
		print("Wrapping opener and closer ", row["Letter"])
		new_row = row
		
		
		#l_list = [1038,1039,1040]
		if row["Type"] == 'Letter':
			#print('--------')
			#print(row["Letter"], row["Type"])
			text = self._merged_pages(row['Pages'])
			text = self._wrap_opener_and_closer_process(text)
			split = self._split_pages(text)
			new_row["Pages"] = self._build_new_page_row(row['Pages'], split)
		# Implicitly, else do nothing	
		
		return new_row
		

	def _merged_pages(self, pages):
		def page_ok_to_include(k, v):
			#print(k, v["PageType"] )
			if v["Translation"] and v["PageType"] =='PageType':
				return True
			else:
				return False

		text = "\n\n" + "§§\n".join([str(v["Translation"]) for k, v in sorted(pages.items()) if page_ok_to_include(k, v)])
		return(text)
			
	def _split_pages(self, pages_text):
		split = pages_text.split('§§\n')
		#print(len(split))
		return split

	def _build_new_page_row(self, pages, split):
		new_page_dict = pages
		for page_text, page_d in zip(split, sorted(pages.items())):
			new_page_dict[page_d[0]]["Translation"] = page_text
		return new_page_dict




	def _wrap_opener_and_closer_process(self, text):
		#print(text)
		
		
		# List of tags to consider
		tags_in_opener_and_closer =  ['salute', 'dateline', 'date', 'address', 'signed']
		letter_text = text
		for tag in tags_in_opener_and_closer:
			#print(tag)
			letter_text = WU.wrap_element_with_tags(letter_text, tag, 'TEMP')
		pieces = []
		pieces = WU.find_positions_of_matches(letter_text, pieces=[])
		#if pieces:
			#print('Pieces ok')
		try:
			contiguous_pieces = WU.find_contiguous_pieces(pieces)
			#if contiguous_pieces:
				#print('cont_pieces ok')
			opener_closer_fixed_text = WU.wrap_pieces_in_text(letter_text, contiguous_pieces)
			#print('SUCCESS')
			#print(opener_closer_fixed_text)
			return opener_closer_fixed_text
		except Exception as e:
			#Maybe raise error and log higher up??)
			#print('FAIL', e)
			return text		




if __name__ == '__main__':
	w = WrapOpenerAndCloser('shelve_files/ExtractorRPD_ExtractorMLP_FilterComplete_OmekaEditsLogged_TagsCleaned_PageTypesLogged.shelve', 'shelve_files/WrapOpenerAndCloser.shelve')
	w.process()