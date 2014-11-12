# coding: utf-8

import requests
import json
import csv
import time
import codecs
import cStringIO
#from unidecode import unidecode
from datetime import datetime

#NOTE: typical ADS API users have a limit of 50,000 total results and 200 results per page.
#As of Nov 12, 2014 this script is retrieving 44,451 results, so we're coming close to
#the limit of total results.

devkey = (open('dev_key.txt','r')).read() #txt file that only has your dev key

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

url1 = 'http://labs.adsabs.harvard.edu/adsabs/api/search/?q=bibgroup:cfa&fmt=json&dev_key='+str(devkey)
contentc = requests.get(url1)
j=contentc.json()

total = j['meta']['hits']
print "Total Results: "+str(total)

timestamp = datetime.now().strftime("%Y_%m%d_%H%M")

resultFile = open("cfa_bibcodes"+timestamp+".csv",'wb')

wr = UnicodeWriter(resultFile,dialect='excel',quoting=csv.QUOTE_ALL)

#write header row
wr.writerow(['Bibcode']+['PubDate']+['Title']+['Authors']+['Affiliations']+['Journal']+['Volume']+['Page']+['Citaions']+['URL'])

#how many times to loop
loop = total/200
print "Looping script "+str(loop)+" times."
startnum = 0

#looping a lot!
for i in range (1,loop+2):
    print "Results Page "+str(i)
    url = 'http://labs.adsabs.harvard.edu/adsabs/api/search/?q=bibgroup:cfa&start='+str(startnum)+'&rows=200&fmt=json&dev_key='+str(devkey)
    content = requests.get(url)
    k=content.json()
    docs = k['results']['docs']
    for x in docs:
        bibcode = x['bibcode']
        print bibcode
        
        absurl = "http://adsabs.harvard.edu/abs/"+bibcode
        
        try:
            affil = x['aff']
            affillist = (('; ').join(affil))
        except KeyError:
            affillist = ''        
                
        try:
            title = x['title']
            titleclean = (('').join(title))
        except KeyError:
            titleclean = ''
                
        try:
             pub = x['pub']
        except KeyError:
             pub = ''
        try:
             pubdate = x['pubdate']
        except KeyError:
             pubdate = ''                
                    
        try:
            volume = x['volume']
        except KeyError:
            volume = ''

        try:
            page = x['page']
            pageclean = "'"+('').join(page)
        except KeyError:
            pageclean = ''
            
        try:
            author = x['author']
            authorlist = (('; ').join(author))
        except KeyError:
            authorlist = ''
    
        try:
            citation_count = x['citation_count']
        except KeyError:
            citation_count = ''    
    
        try:
            year = x['year']
        except KeyError:
            year = ''                              
                
        row = [bibcode]+[pubdate]+[titleclean]+[authorlist]+[affillist]+[pub]+[volume]+[pageclean]+[str(citation_count)]+[absurl]
        wr.writerow(row)

        
    startnum += 200
    time.sleep(1)
    
resultFile.close()

print "Finished loops through all "+str(total)+" results!"