from collections import Counter
import statistics

import sys
sys.path.append('Extractor')
import Stream


count = 0
stream = Stream.Stream('shelve_files/testALL_tagsCleaned.shelve', 'Letter')




fix_counts = [letter["Edits"][-1]['clean_count'] for k, letter in stream.stream() if 'clean_count' in letter["Edits"][-1]]

data = Counter(fix_counts)

for k, v in data.most_common():
	if k in [0, 1]:
		print (k, "...", v)
	else:
		print(k, "|"*v, v)


print('\n', 'Total errors fixed:', sum(fix_counts))

print('\n', 'Mean errors per letter:', statistics.mean(fix_counts))
print('\n', 'Letters with at least 1 error:', len([v for v in fix_counts if v > 0]))
print(" % letters with min 1 error:", len([v for v in fix_counts if v > 0]) / len(fix_counts) * 100)
print('\n', 'Total letters:', len(fix_counts))
