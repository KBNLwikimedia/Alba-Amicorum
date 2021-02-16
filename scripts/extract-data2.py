#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import xmltodict
import pandas as pd

filename = "J. Heyblocq 131H26.xml"

languages = {
    'Dutch; Flemish': 'Q7411', #just Dutch
    'French': 'Q150',
    'Latin' : 'Q397',
    'German': 'Q188',
    'Hebrew': 'Q9288',
    'English': 'Q1860',
    'Greek, Ancient (to 1453)' :'Q35497',
    'Italian' :'Q652'
}

outlist = {}
with open(filename, encoding="UTF-8") as fd:
    doc = xmltodict.parse(fd.read())
    album_name = [x['#text'] for x in doc['srw:searchRetrieveResponse']['srw:records']['srw:record'][0]['srw:recordData']['srw_dc:dc']['dcterms:isPartOf'] if '@dcx:recordIdentifier' in x][0]
    album_name = re.sub(r'(Album amicorum van )?(.+?);.+', r'\2', album_name).strip()
    album_code = "AA"+"".join(re.findall(r'[A-Z]', album_name))
    for i in range(len(doc['srw:searchRetrieveResponse']['srw:records']['srw:record'])):
        out = {}
        row = doc['srw:searchRetrieveResponse']['srw:records']['srw:record'][i]['srw:recordData']['srw_dc:dc']

        out['title']      = row['dc:title']['#text']
        out['date']       = re.sub(r'[\[\]]', '', row['dc:date']) if 'dc:date' in row else ""
        out['pagelist']   = [re.sub(r'.+\((.+?)\)', r'\1',
                  x['@dcx:anchorText']) for x in row['dc:identifier'] if x['@xsi:type'] == 'dcterms:URI' and '@dcx:anchorText' in x]
        out['images']     = [x['#text'] for x in row['dc:identifier'] if x['@xsi:type'] == 'dcterms:URI' and '@dcx:anchorText' in x]
        out['kbcatlinks'] = [x['#text'] for x in row['dc:identifier'] if x['@xsi:type'] == 'dcterms:URI' and '@dcx:anchorText' not in x][0]
        out['OCLC']       = [x['#text'] for x in row['dc:identifier'] if x['@xsi:type'] == 'OCLC'][0]
        out['shelfmark']  = [x['#text'] for x in row['dc:identifier'] if x['@xsi:type'] == 'shelfmark'][0]
        out['shelfmark']  = out['shelfmark'].replace('Den Haag, Koninklijke Bibliotheek : ', '')
        out['kbcatlinks'] = out['kbcatlinks'].replace("http://resolver.kb.nl/resolve?urn=PPN:", "")
        out['kbcatahidden'] = "https://opc-kb.oclc.org/DB=1/SET=1/TTL=1/PRS=PP/PPN?PPN="+out['kbcatlinks']
        out['kbcatlinks']   = "https://opc-kb.oclc.org/DB=1/PPN?PPN="+out['kbcatlinks']
        if 'dc:language' in row:
            out['lang'] = []
            for x in range(len(row['dc:language'])): 
                if '@xml:lang' in row['dc:language'][x] and row['dc:language'][x]['@xml:lang'] == 'en':
                    lang = row['dc:language'][x]['#text']
                    if lang in languages:
                        out['lang'].append(languages.get(lang))
                    else:
                        out['lang'].append(lang)
        if 'dcx:annotation' in row: 
            if not isinstance(row['dcx:annotation'], list):
                row['dcx:annotation'] = [row['dcx:annotation']]
            out['annotations']  = [x          for x in row['dcx:annotation'] if isinstance(x, str)] 
            out['annotations'] += [x['#text'] for x in row['dcx:annotation'] if isinstance(x, dict)]
            out['annotations'].reverse()
        out['creator'] = []
        if 'dc:creator' not in row:
            creator = {}
            creator['name'] = 'N. N.'
            out['creator'].append(creator)
        else:
            if not isinstance(row['dc:creator'], list):
                row['dc:creator'] = [row['dc:creator']]
            for dccreator in row['dc:creator']:
                creator = {}
                label = dccreator if isinstance(dccreator, str) else dccreator['#text']
                creator['name'] = re.sub(r'^([^\(,]+),?([^\(]*).*', r'\2 \1', label).replace('  ', ' ').strip()
                creator['isni'] = re.sub(r'.+\(ISNI (.+?)\)', r'\1', label) if re.match(r'.+\(ISNI .+?\)', label) else ""
                if re.match(r'.+?\(.*-.*\).*', label):
                    creator['birthyear'] = re.sub(r'.+?\((.*?)-.+', r'\1', label)
                    creator['deadyear']  = re.sub(r'.+?\(.*?-(.*?)\).*', r'\1', label)
                if '@dcx:recordIdentifier' in dccreator:
                    creator['nta']     = dccreator['@dcx:recordIdentifier'][3:] 
                    creator['nta-url'] = 'http://data.bibliotheken.nl/id/thes/p' + creator['nta']
                out['creator'].append(creator)
        outlist[out['pagelist'][0]] = out
