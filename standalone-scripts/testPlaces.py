import re
import sys
sys.path.append('Extractor')

import Stream
from fuzzywuzzy import fuzz, process



places = Stream.Stream('spreadsheets/placeList_ID.xlsx', 'Place', sheet='new')



# Builds a dict for reversing the lookup process
def assemblePlaceTuple(v):
	return tuple(v[x] for x in ['Place', 'County', 'Country'] if v[x] is not None)
placesLookupDict =  {assemblePlaceTuple(v): v for _, v in places.stream()}

def placesLookup(result):
	try:
		res = tuple(reversed(result))
		return placesLookupDict[res]
	except KeyError:
		return None


placeChoices = list(set([k[0] for k, _ in placesLookupDict.items() if k]))
countyChoices = list(set([k[1] for k, _ in placesLookupDict.items() if len(k)>1]))
countryChoices = list(set([k[2] for k, _ in placesLookupDict.items() if len(k)>2]))


placesDict = {}

for country in countryChoices:
	placesDict[country] = {}

	for k, v in placesLookupDict.items():
		if len(k) > 2 and k[2] == country:
			placesDict[country][k[1]] = []
			for l, m in placesLookupDict.items():
				if len(l) > 2 and l[1] == k[1]:
					placesDict[country][k[1]].append(l[0])

#print(placesDict)




def getChoices(level, identifier=None):
	#print('identifier:', identifier)
	if level == 'country':
		return countryChoices
	if level == 'county':
		return [k for k, v in placesDict[identifier].items()]
	if level == 'place':
		return placesDict[identifier[0]][identifier[1]]


def normalise(place):
	
	replace = {'England': 'United Kingdom', 'UK': 'United Kingdom'}
	
	if place in replace:
		return replace[place]
	else:
		return place

def doMatch(place, choices, t=70):
	#print(place, choices)
	match = process.extractOne(place, choices)
	#print(place, 'match', match)
	if match[1] > t:
		#print(place, match[0])
		return match[0]
	else:
		return False


def lookupParent(place):
	for k, v in placesDict.items():
		if place in v.keys():
			return k

def lookupCountyFromPlace(place):
	for k, v in placesDict.items():
		for l, m in v:
			if place in m.keys():
				return l

def getPlaceRef(place):
	try:
		if place == 'NULL':
			#print('it is null')
			return None

		placeList =  [p.strip() for p in place.split(',')]
		
		result = []

		matchCountry = doMatch(normalise(placeList[-1]), getChoices('country'), t=80)
		# Is country
		if matchCountry:
			#print('a. country matched--')
			#print('matchCountry', matchCountry)
			try:
				result.append(matchCountry)
				matchCounty = doMatch(placeList[-2], getChoices('county', matchCountry))
				if matchCounty:
					#print('b.if.. matchCounty')
					#print('matchCounty', matchCounty)
					result.append(matchCounty)
					matchPlace = doMatch(" ".join(placeList[:-2]), getChoices('place', (matchCountry, matchCounty)), t=60)
					if matchPlace:
						#print('c..if matchplace')
						result.append(matchPlace)
						return result
					else:
						#print('c. else matchplace')
						matchPlace = doMatch(matchCounty, getChoices('place', (matchCountry, matchCounty)), t=50)
						if matchPlace:
							result.append(matchPlace)
							return result
				else:
					#print('b. else..matchCounty')
					matchPlace = doMatch(" ".join(placeList[:-1]), getChoices('place', placeChoices), t=60)
					if matchPlace:
						#print('cc..if matchplace')
						matchCounty = lookupCountyFromPlace(matchPlace)
						if matchCounty:
							#matchCountry = lookupParent(matchCounty)
							#result.append(matchCountry)
							result.append(matchCounty)
							result.append(matchPlace)
							return result
						else:
							return None


			except IndexError:
				matchCounty = doMatch(placeList[-1], getChoices('county', matchCountry))
				matchPlace = doMatch(placeList[-1], getChoices('place', (matchCountry, matchCounty)), t=60)
				if matchCounty and matchPlace:
					result.append(matchCounty)
					result.append(matchPlace)
					return result

		else:
			#print('1. country not matched')
			try:
				matchCounty = doMatch(placeList[-1], countyChoices)
				if matchCounty:
					matchCountry = lookupParent(matchCounty)
					result.append(matchCountry)
					result.append(matchCounty)
					#print('2. if..', matchCountry, matchCounty, placeList[:-2])

					placeMatchString = " ".join(placeList[:-1]) or placeList[0]

					matchPlace = doMatch(placeMatchString, getChoices('place', (matchCountry, matchCounty)), t=50)
					if matchPlace:
						#print('3. if..matchplace', matchPlace)
						result.append(matchPlace)
						return result
					else:
						#print('3. else..matchplace', matchPlace)
						matchPlace = doMatch(matchCounty, getChoices('place', (matchCountry, matchCounty)), t=50)
						if matchPlace:
							result.append(matchPlace)
							return result
				else:
					#second from end doesn't match county... maybe it matches place??
					return None

			except Exception:
				return None
	except Exception:
		return None
		


'''

res = getPlaceRef('Someplace long place long long, Kells')
print(res)
if res:
	print('\n\nTHE ANSWER:::', placesLookup(res))

'''



files = Stream.Stream('Processed2016-02-16/shelves/ExtractorRPD_ExtractorMLP_FilterComplete_OmekaEditsLogged_TagsCleaned_PageTypesLogged_WrapOpener_FixAddrDateLines_BuildCollectionIdnos.shelve', 'Letter')

notThere = []

for k, i in files.stream():
	#print('-------------------\n\n', i['Sender_location'])
	#print(i.keys())
	res = getPlaceRef(i['Sender_location'])
	#print('res', res)
	if not res:
		notThere.append(i['Sender_location'])
		#print('\n\nTHE ANSWER:::', placesLookup(res))

	res = getPlaceRef(i['Recipient_location'])
	if not res:
		notThere.append(i['Recipient_location'])

for i in set(sorted(notThere)):
		print(i)
