import re
import xmltodict
import pandas as pd

filename = "Heyblocq.xml"

outlist = {}
with open(filename, encoding="UTF-8") as fd:
    doc = xmltodict.parse(fd.read())
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
        if 'dc:language' in row:
            out['lang'] = [row['dc:language'][x]['#text'] for x in range(len(row['dc:language'])) if '@xml:lang' in row['dc:language'][x] 
                                                                           and row['dc:language'][x]['@xml:lang'] == 'en']
        if isinstance(row['dcx:annotation'], list):
            out['annotations']  = [x          for x in row['dcx:annotation'] if isinstance(x, str)] 
            out['annotations'] += [x['#text'] for x in row['dcx:annotation'] if isinstance(x, dict)]
        else:
            out['annotations']  = [row['dcx:annotation']["#text"]]
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
                if '@dcx:recordIdentifier' in dccreator:
                    creator['nta']     = dccreator['@dcx:recordIdentifier'][3:] 
                    creator['nta-url'] = 'http://data.bibliotheken.nl/id/thes/p' + creator['nta']
                if re.match(r'.+?\(.*-.*\).*', label):
                    creator['birthyear'] = re.sub(r'.+?\((.*?)-.+', r'\1', label)
                    creator['deadyear']  = re.sub(r'.+?\(.*?-(.*?)\).*', r'\1', label)
                out['creator'].append(creator)
        outlist[out['pagelist'][0]] = out
#output to excel:

maxLenghts = {}
maxLenghts["creator"]     = max([len(outlist[page]["creator"])     for page in outlist])
maxLenghts["pagelist"]    = max([len(outlist[page]["pagelist"])    for page in outlist if "pagelist" in outlist[page]])
maxLenghts["images"]      = max([len(outlist[page]["images"])      for page in outlist if "images"   in outlist[page]])
maxLenghts["lang"]        = max([len(outlist[page]["lang"])        for page in outlist if "lang"     in outlist[page]])
maxLenghts["annotations"] = max([len(outlist[page]["annotations"]) for page in outlist if "annotations" in outlist[page]])

dfcolumns = ['page', 'title', 'date', 'PPN kbcatlinks', 'oclc', 'shelfmark']

for x in maxLenghts:
    if x == "creator":
        for y in range(maxLenghts[x]):
            dfcolumns += ['name'+str(y+1), 'birthyear'+str(y+1), 'deadyear'+str(y+1), 'nta'+str(y+1), 'nta-url'+str(y+1), 'isni'+str(y+1)]
    else:
        dfcolumns += [x+str(y+1) for y in range(maxLenghts[x])]
df = pd.DataFrame(columns=dfcolumns)
for page in sorted(outlist):
    row = outlist[page]
    contribtuple = [page, 
        row.get('title'),
        row.get('date'),
        row.get('kbcatlinks'),
        row.get('OCLC'),
        row.get('shelfmark')]
    for x in maxLenghts:
        for y in range(maxLenghts[x]):
            if x == 'creator':
                try:
                    contribtuple += [
                    row[x][y].get('name'),
                    row[x][y].get('birthyear'),
                    row[x][y].get('deadyear'),
                    row[x][y].get('nta'),
                    row[x][y].get('nta-url'),
                    row[x][y].get('isni')]
                except IndexError as e:
                    contribtuple += ["","","","","",""]
            else:
                try:
                    contribtuple.append(row[x][y])
                except (IndexError,KeyError) as e:
                    contribtuple.append("")
    s = pd.Series(contribtuple, index=df.columns)
    df = df.append(s, ignore_index=True)
print(df)
df.to_excel("contributors-"+filename[:-4]+".xlsx")
