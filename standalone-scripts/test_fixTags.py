import re

text = """
some text <pb/ <lb/ <p  <p/>some text
"""

def clean_tags(text):
	tags_fixed = 0

	tags_fixed += len(re.findall(r'&(?!\S+[^;][&])', text))
	text = re.sub(r'&(?!\S+[^;][&])', '&amp;', text)
	
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




	#fix hi rends... (so don't clash with hi)
	tags = ["address", "date", "salute", "del", "note", "sic",  "foreign", "p", "unclear", "add", 'qqq', 'yyy',  "hi"]

	#split = text.split(tag)
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



print(clean_tags(text)[1])
print(clean_tags(text)[0])


