import Stream
from Processor import Processor
from fuzzywuzzy import fuzz, process

from EditLogger import EditLogger

editLogger = EditLogger()

class BuildPlaceRefs(Processor):

	def __init__(self, inputFilePath, outputFilePath, placeListFile, placeSheet='new'):
		self.resolve = self._addPlaceRef
		self.transform = self._addPlaceRef
		self.dict_key = 'Letter'
		self.inputFilePath = inputFilePath
		self.outputFilePath = outputFilePath



		places = Stream.Stream(placeListFile, 'Place', sheet=placeSheet)

		self.placesLookupDict =  {self.assemblePlaceTuple(v): v for _, v in places.stream()}
		
		self.placeChoices = list(set([k[0] for k, _ in self.placesLookupDict.items() if k]))
		self.countyChoices = list(set([k[1] for k, _ in self.placesLookupDict.items() if len(k)>1]))
		self.countryChoices = list(set([k[2] for k, _ in self.placesLookupDict.items() if len(k)>2]))


		placesDict = {}
		for country in self.countryChoices:
			placesDict[country] = {}
			for k, v in self.placesLookupDict.items():
				if len(k) > 2 and k[2] == country:
					placesDict[country][k[1]] = []
					for l, m in self.placesLookupDict.items():
						if len(l) > 2 and l[1] == k[1]:
							placesDict[country][k[1]].append(l[0])

		self.placesDict = placesDict

		super().__init__()

	@editLogger('Try to normalise sender and recipient places and refs', 'PythonScript')
	def _addPlaceRef(self, row):
		new_row = row

		sender_res = self.getPlaceRef(row['Sender_location'])
		if sender_res:
			new_row['SenderPlaceRefs'] = self.placesLookup(sender_res)
			
		else:
			new_row['SenderPlaceRefs'] =  None

		recipient_res = self.getPlaceRef(row['Recipient_location'])
		if recipient_res:
			new_row['RecipientPlaceRefs'] = self.placesLookup(recipient_res)
			
		else:
			new_row['RecipientPlaceRefs'] = None

		print(new_row['SenderPlaceRefs'], new_row['RecipientPlaceRefs'])

		return new_row


	# Builds a dict for reversing the lookup process
	def assemblePlaceTuple(self, v):
		return tuple(v[x] for x in ['Place', 'County', 'Country'] if v[x] is not None)



	def placesLookup(self, result):
		try:
			res = tuple(reversed(result))
			return self.placesLookupDict[res]
		except KeyError:
			return None

	def getChoices(self, level, identifier=None):
		#print('identifier:', identifier)
		if level == 'country':
			return self.countryChoices
		if level == 'county':
			return [k for k, v in self.placesDict[identifier].items()]
		if level == 'place':
			return self.placesDict[identifier[0]][identifier[1]]


	def normalise(self, place):
		
		replace = {'England': 'United Kingdom', 'UK': 'United Kingdom'}
		
		if place in replace:
			return replace[place]
		else:
			return place

	def doMatch(self, place, choices, t=70):
		#print(place, choices)
		match = process.extractOne(place, choices)
		#print(place, 'match', match)
		if match[1] > t:
			#print(place, match[0])
			return match[0]
		else:
			return False


	def lookupParent(self, place):
		for k, v in self.placesDict.items():
			if place in v.keys():
				return k

	def lookupCountyFromPlace(self, place):
		for k, v in self.placesDict.items():
			for l, m in v:
				if place in m.keys():
					return l

	def getPlaceRef(self, place):
		try:
			if place == 'NULL':
				#print('it is null')
				return None

			placeList =  [p.strip() for p in place.split(',')]
			
			result = []

			matchCountry = self.doMatch(self.normalise(placeList[-1]), self.getChoices('country'), t=80)
			# Is country
			if matchCountry:
				#print('a. country matched--')
				#print('matchCountry', matchCountry)
				try:
					result.append(matchCountry)
					matchCounty = self.doMatch(placeList[-2], self.getChoices('county', matchCountry))
					if matchCounty:
						#print('b.if.. matchCounty')
						#print('matchCounty', matchCounty)
						result.append(matchCounty)
						matchPlace = self.doMatch(" ".join(placeList[:-2]), self.getChoices('place', (matchCountry, matchCounty)), t=60)
						if matchPlace:
							#print('c..if matchplace')
							result.append(matchPlace)
							return result
						else:
							#print('c. else matchplace')
							matchPlace = self.doMatch(matchCounty, self.getChoices('place', (matchCountry, matchCounty)), t=50)
							if matchPlace:
								result.append(matchPlace)
								return result
					else:
						#print('b. else..matchCounty')
						matchPlace = self.doMatch(" ".join(placeList[:-1]), self.getChoices('place', self.placeChoices), t=60)
						if matchPlace:
							#print('cc..if matchplace')
							matchCounty = self.lookupCountyFromPlace(matchPlace)
							if matchCounty:
								#matchCountry = lookupParent(matchCounty)
								#result.append(matchCountry)
								result.append(matchCounty)
								result.append(matchPlace)
								return result
							else:
								return None


				except IndexError:
					matchCounty = self.doMatch(placeList[-1], self.getChoices('county', matchCountry))
					matchPlace = self.doMatch(placeList[-1], self.getChoices('place', (matchCountry, matchCounty)), t=60)
					if matchCounty and matchPlace:
						result.append(matchCounty)
						result.append(matchPlace)
						return result

			else:
				#print('1. country not matched')
				try:
					matchCounty = self.doMatch(placeList[-1], self.countyChoices)
					if matchCounty:
						matchCountry = self.lookupParent(matchCounty)
						result.append(matchCountry)
						result.append(matchCounty)
						#print('2. if..', matchCountry, matchCounty, placeList[:-2])

						placeMatchString = " ".join(placeList[:-1]) or placeList[0]

						matchPlace = self.doMatch(placeMatchString, self.getChoices('place', (matchCountry, matchCounty)), t=50)
						if matchPlace:
							#print('3. if..matchplace', matchPlace)
							result.append(matchPlace)
							return result
						else:
							#print('3. else..matchplace', matchPlace)
							matchPlace = self.doMatch(matchCounty, self.getChoices('place', (matchCountry, matchCounty)), t=50)
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


if __name__ == '__main__':
	b = BuildPlaceRefs('TEST2016-02-16/shelves/ExtractorRPD_ExtractorMLP_FilterComplete_OmekaEditsLogged_TagsCleaned_PageTypesLogged_WrapOpener_FixAddrDateLines_BuildCollectionIdnos.shelve',
		'shelve_files/addedPlaceRef.shelve', 'spreadsheets/placeList_ID.xlsx')

	b.process()