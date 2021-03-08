#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import csv
import time
import urllib.request
import datetime as dt
import xmltodict
import pandas as pd

LANGUAGES = {
    'Dutch; Flemish': 'Q7411', #just Dutch
    'French': 'Q150',
    'Latin' : 'Q397',
    'German': 'Q188',
    'Hebrew': 'Q9288',
    'English': 'Q1860',
    'Greek, Ancient (to 1453)' :'Q35497',
    'Italian' :'Q652'
}
MONTH_LABELS = {
    "01":{"jan.", "januari" },
    "02":{"feb.", "februari" , "febr."},
    "03":{"maa.", "maart"},
    "04":{"apr.", "april" },
    "05":{"mei"},
    "06":{"jun.", "juni"},
    "07":{"jul.", "juli"},
    "08":{"aug.", "augustus" },
    "09":{"sep.", "september", "sept."},
    "10":{"okt.", "oktober"},
    "11":{"nov.", "november" },
    "12":{"dec.", "december" }
}
def langToQID(lang):
    if lang in LANGUAGES:
        return LANGUAGES.get(lang)
    else:
        return lang

def date_format(date):
    date = date.strip()
    clean_date = {'stated_as' : date,
               'clean' : "unknown value",
               'ca' : "",
               'start' : "",
               'end' : ""};
    if date == "":
        clean_date['clean'] = ""
        return clean_date
    if date.find('?') != -1:
        clean_date['ca'] = 'Q18122778'
        date = date.replace('(?)','').replace('?','').strip()
    elif date.find('ca.') != -1:
        clean_date['ca'] = 'Q5727902'
        date = date.replace('ca.', '').replace('  ',' ').strip()
    if re.match(r'^1\d\d\d$', date):
        clean_date['clean'] = date
        return clean_date
    # voor 1687
    if re.match(r'^voor 1\d\d\d', date):
        clean_date['clean'] = re.sub(r'^voor (\d\d\d)\d', r'\1', date) + '0D'
        clean_date['end']   = re.sub(r'^voor (\d\d\d\d)', r'\1', date)
        return clean_date
    # 1666 of later
    if re.match(r'^1\d\d\d of later$', date):
        clean_date['clean'] = re.sub(r'^(\d\d\d)\d of later$', r'\1', date) + '0D'
        clean_date['start'] = re.sub(r'^(\d\d\d\d) of later$', r'\1', date)
        return clean_date
    # tussen 1849 en 1861 // tussen 1849 en 1863 // tussen 1849 en 1863
    if re.match(r'^tussen 1\d\d\d en 1\d\d\d$', date):
        clean_date['start'] = re.sub(r'^tussen (1\d\d\d).+', r'\1', date)
        clean_date['end']   = re.sub(r'^tussen \d{4} en (1\d\d\d)$',   r'\1', date)
        if int(clean_date['start'][-1]) > 7 and int(clean_date['end'][-1]) < 4 and int(clean_date['start'][0:3]) + 1 == int(clean_date['end'][0:3]) -1:
            clean_date['clean'] = str(int(clean_date['start'][0:3]) + 1) +'0D'
        else:
            clean_date['clean'] = str(int(clean_date['start'][0:2]) + 1) +'00C'
        return clean_date
    # 9/10 1661
    if re.match(r'^\d{1,2}\/\d{1,2} 1\d', date):
        clean_date['clean'] = re.sub(r'^(\d{1,2})\/\d{1,2} (1\d\d\d)$', r'\2-\1', date)
        clean_date['clean'] = dt.datetime.strptime(clean_date['clean'],"%Y-%m").strftime("%Y-%m") # zerofill date
        clean_date['ca']    = 'Q5727902'
        return clean_date
    
    for month in MONTH_LABELS:
        for mlabel in MONTH_LABELS[month]:
            if re.match(r'^\d{1,2} '+mlabel+ r' 1\d\d\d$', date):
                #12 dec. 1830 // 23 mei 1459 // 3 maart 1888
                clean_date['clean'] = re.sub(r'(\d{1,2}) '+mlabel + r' (1\d\d\d)', r'\2-'+ month+ r'-\1', date)
                clean_date['clean'] = dt.datetime.strptime(clean_date['clean'],"%Y-%m-%d").strftime("%Y-%m-%d") # zerofill date
            elif re.match(r'^'+mlabel+ r' 1\d\d\d$', date):
                #apr. 1848 // augustus 1765
                clean_date['clean'] = re.sub(r'^'+mlabel+ r' (1\d\d\d)', r'\1-'+ month, date)
    if clean_date['clean'] == 'unknown value' and date != 's.a':
        print("niet opgeschone datum:", clean_date['stated_as'])
    return clean_date
    
