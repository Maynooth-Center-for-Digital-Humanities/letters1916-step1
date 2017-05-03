from CheckSpreadsheet import Checker
import Extractor as Extractor
from Processor import Filter as Filter
import Filter as FilterLists
import Cleaners
import PageTypeLoggers
import wrapOpener
import FixAddrLinesDates
import BuildCollectionIdnos
import BuildInstitutionRefs
import BuildPlaceRefs
import BuildNameRefs

import datetime
import os
import shelve
import shutil
import yaml

class ProcessQueue:
	def __init__(self, config):

		self.config = config

		#print(self.config["templateFile"])
		
		self.inputFilePath = config["inputFilePath"]

		self.filter_configs = config["filter_configs"]
		self.editLogger_configs = config["editLogger_configs"]
		self.buildInstitutionRefs_configs = config["buildInstitutionRefs_configs"]
		self.buildPlaceRefs_configs = config["buildPlaceRefs_configs"]
		self.buildNameRefs_configs = config["buildNameRefs_configs"]

		self.output_file_name = ""

		folder_name = config["outputFolder"] + config["processingFolderPrefix"] + datetime.datetime.today().strftime("%Y-%m-%d")

		if os.path.isdir(folder_name):
			shutil.rmtree(folder_name)

		os.mkdir(folder_name)
		os.mkdir(folder_name + '/' + 'xmlfiles')
		os.mkdir(folder_name + '/' + 'shelves')

		self.shelve_directory = folder_name + '/' + 'shelves/'
		self.output_directory = folder_name + '/' + 'xmlfiles/'

	def __call__(self):
		self.run_Checker()
		self.run_Extractor_RPD()
		self.run_Extractor_MLP()
		self.run_Filter()
		self.run_EditLogger()
		self.run_Cleaners()
		self.run_PageTypeLoggers()
		self.run_WrapOpener()
		self.run_FixAddrLines()
		self.run_BuildCollectionIdnos()
		self.run_BuildInstitutionRefs()
		self.run_BuildPlaceRefs()
		self.run_BuildNameRefs()
		#self.run_StreamOutput()
		self.run_Templater()

	def run_Checker(self):
		c = Checker(self.inputFilePath)
		c.check()
	

	def run_Extractor_RPD(self):
		self.output_file_name = 'ExtractorRPD'
		r = Extractor.RemovePageDuplicates(self.inputFilePath, self.output_file_path())
		#print(self.output_file_name)
		r.process()

	def run_Extractor_MLP(self):
		self.update_file_names('ExtractorMLP')
		m = Extractor.MergeLetterPages(self.input_file_path(), self.output_file_path())
		#print(self.input_file_name, self.output_file_name)
		m.process()

	def run_Filter(self):
		self.update_file_names('FilterComplete')
		
		# Set up filter object
		f = Filter(self.input_file_path(), self.output_file_path())

		if 'inclusionListObject' in self.filter_configs:
			f.inclusionListAdd(self.filter_configs["inclusionListObject"])

		if 'exclusionListObject' in self.filter_configs:
			f.exclusionListAdd(self.filter_configs["exclusionListObject"])


		if 'inclusionDirectoryPath' in self.filter_configs:
			incList = FilterLists.ListFromDirectory(self.filter_configs["inclusionDirectoryPath"])
			f.inclusionListAdd(incList)

		if 'inclusionFilePath' in self.filter_configs:
			incList = FilterLists.ListFromExcel(self.filter_configs["inclusionFilePath"], 
				'ID', self.filter_configs["inclusionCutoffDate"])
			f.inclusionListAdd(incList)
		
		if 'exclusionDirectoryPath' in self.filter_configs:
			excList = FilterLists.ListFromDirectory(self.filter_configs["exclusionDirectoryPath"])
			f.exclusionListAdd(excList)
		if 'exclusionURL' in self.filter_configs:
			excList  = FilterLists.ListFromURL(self.filter_configs["exclusionURL"])
			f.exclusionListAdd(excList)
		
		f.filter()

	def run_EditLogger(self):
		''' Script written in **horrible** way -- only option to call from command line '''
		self.update_file_names('OmekaEditsLogged')
		command = "python Extractor/EditLogger.py -i " + self.input_file_path() \
					+ ' -o ' + self.output_file_path() + ' -f ' \
					+ "'" + self.editLogger_configs["editFilePath"] + "'"
		os.system(command)

	def run_Cleaners(self):
		self.update_file_names('TagsCleaned')
		fix_tags = Cleaners.FixTags(self.input_file_path(), self.output_file_path())
		fix_tags.process()


	def run_PageTypeLoggers(self):
		self.update_file_names('PageTypesLogged')
		logger = PageTypeLoggers.PageTypeLogger(self.input_file_path(), self.output_file_path())
		logger.process()

	def run_WrapOpener(self):
		self.update_file_names('WrapOpener')
		w = wrapOpener.WrapOpenerAndCloser(self.input_file_path(), self.output_file_path())
		w.process()

	def run_FixAddrLines(self):
		self.update_file_names('FixAddrDateLines')
		f = FixAddrLinesDates.FixAddrLineDate(self.input_file_path(), self.output_file_path())
		f.process()

	def run_BuildCollectionIdnos(self):
		self.update_file_names('BuildCollectionIdnos')
		b = BuildCollectionIdnos.BuildCollectionIdnos(self.input_file_path(), self.output_file_path())
		b.process()

	def run_BuildInstitutionRefs(self):
		self.update_file_names('BuildInstitutionRefs')
		
		
		b = BuildInstitutionRefs.BuildInstitutionRefs(self.input_file_path(), self.output_file_path(), self.buildInstitutionRefs_configs['instListFile'])

		b.process()


	def run_BuildPlaceRefs(self):
		self.update_file_names('BuildPlaceRefs')
		b = BuildPlaceRefs.BuildPlaceRefs(self.input_file_path(), self.output_file_path(), self.buildPlaceRefs_configs['placeListFile'])
		b.process()

	def run_BuildNameRefs(self):
		self.update_file_names('BuildNameRefs')
		b =  BuildNameRefs.BuildNameRefs(self.input_file_path(), self.output_file_path(), self.buildNameRefs_configs['nameListFile'])
		b.process()

	def run_Templater(self):
		self.update_file_names('Templateable')
		#print(self.input_file_path())
		command = "python Extractor/Templater.py" \
				+  " -i " + self.input_file_path() + " -d " + self.output_directory \
				+ " -t " + self.config["templateFile"]
		#print(command)
		os.system(command)

	def run_StreamOutput(self):
		''' Quick sanity check by outputting the entire finished doc '''
		command = "python Extractor/Stream.py -f " + self.output_file_path() \
					+ ' -k Letter'
		os.system(command)



	'''
	Util functions for managing file names and paths
	'''
	def input_file_path(self):
		return self.shelve_directory + self.input_file_name + '.shelve'

	def output_file_path(self):
		return self.shelve_directory + self.output_file_name + '.shelve'

	def update_file_names(self, addition):
		self.input_file_name = self.output_file_name
		self.output_file_name = self.input_file_name + "_" + addition



