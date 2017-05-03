import re
import sys
sys.path.append('Extractor')
import Stream

stream = Stream.Stream('spreadsheets/02122015_revisors.xlsx', 'Page')

#contribs = {(v["RevisorID"], v["RevisorName"] )for k, v in stream.stream()}

#for i, n in sorted(contribs, key=lambda x: x[0]):
	#print(i, "|", n)

contribs = {v["Contributor"]for k, v in stream.stream()}

for a in contribs:
	print(a)