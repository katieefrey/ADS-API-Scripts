# -*- coding: utf-8 -*-

import csv
import time
import string
from lxml import etree
import codecs
import cStringIO
import sys
import itertools

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

#Code from Alberto Accomazzi to split the ADS affiliation string into a list of affiliations
#https://gist.github.com/aaccomazzi/8103059
letters = [ c for c in string.uppercase ]
double_aff = [ "%c%c" % (x,y) for (x,y) in itertools.product(letters,letters) ]
triple_aff = [ "%s%c" % (x,y) for (x,y) in itertools.product(double_aff,letters) ]

AFFILIATION_LABELS = double_aff + triple_aff

def parse_balanced_affiliations(string):
    """
    Generate parenthesized contents in string as pairs (level, contents).
    For affiliations: only return level 0, where stack size is 0. 
    There is only one assumption: affliation labels are never longer
    than 3 characters (AA ... ZZZ), i.e. there are no publications with
    more than 18253 authors.
    You cannot use regular expressions to parse ADS affiliations, so we use
    parenthesis counting and a stack.
    """
    affmap = {}
    preceding = {}
    stack = []
    for i, c in enumerate(string):
        if c == '(':
            stack.append(i)
            preceding[i] = string[max(0,i-3):i]
        elif c == ')' and stack:
            start = stack.pop()
            if not stack:
                ADSlabel = preceding[start].strip()
                ADSlabel = ADSlabel.replace(',','').strip()
                try:
                    aff_index = AFFILIATION_LABELS.index(ADSlabel)
                except:
                    raise Exception('Unrecognized Affilation Label: %s'%ADSlabel)
                affmap[aff_index] = string[start + 1: i]
    return affmap

#/end affiliation string code

bibcodes = open('bibcodes.txt').read() #reads from a file that has one bibcode per line
bibcode_lines = bibcodes.splitlines()

resultFile = open("checkaffil.csv",'wb') #creates and writes (overwrites) this file
wr = UnicodeWriter(resultFile,dialect='excel',quoting=csv.QUOTE_ALL)

wr.writerow(['.'])

for i in bibcode_lines:
    print i
    url = 'http://adsabs.harvard.edu/abs/'+i+'&data_type=XML'    
    print url #printing url for troubleshooting
    
    wr.writerow(['%R']+[i]) #write the bibcode
    
    tree = etree.parse(url)
    root = tree.getroot()

    for title in root.iter('{http://ads.harvard.edu/schema/abs/1.1/abstracts}title'):
        t = title.text
    wr.writerow(['%T']+[t]) #write article title
    
    b = []
    for auth in root.iter('{http://ads.harvard.edu/schema/abs/1.1/abstracts}author'):
        author = auth.text
        b.append(author)
    wr.writerow(['%A']+b) #write author list

    a = ''
    for affil in root.iter('{http://ads.harvard.edu/schema/abs/1.1/abstracts}affiliation'):
        try:
            a = affil.text
        except NameError:
            pass

    if a != '':
        affil1 = parse_balanced_affiliations(a) #uses the code from Alberto
        c = []
        for key,value in affil1.iteritems():
            c.append(value)    
        wr.writerow(['%F']+c) #write affiliation list
    else:
        wr.writerow(['%F']) #write affiliation list

    wr.writerow(['']) #writes a blank row
    time.sleep(1)
    
resultFile.close()
print 'finished getting data, look at checkafill.csv'