if __name__ == '__main__':
	def arbitraryInclusionList():
		return [77]

	def arbitraryExclusionList():
		#return [x.strip('.xml')+'.0' for x in  ["1323.xml", "1333.xml", "1339.xml", "1342.xml", "136.xml", "138.xml", "1380.xml", "1383.xml", "1385.xml", "140.xml", "1400.xml", "1403.xml", "1406.xml", "1409.xml", "141.xml", "1410.xml", "1421.xml", "1428.xml", "143.xml", "1431.xml", "1444.xml", "1447.xml", "1451.xml", "1452.xml", "1454.xml", "1455.xml", "146.xml", "1474.xml", "1476.xml", "1477.xml", "1478.xml", "1479.xml", "1489.xml", "149.xml", "1491.xml", "1493.xml", "1494.xml", "1498.xml", "1500.xml", "1517.xml", "1539.xml", "155.xml", "1550.xml", "1561.xml", "1579.xml", "158.xml", "159.xml", "1610.xml", "1617.xml", "162.xml", "1620.xml", "1622.xml", "1625.xml", "1644.xml", "1648.xml", "1649.xml", "165.xml", "169.xml", "1714.xml", "1715.xml", "1746.xml", "1747.xml", "1768.xml", "1776.xml", "1811.xml", "1023.xml", "132.xml", "178.xml", "1816.xml", "1027.xml", "1137.xml", "1148.xml", "1321.xml", "1322.xml", "1384.xml", "1619.xml", "1621.xml", "1647.xml", "1798.xml", "182.xml", "1038.xml", "1039.xml", "1154.xml", "1162.xml", "1163.xml", "121.xml", "1266.xml", "1315.xml", "1618.xml", "171.xml", "1769.xml", "1803.xml", "1829.xml", "1090.xml", "1165.xml", "1580.xml", "163.xml", "166.xml", "1662.xml", "1713.xml", "1738.xml", "174.xml", "1770.xml", "1804.xml", "1830.xml", "108.xml", "1081.xml", "1133.xml", "1134.xml", "1135.xml", "1136.xml", "1138.xml", "1155.xml", "1178.xml", "1182.xml", "1198.xml", "1265.xml", "1275.xml", "1317.xml", "1334.xml", "1338.xml", "164.xml", "1741.xml", "1771.xml", "1805.xml", "1831.xml", "1127.xml", "1129.xml", "1130.xml", "1132.xml", "1160.xml", "1268.xml", "1295.xml", "1772.xml", "1806.xml", "1838.xml", "1092.xml", "1122.xml", "115.xml", "1267.xml", "1297.xml", "175.xml", "1763.xml", "1773.xml", "1808.xml", "1839.xml", "1030.xml", "1040.xml", "1059.xml", "1063.xml", "1064.xml", "1069.xml", "1070.xml", "1071.xml", "1072.xml", "1073.xml", "1310.xml", "1311.xml", "1312.xml", "1314.xml", "1319.xml", "1774.xml", "1809.xml", "1845.xml", "1021.xml", "1775.xml", "1810.xml", "1846.xml", "1046.xml", "1052.xml", "1056.xml", "1065.xml", "1093.xml", "1100.xml", "1118.xml", "1142.xml", "1146.xml", "1159.xml", "1213.xml", "1222.xml", "1258.xml", "1264.xml", "1293.xml", "1306.xml", "1343.xml", "1353.xml", "1375.xml", "1393.xml", "1426.xml", "1464.xml", "1481.xml", "1514.xml", "1523.xml", "1530.xml", "1552.xml", "1560.xml", "1566.xml", "1577.xml", "1583.xml", "1974.xml", "1987.xml", "1991.xml", "1035.xml", "1042.xml", "1047.xml", "1053.xml", "1057.xml", "1067.xml", "1095.xml", "1101.xml", "1120.xml", "1143.xml", "1147.xml", "1161.xml", "1215.xml", "1227.xml", "1259.xml", "1269.xml", "1300.xml", "1307.xml", "1347.xml", "1366.xml", "1378.xml", "1411.xml", "1437.xml", "1470.xml", "1488.xml", "1515.xml", "1525.xml", "1542.xml", "1553.xml", "1562.xml", "1574.xml", "1578.xml", "1585.xml", "1847.xml", "198.xml", "1024.xml", "1036.xml", "1043.xml", "1048.xml", "1054.xml", "1061.xml", "1068.xml", "1098.xml", "1103.xml", "1140.xml", "1144.xml", "1157.xml", "1205.xml", "1219.xml", "1229.xml", "1262.xml", "1270.xml", "1301.xml", "1308.xml", "1348.xml", "1369.xml", "1390.xml", "1413.xml", "1445.xml", "1473.xml", "1505.xml", "1518.xml", "1526.xml", "1543.xml", "1556.xml", "1564.xml", "1575.xml", "1581.xml", "1591.xml", "1850.xml", "1851.xml", "1858.xml", "1861.xml", "1865.xml", "1866.xml", "187.xml", "1876.xml", "1877.xml", "1879.xml", "1881.xml", "1882.xml", "1883.xml", "1884.xml", "1885.xml", "1886.xml", "1887.xml", "1888.xml", "1889.xml", "189.xml", "1897.xml", "1898.xml", "1901.xml", "191.xml", "1910.xml", "1911.xml", "1912.xml", "1915.xml", "1917.xml", "1920.xml", "193.xml", "1940.xml", "1988.xml", "1025.xml", "1037.xml", "1045.xml", "1049.xml", "1055.xml", "1062.xml", "1091.xml", "1099.xml", "1104.xml", "1141.xml", "1145.xml", "1158.xml", "1212.xml", "1221.xml", "1233.xml", "1263.xml", "1274.xml", "1304.xml", "1309.xml", "1352.xml", "1372.xml", "1391.xml", "1418.xml", "1450.xml", "1480.xml", "1513.xml", "1520.xml", "1527.xml", "1544.xml", "1557.xml", "1565.xml", "1576.xml", "1582.xml", "1594.xml", "1595.xml", "1596.xml", "1597.xml", "1598.xml", "1599.xml", "1600.xml", "1601.xml", "1604.xml", "1612.xml", "1614.xml", "1640.xml", "1643.xml", "1665.xml", "1667.xml", "1672.xml", "1679.xml", "1790.xml", "1807.xml", "1855.xml", "1856.xml", "1864.xml", "1871.xml", "1875.xml", "1892.xml", "1893.xml", "1894.xml", "1895.xml", "1896.xml", "1899.xml", "1916.xml", "1918.xml", "1919.xml", "1921.xml", "1922.xml", "1923.xml", "1925.xml", "1926.xml", "1966.xml", "1968.xml", "1992.xml", "1999.xml", "2000.xml", "2002.xml", "2004.xml", "2005.xml", "201.xml", "2010.xml", "2011.xml", "2017.xml", "203.xml", "2040.xml", "2053.xml", "206.xml", "207.xml", "2077.xml", "2096.xml", "2101.xml", "2106.xml", "2108.xml", "2109.xml", "2110.xml", "212.xml", "213.xml", "214.xml", "2140.xml", "2146.xml", "215.xml", "216.xml", "218.xml", "2185.xml", "2187.xml", "2189.xml", "219.xml", "2192.xml", "2195.xml", "220.xml", "2204.xml", "224.xml", "2246.xml", "225.xml", "2255.xml", "2256.xml", "2257.xml", "226.xml", "227.xml", "2283.xml", "2289.xml", "2292.xml", "2294.xml", "2296.xml", "230.xml", "231.xml", "2340.xml", "2353.xml", "2354.xml", "2356.xml", "2359.xml", "2361.xml", "2364.xml", "2365.xml", "2377.xml", "2378.xml", "2379.xml", "2380.xml", "2382.xml", "2383.xml", "2384.xml", "2385.xml", "2386.xml", "2389.xml", "2390.xml", "2392.xml", "2393.xml", "2394.xml", "2395.xml", "2396.xml", "2399.xml", "2402.xml", "2404.xml", "2406.xml", "2407.xml", "2409.xml", "241.xml", "2410.xml", "2411.xml", "2413.xml", "2414.xml", "242.xml", "244.xml", "245.xml", "246.xml", "247.xml", "249.xml", "252.xml", "253.xml", "255.xml", "256.xml", "257.xml", "267.xml", "284.xml", "289.xml", "296.xml", "32.xml", "321.xml", "326.xml", "334.xml", "335.xml", "337.xml", "34.xml", "341.xml", "342.xml", "36.xml", "365.xml", "368.xml", "378.xml", "379.xml", "38.xml", "380.xml", "402.xml", "408.xml", "413.xml", "42.xml", "429.xml", "439.xml", "44.xml", "441.xml", "444.xml", "448.xml", "449.xml", "45.xml", "461.xml", "501.xml", "56.xml", "58.xml", "607.xml", "608.xml", "609.xml", "636.xml", "69.xml", "700.xml", "728.xml", "79.xml", "865.xml", "866.xml", "867.xml", "87.xml", "906.xml", "907.xml", "930.xml", "958.xml", "970.xml", "971.xml", "972.xml", "973.xml", "976.xml", "977.xml", "978.xml", "979.xml", "980.xml", "981.xml", "983.xml", "984.xml", "985.xml", "986.xml", "987.xml", "988.xml", "989.xml", "99.xml", "999.xml", "450.xml", "451.xml", "452.xml", "453.xml", "458.xml", "459.xml", "463.xml", "464.xml", "473.xml", "475.xml", "478.xml", "482.xml", "499.xml", "500.xml"]]
		return []

	elist = {
		'Badzmiek': ("Karolina Badzmierowska", "KB"),
		"Bleierr": ("Roman Bleier", "RB"),
		"RB": ("Roman Bleier", "RB"),
		"Brhughes": ("Brian Hughes", "BH"),
		"Emma": ("Emma Clarke", "EC"),
		"HannahH" : ("Hannah Healy", "HH"),
		"HH" : ("Hannah Healy", "HH"),
		"Linda" : ("Linda Spinazzè", "LS"),
		"NealeRo": ("Neale Rooney", "NR"),
		"NR": ("Neale Rooney", "NR"),
		"Schreibs": ("Susan Schreibman", "SS"),
		"SS": ("Susan Schreibman", "SS"),
		"William.buck": ("William Buck", "WB"),
		"badzmiek": ("Karolina Badzmierowska", "KB"),
		"VDG": ("Vinayak Das Gupta", "VDG"),
		"Mfar": ("Mel Farrell", "MF"),
		"Oculardexterity": ("Richard Hadden", "RH"),
		"Roman": ("Roman Bleier", "RB"),
		"Smcgarry": ("Shane McGarry", "SMG"),
		"lindaspinazze": ("Linda Spinazzè", "LS"),
		"Precaurious": ("Linda Spinazzè", "LS"),
		"Vinayak": ("Vinayak Das Gupta", "VDG")
	}

	with shelve.open('Data/editorList.shelve') as shelf:
		for k, v in elist.items():
			shelf[k] = v

	with open('config.yaml') as f:
		config = yaml.load(f.read())

	#print(config)
	
	p = ProcessQueue(config)
	p()