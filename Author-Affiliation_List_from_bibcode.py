# -*- coding: utf-8 -*-

import requests
import json
import csv
import time
import codecs
import cStringIO
import urllib
from datetime import datetime
import requests.packages.urllib3

requests.packages.urllib3.disable_warnings()

#UnicodeWriter from http://docs.python.org/2/library/csv.html#examples
class UnicodeWriter:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

#/end UnicodeWriter

devkey = (open('dev_key.txt','r')).read() #txt file that only has your dev key

timestamp = datetime.now().strftime("_%Y_%m%d_%H%M")

bibcodes = open('bibcodes.txt').read() #one bbicode per line
bibcode_lines = bibcodes.splitlines()

resultFile = open("paper_author"+timestamp+".csv",'wb')
wr = UnicodeWriter(resultFile,dialect='excel',quoting=csv.QUOTE_ALL)

wr.writerow(['bibcode','author','affiliation'])

for i in bibcode_lines:
    url = 'https://api.adsabs.harvard.edu/v1/search/query/?q=bibcode:'+urllib.quote(i)+'&fl=bibcode,pubdate,aff,author'
    print url #printing url for troubleshooting
  
    headers={'Authorization': 'Bearer '+devkey}
    content = requests.get(url, headers=headers)
    results=content.json()
    k = results['response']['docs'][0]

    try:
        authors = k['author']
    except KeyError:
        print "bad author"
     
    try:
        affil = k['aff']
    except KeyError:
        print "bad affil"
    
    n = len(authors)
    for x in range(0, n):
        try:
            wr.writerow([i] + [authors[x]] + [affil[x]])
        except IndexError:
            wr.writerow([i] + [authors[x]])

    #wr.writerow([''])
    time.sleep(1)
    
resultFile.close()
print 'finished getting data, look at paper_author_(timestamp).csv'