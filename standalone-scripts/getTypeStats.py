import sys
sys.path.append('Extractor')
import Stream

stream = Stream.Stream('shelve_files/pageTypeLogs.shelve', 'Letter')


letter_count = 0
postcard_collection_count = 0
collection_count =0
postcard_count = 0
telegraph_count = 0
telegram_count = 0
greeting_count = 0
card_count = 0
photograph_count = 0
other_count = 0


for k, item in stream.stream():
	if k == '242':
		for i, page in item["Pages"].items():
			print(page["PageType"])
			print(page["Translation"])
			print('\n--------------------\n')

	'''

	if 'letter' in item["Title"].lower():
		letter_count += 1
	elif 'collection' in item["Title"].lower() and 'postcard' in item["Title"].lower():
		postcard_collection_count += 1
	elif 'collection' in item["Title"].lower():
		collection_count += 1

	elif 'postcard'in  item["Title"].lower() :
		postcard_count += 1
	elif 'telegraph'in  item["Title"].lower() :
		telegraph_count += 1
	elif 'telegram'in  item["Title"].lower() :
		telegram_count += 1
	elif 'greeting'in  item["Title"].lower()  or  'christmas' in item["Title"].split()[0].lower():
		greeting_count += 1
	elif 'card'in item["Title"].lower() :
		card_count += 1
	elif 'photo' in item["Title"].split()[0].lower():
		postcard_count += 1
	else:
		print(k, ":",item["Title"])
		other_count += 1


print('\n\n-------------------------------\n')
print('Letter:', letter_count)
print('Postcard collection:', postcard_collection_count)
print('Collection-generic:', collection_count)
print('Postcard:', postcard_count)
print('Telegraph:', telegraph_count)
print('Telegram:', telegram_count)
print('Card:', card_count)
print('Photograph:', photograph_count)
print('Other:', other_count)
'''
