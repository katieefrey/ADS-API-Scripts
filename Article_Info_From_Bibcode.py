# -*- coding: utf-8 -*-

import requests
import json
import time
import csv
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

devkey = (open('dev_key.txt','r')).read()

#you need to start with a text file containing a list of bibcodes
bib = open('bibcodes.txt').read()

timestamp = datetime.now().strftime("%Y_%m%d_%H%M")

fileout = codecs.open('article_info'+timestamp+'.csv','wb') #will create or overwrite this file name
wr = UnicodeWriter(fileout,lineterminator='\n', delimiter=',', dialect='excel',quoting=csv.QUOTE_ALL)

bib1 = bib.splitlines()
bib_lines = [x.strip() for x in bib1]

for i in bib_lines:
    url = 'https://api.adsabs.harvard.edu/v1/search/query/?q=bibcode:'+urllib.quote(i)+'&fl=bibcode,pubdate,aff,author,year,pub,title,abstract,keyword'
    print url
    
    headers = {'Authorization': 'Bearer '+devkey}
    content = requests.get(url, headers=headers)
    results = content.json()
    k = results['response']['docs'][0]

    try:
        year = k['year']
    except KeyError:
        year = ''

    try:
        pub = k['pub']
    except KeyError:
        pub = ''

    try:
        title = k['title']
    except KeyError:
        title = ''

    try:
        author = k['author']
        authors = '; '.join(author)
    except KeyError:
        authors = ''

    try:
        aff = k['aff']
        affil = '; '.join(aff)
    except KeyError:
        affil = ''

    try:
        abstract = k['abstract']
    except KeyError:
        abstract = ''

    try:
        keyword = k['keyword']
        keywords = '; '.join(keyword)
    except KeyError:
        keywords = ''

    print i
    
    wr.writerow([year]+[pub]+title+[authors]+[affil]+[abstract]+[keywords]+[i]+['\r'])
    
    time.sleep(.25)

print 'Katie\'s awesome script has just made your life a little easier.'
fileout.close()
#comment