albums = {}
with open( 'dict.csv', 'r', encoding='UTF8' ) as file:
    reader = csv.reader(file, delimiter=';')
    for AA in reader:
        try:
            album_id = str(AA[0]).strip()
        except:
            print("GEEN VALIDE ID GEVONDEN IN dict.csv")
            continue
        print("gevonden id:", album_id)
        outrows = {}
        with urllib.request.urlopen("http://jsru.kb.nl/sru?query=(EuropeanaTravel%20AND%20"+album_id+")&recordSchema=dcx&startRecord=1&maximumRecords=1000&version=1.2&operation=searchRetrieve&x-collection=GGC") as xml:
            doc = xmltodict.parse(xml.read())
            if 'srw:records' in doc['srw:searchRetrieveResponse']:
                if not isinstance(doc['srw:searchRetrieveResponse']['srw:records']['srw:record'], list):
                    doc['srw:searchRetrieveResponse']['srw:records']['srw:record'] = [doc['srw:searchRetrieveResponse']['srw:records']['srw:record']]
                print("aantal regels:", len(doc['srw:searchRetrieveResponse']['srw:records']['srw:record']))
                for i in range(len(doc['srw:searchRetrieveResponse']['srw:records']['srw:record'])):
                    out = {}
                    row = doc['srw:searchRetrieveResponse']['srw:records']['srw:record'][i]['srw:recordData']['srw_dc:dc']
                    try:
                        out['album_name'] = [x['#text'] for x in row['dcterms:isPartOf'] if '@dcx:recordIdentifier' in x][0]
                    except IndexError as e:
                        out['album_name'] = "GEEN ALBUM NAAM GEVONDEN"
                        print("!!! Bijdrage zonder albumnaam gevonden")
                    out['album_name'] = re.sub(r'(Album amicorum van )?(.+?);.+', r'\2', out['album_name']).strip()
                    out['album_code'] = "AA"+"".join(re.findall(r'[A-Z]', out['album_name']))
                    
                    out['title']      = row['dc:title']['#text']
                    out['date']       = re.sub(r'[\[\]]', '', row['dc:date']) if 'dc:date' in row else ""
                    out['date']       = date_format(out['date'])
                    out['pagelist']   = [re.sub(r'.+\((.+?)\)', r'\1',
                              x['@dcx:anchorText']) for x in row['dc:identifier'] if x['@xsi:type'] == 'dcterms:URI' and '@dcx:anchorText' in x]
                    out['images']     = [x['#text'] for x in row['dc:identifier'] if x['@xsi:type'] == 'dcterms:URI' and '@dcx:anchorText' in x]
                    out['kbcatlinks'] = [x['#text'] for x in row['dc:identifier'] if x['@xsi:type'] == 'dcterms:URI' and '@dcx:anchorText' not in x][0]
                    out['OCLC']       = [x['#text'] for x in row['dc:identifier'] if x['@xsi:type'] == 'OCLC'][0]
                    out['shelfmark']  = [x['#text'] for x in row['dc:identifier'] if x['@xsi:type'] == 'shelfmark'][0]
                    out['shelfmark']  = out['shelfmark'].replace('Den Haag, Koninklijke Bibliotheek : ', '')
                    out['PPN'] = out['kbcatlinks'].replace("http://resolver.kb.nl/resolve?urn=PPN:", "")
                    if 'dc:language' in row:
                        out['lang'] = []
                        for x in range(len(row['dc:language'])): 
                            if '@xml:lang' in row['dc:language'][x] and row['dc:language'][x]['@xml:lang'] == 'en':
                                out['lang'].append(langToQID(row['dc:language'][x]['#text']))
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
                    outrows[out['pagelist'][0]] = out
            else:
                print('geen records gevonden')
        albums[album_id] = outrows
        time.sleep(4)
