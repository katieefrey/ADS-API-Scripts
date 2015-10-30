# -*- coding: utf-8 -*-

import requests
import json
import csv
import time
import codecs
import cStringIO
import sys
import urllib

requests.packages.urllib3.disable_warnings()

reload(sys)
sys.setdefaultencoding("utf-8")

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

bibcodes = open('bibcodes.txt').read() #one bbicode per line
bibcode_lines = bibcodes.splitlines()

resultFile = open("checkaffil-api.csv",'wb')
wr = UnicodeWriter(resultFile,dialect='excel',quoting=csv.QUOTE_ALL)

wr.writerow(['.'])

for i in bibcode_lines:
    url = 'https://api.adsabs.harvard.edu/v1/search/query/?q=bibcode:'+urllib.quote(i)+'&fl=bibcode,pubdate,aff,author,year,pub,title,abstract,keyword'
    print url
    
    headers = {'Authorization': 'Bearer '+devkey}
    content = requests.get(url, headers=headers)
    results = content.json()
    k = results['response']['docs'][0]    
    
    wr.writerow(['%R']+[i]) #write the bibcode
    
    try:
        title = k['title']    
        wr.writerow(['%T']+title)
    except KeyError:
        wr.writerow(['%T'])

    try:
        authors = k['author']   
        wr.writerow(['%A']+authors)
    except KeyError:
        wr.writerow(['%A'])
    
    try:
        afillist = []
        affil = k['aff']
        #print affil
        for i in affil:
            #print i
            if i == "-":
                afillist.append("")
            else:
                afillist.append(i)
        #print ["lok"] + afillist
        wr.writerow(['%F']+afillist)


    except KeyError:
        wr.writerow(['%F'])
    
    wr.writerow([''])
    time.sleep(1)
    
resultFile.close()
print 'finished getting data, look at checkaffil.csv'