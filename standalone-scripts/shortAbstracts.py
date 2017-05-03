import sys
sys.path.append('Extractor')
import Stream

stream = Stream.Stream('shelve_files/MLP.shelve', 'Letter')
def is_short(desc):
	if desc is None or len(desc) < 200:
		return True
	return False


short = sorted([int(k) for k, l in stream.stream() if is_short(l["Description"]) ])

filtered = [int(k) for k, l in Stream.Stream('shelve_files/filtered.shelve', 'Letter').stream()]



for i in short:
	string = str(i)
	if i in filtered:
		string += " *"
	print(string)