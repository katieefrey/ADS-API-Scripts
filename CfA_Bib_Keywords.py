# -*- coding: utf-8 -*-

import requests
import json
import nltk
from nltk.tokenize import LineTokenizer
import csv
import time
import codecs
import cStringIO
import requests.packages.urllib3

requests.packages.urllib3.disable_warnings()


"""
    url = 'https://api.adsabs.harvard.edu/v1/search/query/?q=bibcode:'+urllib.quote(i)+'&fl=bibcode,pubdate,aff,author,year,pub,title,abstract,keyword'
    print url
    
    headers = {'Authorization': 'Bearer '+devkey}
    content = requests.get(url, headers=headers)
    results = content.json()
    k = results['response']['docs'][0]
"""

#enter numerical value for your starting date (month and year)
startYear = 2013
startMonth = 1

#enter numerical value for your ending date (month and year)
endYear = 2013
endMonth = 4

#location and file name of your ADS devkey
devkey = (open('dev_key.txt','r')).read()

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

realendMonth = endMonth+1
realendYear =  endYear+1

daterange = ' - '+str(startMonth)+' '+str(startYear)+' to '+str(endMonth)+' '+str(endYear)

text = codecs.open('keywords'+daterange+'.txt','w')
for y in range(startYear,realendYear):
    for m in range(startMonth,realendMonth): # first number is starting month, last number needs to be one more than final month
        #url = 'http://labs.adsabs.harvard.edu/adsabs/api/search/?q=bibgroup:cfa,pubdate:'+str(y)+'-'+str(m)+'&rows=200&fl=keyword&fmt=json&dev_key='+str(devkey)
        url = 'https://api.adsabs.harvard.edu/v1/search/query/?q=pubdate:'+str(y)+'-'+str(m)+'&rows=200&fl=bibcode,bibgroup:cfapubdate,aff,author,year,pub,title,abstract,keyword'
        print url
        
        headers = {'Authorization': 'Bearer '+devkey}
        content = requests.get(url, headers=headers)
        results = content.json()
        k = results['response']['docs']

        for i in k:
            try:
                mywords=i['keyword']
                myList = list(set(mywords)) #magic line that removes exact duplicates from an articles keywords
                cleanList = u' '.join(myList)
                unicode_list = (str(y)+'|'+str(m)+'|')+u'**'.join(myList)
                clean_unicode = '\n'+unicode_list.replace('**','\n'+str(y)+'|'+str(m)+'|')
                #print clean_unicode
                text.write(clean_unicode.encode('utf-8'))
            except KeyError:
                pass
        time.sleep(1)
text.close()
print 'finished getting keywords'

text = open('keywords'+daterange+'.txt','r').read()
freqlist = open('freqlist'+daterange+'.txt','wb')
lowertext = text.lower()
lines = LineTokenizer(blanklines='discard').tokenize(lowertext)
freq = nltk.FreqDist(lines)
#print freq
writer = csv.writer(freqlist, delimiter='|', lineterminator='\n', quotechar='"', quoting=csv.QUOTE_MINIMAL)
writer.writerows(freq.items())
freqlist.close()
print 'finished getting frequency distribution'

fileout = codecs.open('frequency'+daterange+'.csv', 'wb')

csv_out = csv.writer(fileout, lineterminator='\n', delimiter=',')
wr = UnicodeWriter(fileout,lineterminator='\n', delimiter=',', dialect='excel',quoting=csv.QUOTE_ALL)

wr.writerow(["Year","Month","Keyword","Frequency"])
f = codecs.open('freqlist'+daterange+'.txt')
for line in f:
    vals = line.split('|')
    words = [v.replace('\n', '') for v in vals]
    words1 = [v.replace('"', '') for v in words]
    #print words1
    csv_out.writerow((words1[0], words1[1], words1[2], words1[3]))
f.close()
fileout.close()
print 'finished writing csv file'