#output to excel:
writer = pd.ExcelWriter('contributions'+dt.datetime.utcnow().strftime('%Y-%m-%d_%H:%M')[:-3]+'.xlsx')  # pylint: disable=abstract-class-instantiated

for album_id in albums:
    album = albums[album_id]
    if album == {}:
        df = pd.DataFrame(columns=['Geen bijdragen gevonden'])
        df.to_excel(writer, sheet_name = album_id )
        continue
    maxLenghts = {}
    maxLenghts["creator"]     = max([len(album[page]["creator"])     for page in album])
    maxLenghts["pagelist"]    = max([len(album[page]["pagelist"])    for page in album])
    maxLenghts["images"]      = max([len(album[page]["images"])      for page in album])
    maxLenghts["lang"]        = max([len(album[page]["lang"])        for page in album if "lang"        in album[page]])
    maxLenghts["annotations"] = max([len(album[page]["annotations"]) for page in album if "annotations" in album[page]])

    dfcolumns = ['volgnr', 'album_name', 'album_code','page','Label EN', 'Label NL', 'Des EN', 'Des NL', 'title', 'date_stated_as', 'date_clean', 'date_ca', 'date_start','date_end', 'PPN kbcatlinks','PPN kbcatahidden',  'oclc', 'shelfmark']

    for x in maxLenghts:
        if x == "creator":
            for y in range(maxLenghts[x]):
                dfcolumns += [ 'name'+str(y+1), 'birthyear'+str(y+1), 'deadyear'+str(y+1), 'nta'+str(y+1), 'nta-url'+str(y+1), 'isni'+str(y+1)]
        elif x == 'pagelist':
            for y in range(maxLenghts[x]):
                dfcolumns += [ 'page'+str(y+1), 'title'+str(y+1)]
        else:
            dfcolumns += [x+str(y+1) for y in range(maxLenghts[x])]
    df = pd.DataFrame(columns=dfcolumns)
    index = 1;
    for page in sorted(album):
        row = album[page]
        volgnr = str(index).zfill(3)
        creators = ", ".join([x.get('name') for x in row['creator']])
        creators_en = re.sub(r'(.+), (.+)', r'\1 and \2', creators)
        creators_nl = re.sub(r'(.+), (.+)', r'\1 en \2', creators)
        contribtuple = [volgnr,
            row.get('album_name'),
            row.get('album_code'),
            page,
            row.get('album_code')+"-"+volgnr+' Contribution of '+creators_en, 
            row.get('album_code')+"-"+volgnr+' Bijdrage van ' +  creators_nl, 
            'contribution of '+ creators_en +' to album amicorum of '+row.get('album_name'), 
            'albumbijdrage van ' + creators_nl +' aan album amicorum van '+row.get('album_name'), 
            row.get('title'),
            row['date'].get('stated_as'),
            row['date'].get('clean'),
            row['date'].get('ca'),
            row['date'].get('start'),
            row['date'].get('end'),
            "https://opc-kb.oclc.org/DB=1/SET=1/TTL=1/PRS=PP/PPN?PPN="+row.get('PPN'),
            "https://opc-kb.oclc.org/DB=1/PPN?PPN="+row.get('PPN'),
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
                elif x == 'pagelist':
                    try:
                       contribtuple += [
                        row[x][y],
                        "Album amicorum of "+row.get('album_name')+" - "+creators_en+ " - " +album_id +"-" + row[x][y]
                       ] 
                    except (IndexError,KeyError) as e:
                        contribtuple += ["",""]
                else:
                    try:
                        contribtuple.append(row[x][y])
                    except (IndexError,KeyError) as e:
                        contribtuple.append("")
        s = pd.Series(contribtuple, index=df.columns)
        df = df.append(s, ignore_index=True)
        index += 1
    # print(df)
    df.to_excel(writer, sheet_name = album_id )
writer.save()
