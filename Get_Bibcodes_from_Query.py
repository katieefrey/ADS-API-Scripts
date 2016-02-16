import requests
import time
import datetime
import requests.packages.urllib3
import json
import time
import codecs
import cStringIO

requests.packages.urllib3.disable_warnings()

#returns bibcodes based on a custom query

devkey = (open('dev_key.txt','r')).read() #txt file that only has your dev key

#finds everything in the CfA Bibgroup that does NOT have a CfA affiliation (helps to weed out things that do not belong in the bibgroup)
#query = 'bibgroup:CfA year:2015 -(aff:"Harvard-Smithsonian" OR aff:"Harvard" OR aff:"Smithsonian" OR aff:"ITAMP" OR aff:"CfA" OR aff:"Whipple" OR aff:"FLWO")

#finds all papers with CfA affiliations that are NOT in the CfA Bibgroup
query = '(aff:"Harvard-Smithsonian" OR aff:"Harvard" OR aff:"Smithsonian" OR aff:"ITAMP" OR aff:"CfA" OR aff:"Whipple" OR aff:"FLWO") -bibgroup:CfA pubdate:[1600-01-00 TO 1799-12-31]'

r = requests.get('https://api.adsabs.harvard.edu/v1/search/query', params={'q': query}, headers={'Authorization': 'Bearer '+devkey})

num_found = r.json()['response']['numFound']
bibcodes = []

start = 0
while start < num_found:
	r = requests.get('https://api.adsabs.harvard.edu/v1/search/query', params={'q': query, 'fl': 'bibcode', 'rows': 100, 'start': start}, headers={'Authorization': 'Bearer '+devkey})
	start += 100
	for d in r.json()['response']['docs']:
		bibcodes.append(d['bibcode'])
		#print d

fo = open('bibcodes.%s.txt' % datetime.datetime.utcnow().isoformat().replace(':', '-'), 'w')
fo.write('\n'.join(bibcodes))
fo.close()	