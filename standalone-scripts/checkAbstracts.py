import sys
sys.path.append('Extractor')
import Stream

s = Stream.Stream('spreadsheets/14122015_revisors.xlsx', 'Page')
max = 0
for k, v in s.stream():
	if len(v["Description"]) > max:
		max = len(v["Description"])
		print(max)
print(max)