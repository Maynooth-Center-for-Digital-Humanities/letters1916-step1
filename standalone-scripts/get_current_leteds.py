
import re
import urllib.request
import json
import sys


sys.path.append('Extractor')
import Filter



urlList = Filter.ListFromURL("http://xl1916mono.mucampus.ie:5001/currentFiles")()
print(urlList)

#fileList = Filter.ListFromExcel('spreadsheets/ProofingTranscriptionsAbstracts14122015.xlsx', 'ID')()
fileList = Filter.ListFromDirectory('Processed2015-12-14/xmlfiles')()
print(fileList)
print(set(urlList).intersection(fileList))



