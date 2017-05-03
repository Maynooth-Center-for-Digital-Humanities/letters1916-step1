import datetime
import re

from Processor import Processor as Processor
from EditLogger import EditLogger


editLogger = EditLogger()

class FixTags(Processor):
	def __init__(self, inputFilePath, outputFilePath):
		self.resolve = self._clean_tags
		self.transform = self._clean_tags
		self.dict_key = 'Letter'
		self.inputFilePath = inputFilePath
		self.outputFilePath = outputFilePath
		super().__init__()

	#@editLogger('Clean tags', 'PythonScript_CleanersFixAmpersands')
	def _clean_tags(self, row):
		print('Cleaning tags, Letter ', row["Letter"])
		new_row = row
		reg = r'&(?!\S+[^;])'
		mod = '&amp;'

		for key, page in row["Pages"].items():
			if page["Translation"] is not None:
				re.purge()
				modified_page = page["Translation"].replace('&#x2014;', '§§§§')
				modified_page =  re.sub(reg, mod, modified_page)
				modified_page = modified_page.replace('§§§§', '&#x2014;')
				#new_row["Pages"][key]["Translation"] = modified_page

			
				cleaned = self._tag_cleaner(modified_page)
				new_row["Pages"][key]["Translation"] = cleaned[1]
				
				edit = {'page_cleaned': key, 'clean_count': cleaned[0], 'editType': 'Clean Tags', 'editor': "PythonScript", 'datetime': str(datetime.datetime.now())[:-7].replace(" ", "T")}
				new_row["Edits"].append(edit)

		return new_row

	def _tag_cleaner(self, text):
		tags_fixed = 0

		tags_fixed += len(re.findall(r'&(?!\S+[^;][&])', text))
		#text = re.sub(r'&(?!\S+[^;][&])', '&amp;', text)
		
		tags_fixed += len(re.findall(r'<<', text))
		text = re.sub(r'<<', '<', text)
		
		tags_fixed += len(re.findall(r'>>', text))
		text = re.sub(r'>>', '>', text)
		
		tags_fixed += len(re.findall(r'\<\s+\>', text))
		text = re.sub(r'\<\s+\>', "", text)
		
		tags_fixed += len(re.findall(r'\<\s+', text))
		text = re.sub(r'\<\s+', "<", text)
		
		tags_fixed += len(re.findall(r'\s+\>', text))
		text = re.sub(r'\s+\>', ">", text)
		

		for empttag in ["lb", "pb", "gap"]:
			for sub in [r'\<\/' + empttag + r'\>', 
						r'\<\/' + empttag + r'(?!\>)',
						r'(?<!\<)\/' + empttag + r'\>?',
						r'\<' + empttag + r'\/(?!\>)',
						r'\<' + empttag + r'\>']:
				tags_fixed += len(re.findall(sub, text))
				text = re.sub(sub, "<" + empttag + "/>", text)

		text = re.sub(r'\<pb\/\>', "<zz/>", text)
		text = re.sub(r'\<gap\/\>', "<gg/>", text)

		text = re.sub(r'hi rend="underline"', "qqq", text)
		text = re.sub(r'hi rend="superscript"', "yyy", text)


		tags = ["address", "date", "salute", "del", "note", "sic",  "foreign", "p", "unclear", "add", 'qqq', 'yyy',  "hi"]


		for tag in tags:
			split = [ch for ch in re.split( r'(?<=\<)(' + tag + r')|(?<=\/)(' + tag + r')|(' + tag + r')(?=\/{0,1}\>)', text) if ch is not None]
			split = [ch for ch in split if ch != tag]


			new_list = []

			for i, chunk in enumerate(split):
				if len(split) == 1:
					new_list.append(chunk)

				# First chunk
				elif i == 0:
					new_chunk = chunk
					if not chunk.endswith("<"):
						if not chunk.endswith("</"):
							new_chunk = chunk + "<"
							tags_fixed+=1
					new_list.append(new_chunk)

				# Last chunk
				elif i == len(split)-1:
					new_chunk = chunk
					if not (chunk.startswith(">")):
						if chunk.startswith("/"):
							new_chunk = chunk[1:]
							new_list[i-1] = new_list[i-1] + "/"
							tags_fixed+=1
						else:
							new_chunk = ">" + new_chunk
							tags_fixed+=1

					new_list.append(new_chunk)

				else:
					new_chunk = chunk
					if not (chunk.endswith("</") or chunk.endswith("<")):
						if chunk.endswith("/"):
							new_chunk = chunk[:-1] + "</"
							tags_fixed+=1
						else:
							new_chunk += "<"
							tags_fixed+=1
					if not chunk.startswith(">"):
						if chunk.startswith("/"):
							new_chunk = chunk[1:]
							new_list[i-1] = new_list[i-1] + "/"
							tags_fixed+=1
						else:
							new_chunk = ">" + new_chunk
							tags_fixed+=1

					new_list.append(new_chunk)

			#THIS ALSO NEEDS TO BE DONE WITH > FOR FIRST!
			if new_list[-1].endswith("<") or new_list[-1].endswith("/"):
				new_list.append(">")		
			
			
			text = tag.join(new_list)

			if tag == "address":
				text = re.sub(r'\<address\>', '<xx>', text)
				text = re.sub(r'\<\/address\>', '</xx>', text)


		text = re.sub(r'\<xx\>', '<address>', text)
		text = re.sub(r'\<\/xx\>', '</address>', text)
			
		text = re.sub(r'\<zz\/\>', "<pb/>", text)
		text = re.sub(r'\<gg\/\>', "<gap/>", text)
		text = re.sub(r'\<qqq\>', '<hi rend="underline">', text)
		text = re.sub(r'\<yyy\>', '<hi rend="superscript">', text)

		return (tags_fixed, text)

		#END of fugly cleaner function

if __name__ == '__main__':
	fix_tags = FixTags('shelve_files/editsLogged.shelve','shelve_files/tagsCleaned.shelve')
	fix_tags.process()