#output to excel:

maxLenghts = {}
maxLenghts["creator"]     = max([len(outlist[page]["creator"])     for page in outlist])
maxLenghts["pagelist"]    = max([len(outlist[page]["pagelist"])    for page in outlist])
maxLenghts["images"]      = max([len(outlist[page]["images"])      for page in outlist])
maxLenghts["lang"]        = max([len(outlist[page]["lang"])        for page in outlist if "lang"        in outlist[page]])
maxLenghts["annotations"] = max([len(outlist[page]["annotations"]) for page in outlist if "annotations" in outlist[page]])

dfcolumns = ['volgnr', 'album_name', 'album_code','page', 'title', 'date', 'PPN kbcatlinks','PPN kbcatahidden',  'oclc', 'shelfmark']

for x in maxLenghts:
    if x == "creator":
        for y in range(maxLenghts[x]):
            dfcolumns += ['Label EN'+str(y+1), 'Label NL'+str(y+1), 'Des EN'+str(y+1), 'Des NL'+str(y+1), 'name'+str(y+1), 'birthyear'+str(y+1), 'deadyear'+str(y+1), 'nta'+str(y+1), 'nta-url'+str(y+1), 'isni'+str(y+1)]
    else:
        dfcolumns += [x+str(y+1) for y in range(maxLenghts[x])]
df = pd.DataFrame(columns=dfcolumns)
index = 1;
for page in sorted(outlist):
    row = outlist[page]
    volgnr = str(index).zfill(3)
    contribtuple = [volgnr,
        album_name,
        album_code,
        page,
        row.get('title'),
        row.get('date'),
        row.get('kbcatlinks'),
        row.get('kbcatahidden'),
        row.get('OCLC'),
        row.get('shelfmark')]
    for x in maxLenghts:
        for y in range(maxLenghts[x]):
            if x == 'creator':
                try:
                    contribtuple += [
                    album_code+"-"+volgnr+' Contribution of '+row[x][y].get('name'), 
                    album_code+"-"+volgnr+' Bijdrage van ' +  row[x][y].get('name'), 
                    'contribution of '+row[x][y].get('name')+' to album amicorum of '+album_name, 
                    'albumbijdrage van ' +  row[x][y].get('name')+' aan album amicorum van '+album_name, 
                    row[x][y].get('name'),
                    row[x][y].get('birthyear'),
                    row[x][y].get('deadyear'),
                    row[x][y].get('nta'),
                    row[x][y].get('nta-url'),
                    row[x][y].get('isni')]
                except IndexError as e:
                    contribtuple += ["","","","","","","","","",""]
            else:
                try:
                    contribtuple.append(row[x][y])
                except (IndexError,KeyError) as e:
                    contribtuple.append("")
    s = pd.Series(contribtuple, index=df.columns)
    df = df.append(s, ignore_index=True)
    index += 1
print(df)
df.to_excel("contributors-"+filename[:-4]+".xlsx")
