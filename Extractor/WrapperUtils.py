import re	
		

def wrap_element_with_tags(text, elem_to_wrap, wrapping_element):
	regex = r'(<' + elem_to_wrap + r'>[\s\S]*?</' + elem_to_wrap + r'>)'
	pattern = re.compile(regex)
	result = pattern.findall(text)
	text = text
	
	for r in set(result):
		try:
			text = re.sub(r, r'<' + wrapping_element + r'>' + r + r'</' + wrapping_element + '>', text)
			#print(text)
		except:
			pass
	return text

def find_positions_of_matches(text, previous_end=0, pieces=[]):
	try:
		temp_wrapper = 'TEMP'
		re.purge()
		find_temp_segments_regex = re.compile(r'[^(<p>)]<' + temp_wrapper + r'>[\s\S]*?</' + temp_wrapper + r'>[\s\n\t]??')
		re.purge()
		result = find_temp_segments_regex.search(text, previous_end)
		re.purge()
	except Exception as e:
		#print('findpos_error')
		raise e
	try:
		rg = result.group()
		#print(rg)
		rs = result.start()
		ren = result.end()
		pieces.append((rs,ren,rg))
		return find_positions_of_matches(text, previous_end=ren, pieces=pieces)
	except:
		#print(pieces)
		return pieces

def find_contiguous_pieces(pieces, threshold=100):
	try:
		cont_pieces = []
		start_pos = pieces[0][0]
		last_pos = pieces[0][1]
		pieces_count = 1
		for i, piece in enumerate(pieces):
			try:
				if piece[1] + threshold >= pieces[i+1][0]:
					pieces_count += 1
					last_pos = pieces[i+1][1]
				else:
					cont_pieces.append((start_pos, last_pos, pieces_count))
					start_pos = pieces[i+1][0]
					last_pos = pieces[i+1][1]
					pieces_count = 1
			except:
				cont_pieces.append((start_pos, piece[1], pieces_count))
				sorted_cont_pieces = sorted(cont_pieces, key=lambda piece: piece[0])
				#print(sorted_cont_pieces)
				return sorted_cont_pieces
	except IndexError:
		raise



# Bunch of utility processing functions

# Grabs the segment of text from its start and end positions
def get_segment(text, s,e):
	try:
		regex = r'[\s\S]*'
		re.purge()
		pattern = re.compile(regex)
		#print(pattern)
		
		try:
			segment = pattern.search(text,s,e).group()
			
			return segment
		except Exception as e:
			#print('getseg regex err -', e)
			raise e
		
	except Exception as e:
		#print('getseg error', e)
		raise e

# Strips temp tags from some text (looks more complicated than just re.sub, but dunno why...)
# Q. above: A. I think to remove internal TEMPS; Used by fix-opener and fix-closer -wraps()
def strip_internal_temps(text):
	regex = r'</TEMP>(?=[\s\S]*?<\/TEMP\>)'
	text = re.sub(regex, '', text)
	regex = r'<TEMP>'[::-1] + r'(?=[\s\S]*?' + r'<TEMP>'[::-1] + r')'
	text = re.sub(regex,'',text[::-1])[::-1]
	return text

# Do as they say on tin; don't know why they can't be one function though...
def fix_opener_wraps(segment):
	segment = strip_internal_temps(segment)
	return re.sub(r'TEMP', 'opener', segment)

def fix_closer_wraps(segment):
	segment = strip_internal_temps(segment)
	return re.sub(r'TEMP', 'closer', segment)



def wrap_pieces_in_text(text, ordered_cont_pieces):
	text_length = len(text)
	text = text
	#if text:
		#print('wp text in ok')
	try: 
	
		try:
			re.purge()
			opener_segment = get_segment(text, ordered_cont_pieces[0][0], ordered_cont_pieces[0][1])
		except Exception as e:
			#print('wp_openseg error')
			raise e
		try:
			re.purge()
			closer_segment = get_segment(text, ordered_cont_pieces[-1][0], ordered_cont_pieces[-1][1])
		except Exception as e:
			#print('wp_closeg error')
			raise e
		# Maybe some more checking in case there's some shit at the top/bottom? -- i.e. check
		# by length or content?	
		
		try:
			if ordered_cont_pieces[-1][1] > text_length * 0.7 and '<salute>' in closer_segment:
				text = re.sub(closer_segment, fix_closer_wraps(closer_segment), text)
		except Exception as e:
			#print('wp closersub failed')
			raise e

		try:
			text = re.sub(opener_segment, fix_opener_wraps(opener_segment), text)	
		except Exception as e:
			#print('wp openersub failed')
			print(e)
	
		#print('wp_ index error not triggered')
	except IndexError: # presumably from fail if there is only one segment identified
		#print('wp_index error')
		opener_segment = get_segment(text, cont_pieces[0][0], cont_pieces[0][1])
		text = re.sub(opener_segment, fix_opener_wraps(opener_segment), text)
	except Exception as e:

		#print('wp_general exception', e)
		raise e
	# Remove all remaining temps
	text = re.sub(r'<TEMP>','',text)
	text = re.sub(r'</TEMP>','',text)
	#print(text)
	return text