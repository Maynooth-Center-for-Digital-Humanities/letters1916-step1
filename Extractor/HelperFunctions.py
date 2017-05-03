import re

def extractTagContents(text,tag):
	try:
		return re.findall(r'(?<=<' + tag + r'>)[\s\S]*(?=</' + tag + r'>)', text)
	except TypeError as e:
		raise e

def wrapOnEmptyElementSplit(text, splitTag, wrapTag, *args, **kwargs):
	text = text.split('<'+splitTag+'/>')
	new_text = []
	for line in text:
		new_line = '<' + wrapTag
		if 'wrapAttributes' in kwargs:
			new_line += ' ' +  kwargs['wrapAttributes'] 
		new_line += '>' + line.strip()
		new_line += '</' + wrapTag + '>'
		new_text.append(new_line)
	return '\n'.join(new_text)


def commentise(text):

	return '<!-- \n' + str(text).replace('--', '~~') + ' \n-->'