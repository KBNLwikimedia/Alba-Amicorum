import json
import xmltodict
import re
import pandas as pd

filename = "bosboom-toussaint.xml"
with open(filename, encoding="UTF-8") as fd:
    creatordictlist = []
    doc = xmltodict.parse(fd.read())
    for i in range(len(doc['srw:searchRetrieveResponse']['srw:records']['srw:record'])):
        creatordict = {}
        row = doc['srw:searchRetrieveResponse']['srw:records']['srw:record'][i]['srw:recordData']['srw_dc:dc']
        creatordict['dcx:recordIdentifier']  = row['dcx:recordIdentifier']
        creatordict['dc:identifier']         = row['dc:identifier']['#text']
        creatordict['dc:title']              = row['dc:title']
        creatordict['dcx:annotation']        = row['dcx:annotation']
        creatordict['dcterms:created'] = row['dcterms:created'] if 'dcterms:created' in row else ""
        creatordict['dcterms:medium']  = [x for x in row['dcterms:medium']][0].replace('@xsi:type','')
        creatordict['dc:creator']  = 'N. N.'
        creatordict['dc:creator2'] = ""
        if 'dc:creator' in row:
            creatordict['dc:creator'] = row['dc:creator']
            if creatordict['dc:creator'].find(',') != -1:
            	names = creatordict['dc:creator'].split(' & ')
            	for x in range(len(names)):
            		names[x] = re.sub(r'(.+?), (.+)', r'\2 \1', names[x])
            	creatordict['dc:creator2'] = " & ".join(names)
        descriptions = []
        if 'dc:description' in row:
            if isinstance(row['dc:description'], str):
                descriptions.append(row['dc:description'])
            else:
                for x in row['dc:description']:
                    if isinstance(x, str):
                        descriptions.append(x)
                    elif isinstance(x, dict):
                        descriptions.append(x['#text'])
        descriptions.reverse()
        creatordict['dc:description'] = descriptions
        creatordictlist.append(creatordict)

dfcolumns = ['dcx:recordIdentifier','dc:identifier','dc:title','dcterms:created','dcterms:medium','dcx:annotation','dc:creator', 'dc:creator2']
maxLenghts = {}
maxLenghts["dc:description"] = max([len(creatordictlist[y]["dc:description"]) for y in range(len(creatordictlist))])
dfcolumns += ["dc:description"+str(x) for x in range(maxLenghts["dc:description"])]
df = pd.DataFrame(columns=dfcolumns)
for row in creatordictlist:
    contribtuple = [
    	row.get('dcx:recordIdentifier'),
		row.get('dc:identifier'),
		row.get('dc:title'),
		row.get('dcterms:created'),
		row.get('dcterms:medium'),
		row.get('dcx:annotation'),
		row.get('dc:creator'),
		row.get('dc:creator2')]
    for x in maxLenghts:
        for y in range(maxLenghts[x]):
        	try:
        		contribtuple.append(row[x][y])
        	except IndexError as e:
        		contribtuple.append("")
    s = pd.Series(contribtuple, index=df.columns)
    df = df.append(s, ignore_index=True)
print(df)
df.to_excel("contributors-"+filename[:-4]+".xlsx")
