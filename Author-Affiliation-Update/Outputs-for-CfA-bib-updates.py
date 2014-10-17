# coding: utf-8

# This script will only work if every affiliation has a corresponding author
# However the file can have authors without affiliations.

import os
import csv
import string
from datetime import datetime

allTheLetters = string.ascii_uppercase
standard_mapping = list(allTheLetters)

#Rahul's functioning for interating the alphabet for the affiliations
#only works for the first 676 authors (26x26, AA - ZZ)

def alphabets2(affiliations):
    outs=[]
    N=len(affiliations)
    maxmodulus = N / 26 #number of times 26 goes into N
    maxsecondletter =  N % 26 #left over amount after the above division
    if maxsecondletter == 0:
        howmanytimes=range(maxmodulus)
    else:
        howmanytimes=range(maxmodulus+1)
    j=0
    for i in howmanytimes:
        firstletter = standard_mapping[i]
        if i==(len(howmanytimes)) and maxsecondletter!=0:
            letters = [firstletter+standard_mapping[k] for k in range(maxsecondletter+1)]
        else:
            letters = [firstletter+standard_mapping[k] for k in range(26)]
        for l in letters:
            try:
                out = l+'('+affiliations[j].strip()+')'
                outs.append(out)
                j=j+1
            except IndexError:
                pass
    return outs
#/end Rahul's script

#modified Rahul's script to handle over 678 authors
#works for more than 676 authors (26x26x26, AAA-ZZZ)
#this is probably super messy and hacked together...but it seems to work!

def alphabets3(affiliations):
    outs = []
    N = len(affiliations)
    triplemodulus = N / 676
    maxmodulus = N / 26
    maxthirdletter = N % 26
    if maxthirdletter == 0:
        howmanytimes=range(maxthirdletter)
    else:
        howmanytimes=range(maxthirdletter+1)
    j = 0
    for a in range(0,triplemodulus+1):
        firstletter=standard_mapping[a]
        for b in range(0,26):
            secondletter=standard_mapping[b]
            for i in howmanytimes:
                if i ==(len(howmanytimes)) and maxthirdletter != 0:
                    letters = [firstletter+secondletter+standard_mapping[k] for k in range(maxthirdletter+1)]
                else:
                    letters = [firstletter+secondletter+standard_mapping[k] for k in range(26)]
            for l in letters:
                try:
                    out = l+'('+affiliations[j].strip()+')'
                    outs.append(out)
                    j=j+1
                except IndexError:
                    pass
    return outs
#/end modified Rahul's script

#this is where you put in new typos
           #"bad":"good",
typos  =   {"  ":" ",
            ",,":",",
            ",)":")",
            "..":".",}

def cleanup(stuff):
    for k, v in typos.iteritems():
        stuff = stuff.replace(k, v)
    return stuff
#/end typo section

#This creates and writes a file called "metadata_updates(timestamp).txt" that will list all author/affiliation updates marked on checkaffil.csv

timestamp = datetime.now().strftime("%Y_%m%d_%H%M")

metadata_updates = open('cfametadata_updates'+timestamp+'.txt', 'w')

with open('checkaffil.csv', 'rb') as f:
    reader = csv.reader(f)
    for row in reader:
        
        if '%Rc' in row:
            row.pop(2)
            bib = ('; ').join(row)
            bibcodes = bib.replace('%Rc;','%R')
            data=bibcodes.strip("; ")
            print data
            metadata_updates.write(data+'\n')

        elif '%Tc' in row or '%Tx' in row:
            titl = ('; ').join(row)
            title = titl.replace('%Tc;','*%T').replace('%Tx;','%T')
            data=title.strip("; ")
            metadata_updates.write(data+'\n') 
            
        elif '%Ac' in row or '%Ax' in row:
            row2 = filter(None, row)
            y = len(row2)
            auth = ('; ').join(row)
            authors = auth.replace('%Ac;','*%A').replace('%Ax;','%A')
            data=authors.strip("; ")
            cleaned = cleanup(data) #removes common errors as writen in the above cleanup function
            metadata_updates.write(cleaned+'\n')
        
        elif '%A' in row:
            row2 = filter(None, row)
            y = len(row2)            
        
        elif '%Fc' in row or '%Fx' in row:
            #if this record has more than 676 authors...
            if y >= 677:
                #run alphabets2 on the first 676 authors...
                shortaffillist = row[1:677]
                h=alphabets2(shortaffillist)
                h=[e for e in h if e[1:]!='()']
                affil = (', ').join(h)
                #run alphabets3 on the remaining authors...
                longafflist = row[677:y]
                o = alphabets3(longafflist)
                o=[p for p in o if p[1:]!='()']
                affillong = (', ').join(o)
                #put both lists together...
                data = (row[0]+" "+affil+affillong).replace('%Fc','*%F').replace('%Fx','%F')
                cleaned = cleanup(data) #removes common errors as writen in the above cleanup function
                metadata_updates.write(cleaned+'\n')  
                metadata_updates.write('\n')
            else:
                #if this record has less than 676 authors...
                row3 = row[1:y]
                h=alphabets2(row3) #uses Rahul's above function
                h=[e for e in h if e[0:]!='()'] #more code from Rahul!
                affil = (', ').join(h)
                data = (row[0]+" "+affil).replace('%Fc','*%F').replace('%Fx','%F')
                cleaned = cleanup(data) #removes common errors as writen in the above cleanup function
                metadata_updates.write(cleaned+'\n')  
                metadata_updates.write('\n')

metadata_updates.close()

print 'Finished creating output files - Yay!'