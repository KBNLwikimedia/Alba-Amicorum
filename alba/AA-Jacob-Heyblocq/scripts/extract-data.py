import os, os.path
import json
import requests
import re
import urllib
import numpy as np
import pandas as pd
from urllib.request import urlretrieve

#https://www.geeksforgeeks.org/counting-the-frequencies-in-a-list-using-dictionary-in-python/
def CountFrequency(my_list):
    # Creating an empty dictionary
    freq = {}
    pictures = ['Tekening', 'Gravure', 'Ets', 'Knipwerk']
    piccounter=0
    for item in my_list:
        if item in pictures:
           piccounter += 1
        if (item in freq):
            freq[item] += 1
        else:
            freq[item] = 1
    for key, value in freq.items():
        print("* % s : % s" % (key, value))

    #Tel het aantal afbeeldingen (pictures)
    print('Aantal afbeeldingen (= ' + str(pictures).replace('[','').replace(']','').replace("'",'') + ') in dit album = ' + str(piccounter))

    #download all album images to imagefolder
def imagedownload(imageurl):
    outputdirname="images"
    current_dir = os.path.dirname(os.path.realpath(__file__))
    outputdir=os.path.join(current_dir, outputdirname)
    os.chdir(outputdir)
    # download all files to disk
    localfilenumber = imageurl.split(':')[-1]
    #localfile_full = 'Beschrijving-' + 'maker-' + 'datum-' + 'plaats'+  ' - Album Amicorum Jacob Heyblocq - KB131H26_' + str(localfilenumber) + '.jpg' #AAJH_250#
    localfile_temp = 'Album Amicorum Jacob Heyblocq - KB131H26_' + str(localfilenumber) + '.jpg'  # AAJH_250#
    #print(localfile_temp)
    #urllib.request.urlretrieve(imageurl, localfile_temp)


# convert SRU-XML to JSON via https://www.oxygenxml.com/xml_json_converter.html
jsonfile="HiskiavanHarinxmathoeSlooten.json"
with open(jsonfile, encoding="UTF-8") as data_file:
    data = json.load(data_file)

formaten=[] #List all possible values of dc:terms:hasformat
talen=[] #List all possible languages of contributions
titles={} #Lit of all contribution titles
creatordictlist = {}  # list of creatordicts

creator_overall_dict = {}
identifiers = {}
for i in range(len(data["srw:searchRetrieveResponse"]["srw:records"]["srw:record"])):
    print('/'*10 + ' Record number ' + str(i) + ' ' + '/'*40) #i=0,1,2,3,4
    record = data["srw:searchRetrieveResponse"]["srw:records"]["srw:record"][i]["srw:recordData"]["srw_dc:dc"].items() #tuples
    insdict= dict((k, v) for k, v in record)# https://stackoverflow.com/questions/3783530/python-tuple-to-dict
    #print(insdict)
    keys=insdict.keys()
    for key in keys:
        value = insdict[key] #https://realpython.com/python-keyerror/
       #print(str(key) + ":" + str(value))

################Extract data from all <dc:identifier> fields ##############################
    # 1 Page number
    # 2 Resolver URL of image P18
    # 3 KB-cat resolver URL
    # 4 OCLC control number --> https://www.wikidata.org/wiki/Property:P243 --> https://www.worldcat.org/oclc/902911736
    identifier_dict = {}
    dcid = insdict.get('dc:identifier')
    #print('dcid = ' + str(dcid))

    #1 Pages number
    pagelist = [re.sub(r'.+\((.+?)\)', r'\1', x['dcx:anchorText']) for x in dcid if x['xsi:type'] == 'dcterms:URI']
    print('pages:', pagelist)
    identifier_dict['pages'] = pagelist

    #2 Resolver URL of image P18
    imagelinks = [x['#text'] for x in dcid if x['xsi:type'] == 'dcterms:URI']
    print('imagelinks:' ,imagelinks)
    identifier_dict['imagelinks'] = imagelinks

    identifier_dict['shelfmark'] = [x['#text'] for x in dcid if x['xsi:type'] == 'shelfmark'][0].replace('Den Haag, Koninklijke Bibliotheek : ', '')
    
    print("shelfmark", identifier_dict['shelfmark'])
    #for imageurl in imagelinks: #download the images
        #imagedownload(imageurl)
    #Compare last 3 digits of imageurl ('http://resolver.kb.nl/resolve?urn=EuropeanaTravel:131H26:250')
    # to page number ('250') - they MUST be the same!
         #if imageurl.split(':')[-1] == pagelist[0]: print('')
         #else: print("PROBLEM WITH PAGE NUMBERING!!!!!")
    #3 KB-cat resolver URL // can have more than one value (image 155)
    identifier_dict['kbcatlinks']  = insdict.get('dc:identifier#1').get("#text").replace("http://resolver.kb.nl/resolve?urn=PPN:", "")
    
    #4 OCLC control number --> https://www.wikidata.org/wiki/Property:P243 --> https://www.worldcat.org/oclc/902911736
    #Can have more than one value (image 155)

    # dcid = insdict.get('dc:identifier#2')
    # xsitypelist = [(x['xsi:type'], x['#text']) for x in dcid] # list of tuples
    
    identifier_dict['oclc']  = insdict.get('dc:identifier#2')[0].get("#text")


    # oclcids = [str(tuple[1]) for tuple in xsitypelist if str(tuple[0]) == 'OCLC'] #oclc id as string
    # print('oclc-id-P243:' + str(oclcids))
    # oclcurls = ['https://www.worldcat.org/oclc/' + str(oclcids[i]) for i in range(len(oclcids))]
    # print('oclc-urls:' + str(oclcurls))
    # identifier_dict['oclc'] = oclcids
    identifiers[pagelist[0]] = identifier_dict

################Extract data from all <dc:creator> fields #################################
    # 1 Name of creator/contributor --> P170 (creator) en P767 (contributor)
    # 2 NTA-id of creator --> P1006 --> http://data.bibliotheken.nl/id/thes/p098254065
    # 3 ISNI of creator --> P213 --> http://www.isni.org/0000000117452212
    # 4 Year of birth --> P569
    # 5 Year of death --> P570

    dccreator = insdict.get('dc:creator')
    #print('dccreator = ' + str(dccreator))
    #-------------------------------------
    #output can be
     ## None
        #1) creator = None
     ## String, or list of strings
       #2) creator = Rooy, C. de
       #3) creator = Pantogalos, Meletios (1596 - 1646) or creator = Junius, Wilhelmus (ca. 1633-)" or 'Quina jr., Jacob (-1699)' or 'Ens, Joannes (ca. 1623?-)'
     ##List
       #4) creator = ['Block, Tewis Dirckz.', 'Teunissen, Claes']
       #5) creator = ['Helst, Lodewijk van der (1642-ca. 1684)', 'Hals, Frans (ca. 1580-1666)']
       #6) creator = ['Cool, Joannes (-1680)', {'dcx:recordIdentifier': 'AC:069112894', 'content': 'Jacob Cats (1577-1660) (ISNI 0000 0001 0883 3136)'}]
     ## Dict
       #7) creator = {'dcx:recordIdentifier': 'AC:069966850', 'content': 'Johannes Cabeliau (1601-1657)'}
          # This number '069966850' --> http://opc4.kb.nl/DB=1/XMLPRS=Y/PPN?PPN=069966850 --> NTA
          # --> http://data.bibliotheken.nl/doc/thes/p069966850  --> WD P1006
       #8) creator = {"dcx:recordIdentifier": "AC:069430594","content": "Gulielmus d' Amour (ISNI 0000 0003 9604 2223)"}
       #9) creator = {'dcx:recordIdentifier': 'AC:069885532', 'content': 'Antonius Aemilius (1589-1660) (ISNI 0000 0000 6135 2561)'}
           # This number  ISNI 0000 0000 6135 2561 --> WD P213 -->  http://www.isni.org/0000+0000+6135+2561


    #-------------------------------------
    #-------------------------------------
    # creatordict['name']
    # creatordict['lifeyears']
    # creatordict['birthyear']
    # creatordict['birthyear_source']
    # creatordict['deadyear']
    # creatordict['deadyear_source']
    # -------
    # creatordict['nta']
    # creatordict['nta_source']
    # --------
    # creatordict['isni']
    # creatordict['isni_source']
    #-------------------------------------

    ## None
    # 1) creator = None
    if dccreator == None: # case 1
        creatordict = {}
        creatordict['name'] = 'N.N.'
        creatordictlist[pagelist[0]] = creatordict
    elif isinstance(dccreator, str): #creator is string, cases 2, 3
        ## String, or list of strings
        # 2) creator = Rooy, C. de
        # 3) creator = Pantogalos, Meletios (1596 - 1646) or creator = Junius, Wilhelmus (ca. 1633-)"
        # or 'Quina jr., Jacob (-1699)' or 'Ens, Joannes (ca. 1623?-)'
        
        creatordict = {}
        #Reverse first, last name and lifeyears . Hard case = Bronchorst, Jan Gerritsz. van (ca. 1603-1661)
        if ('(' in str(dccreator) and '-' in str(dccreator)) : # Case 2), creatorstring contains birth/death years)
            firstname = dccreator.split(", ")[1].split(" (")[0]
            lastname = dccreator.split(", ")[0]
            creatordict['name'] = firstname.strip() + ' ' + lastname.strip()
            lifeyears = dccreator.split(", ")[1].split(" (")[1].split(")")[0]
            creatordict['lifeyears'] = lifeyears.strip()
            birthyear = lifeyears.split("-")[0]
            creatordict['birthyear'] = birthyear.strip()
            deadyear =lifeyears.split("-")[1]
            creatordict['deadyear'] = deadyear.strip()
        else: #Case 3), no birth/death years
            creatordict['name'] = " ".join(dccreator.split(", ")[::-1]) # http://stackoverflow.com/questions/15704943/switch-lastname-firstname-to-firstname-lastname-inside-list
        creatordictlist[pagelist[0]] = creatordict

    elif isinstance(dccreator, list):  # creator is list, cases 4, 5 and 6
        ##List
        # 4) creator = ['Block, Tewis Dirckz.', 'Teunissen, Claes']
        # 5) creator = ['Helst, Lodewijk van der (1642-ca. 1684)', 'Hals, Frans (ca. 1580-1666)']
        # 5a) ["Arenbergh, Jan van (1628-voor 1670)", "N.N."]
        # 6) creator = ['Cool, Joannes (-1680)', {'dcx:recordIdentifier': 'AC:069112894', 'content': 'Jacob Cats (1577-1660) (ISNI 0000 0001 0883 3136)'}]
        for person in dccreator:
             creatordict = {}
             #print('person = '+str(person))
             if ('(' in str(person) and '-' in str(person)): # personstring contains birth/death years), cases 5 or 6
                if isinstance(person, dict): #case 6 # {'dcx:recordIdentifier': 'AC:069112894', 'content': 'Jacob Cats (1577-1660) (ISNI 0000 0001 0883 3136)'}
                    # NTA WD P1006
                    ntaid = person.get('dcx:recordIdentifier')
                    if 'AC:' in ntaid:
                        creatordict['nta'] = ntaid.split('AC:')[1].strip()
                        creatordict['nta-url'] = 'http://data.bibliotheken.nl/id/thes/p' + str(creatordict['nta'])
                    else:pass
                        #creatordict['nta'] = "Geen NTA-id gevonden"
                    # ISNI WD P213
                    personcontent = person.get('content') #Jacob Cats (1577-1660) (ISNI 0000 0001 0883 3136)
                    if personcontent != None and '(ISNI' in personcontent :
                        isni = personcontent.split('(ISNI ')[1].split(')')[0]
                        creatordict['isni'] = isni.strip()
                        creatordict['isni-url']  = 'http://www.isni.org/' + str(creatordict['isni'].replace(' ','+'))
                        #Name and lifeyears
                        personnameyears = personcontent.split('(ISNI ')[0] #Jacob Cats (1577-1660)
                        #name
                        personname=  personnameyears.split('(')[0] #Jacob Cats
                        creatordict['name'] = personname.strip()
                        #lifeyears, birthyear, deadyear
                        lifeyears = personnameyears.split("(")[1].split(")")[0]
                        creatordict['lifeyears'] = lifeyears.strip()
                        birthyear = lifeyears.split("-")[0]
                        creatordict['birthyear'] = birthyear.strip()
                        deadyear = lifeyears.split("-")[1]
                        creatordict['deadyear'] = deadyear.strip()
                    else:pass
                        #creatordict['isni'] = "Geen ISNI gevonden"

                elif isinstance(person, str): #case 5 'Helst, Lodewijk van der (1642-ca. 1684)
                    if ('(' in str(person) and '-' in str(person)):
                        firstname = person.split(", ")[1].split(" (")[0]
                        lastname = person.split(", ")[0]
                        creatordict['name'] = firstname.strip() + ' ' + lastname.strip()
                        lifeyears = person.split(", ")[1].split(" (")[1].split(")")[0]
                        creatordict['lifeyears'] = lifeyears.strip()
                        birthyear = lifeyears.split("-")[0]
                        creatordict['birthyear'] = birthyear.strip()
                        deadyear = lifeyears.split("-")[1]
                        creatordict['deadyear'] = deadyear.strip()
                        #print('AAAAAAA '+ str(creatordict))
                    else:  # Case 4), no birth/death years 'Block, Tewis Dirckz.'
                        creatordict['name'] = " ".join(person.split(", ")[::-1])
             else: #case 5a, the N.N. in ["Arenbergh, Jan van (1628-voor 1670)", "N.N."]
                 creatordict['name'] = "N.N."
             creatordictlist[pagelist[0]] = creatordict

    elif isinstance(dccreator, dict):  # creator is dict, case 7, 8 and 9
        #Dict
        # 7) creator = {'dcx:recordIdentifier': 'AC:069966850', 'content': 'Johannes Cabeliau (1601-1657)'}
        # 8) creator = {"dcx:recordIdentifier": "AC:069430594", 'content': "Gulielmus d' Amour (ISNI 0000 0003 9604 2223)"}
        # 9) creator = {'dcx:recordIdentifier': 'AC:069885532', 'content': 'Antonius Aemilius (1589-1660) (ISNI 0000 0000 6135 2561)'}
        creatordict = {}
        # NTA WD P1006
        ntaid = dccreator.get('dcx:recordIdentifier') #AC:069966850
        if 'AC:' in ntaid:
            creatordict['nta'] = ntaid.split('AC:')[1].strip()
            creatordict['nta-url'] = 'http://data.bibliotheken.nl/id/thes/p' + str(creatordict['nta'])
        else:pass
             #creatordict['nta'] = "Geen NTA-id gevonden"

        content = dccreator.get('#text')
        # 'Johannes Cabeliau (1601-1657)' or
        # 'Gulielmus d' Amour (ISNI 0000 0003 9604 2223)' or
        # 'Antonius Aemilius (1589-1660) (ISNI 0000 0000 6135 2561)'

        # ISNI WD P213
        if '(ISNI' in content: # 'Gulielmus d' Amour (ISNI 0000 0003 9604 2223)' or 'Antonius Aemilius (1589-1660) (ISNI 0000 0000 6135 2561)'
            isni = content.split('(ISNI ')[1].split(')')[0]
            creatordict['isni'] = isni.strip()
            creatordict['isni-url'] = 'http://www.isni.org/' + str(creatordict['isni'].replace(' ', '+'))

            nameyears = content.split('(ISNI ')[0] #Antonius Aemilius (1589-1660) or 'Gulielmus d' Amour'
            if ('(' in str(nameyears) and '-' in  str(nameyears)): #Antonius Aemilius (1589-1660)
                name = nameyears.split('(')[0]
                creatordict['name'] = name.strip()
                # lifeyears, birthyear, deadyear
                lifeyears = nameyears.split("(")[1].split(")")[0]
                creatordict['lifeyears'] = lifeyears.strip()
                birthyear = lifeyears.split("-")[0]
                creatordict['birthyear'] = birthyear.strip()
                deadyear = lifeyears.split("-")[1]
                creatordict['deadyear'] = deadyear.strip()
            else:   #'Gulielmus d' Amour'
                creatordict['name'] = nameyears.strip()
        else:#creatordict['isni'] = "Geen ISNI gevonden" #'Johannes Cabeliau (1601-1657)'
            pass

            if ('(' in str(content) and '-' in  str(content)): #'Johannes Cabeliau (1601-1657)'
                name = content.split('(')[0]
                creatordict['name'] = name.strip()
                # lifeyears, birthyear, deadyear
                lifeyears = content.split("(")[1].split(")")[0]
                creatordict['lifeyears'] = lifeyears.strip()
                birthyear = lifeyears.split("-")[0]
                creatordict['birthyear'] = birthyear.strip()
                deadyear = lifeyears.split("-")[1]
                creatordict['deadyear'] = deadyear.strip()
            else:   #'Gulielmus d' Amour'
                creatordict['name'] = content.strip()
        creatordictlist[pagelist[0]] = creatordict
    else: pass
        #creatordict = {}
        #creatordictlist = []  # list of creatordicts
    # print('creatordictlist= ' + str(creatordictlist))

    #TODO Create overall list (or dict or Pandas dataframe?) of all [creatordictlist] (including all N.N.s) to make Excel out of
    # First colum = pagenumber = pagelist[0]
    # Second = [creatordictlist]
    


################Extract data from all <dc:date> fields #################################
    # Date of contributions, can have more than 1 value per page (p 155)
    # record 237, 248 en 155 hebben elk 2 date-velden! en 2 bijdragers!!

    date = insdict.get('dc:date')
    date = re.sub(r'[\[\]]', '', str(date)) #https://stackoverflow.com/questions/44528081/remove-square-brackets-from-a-list-of-characters
    print('date of contribution:'+str(date))
    creatordictlist[pagelist[0]]['date'] = str(date)

################Extract data from all <dc:language> fields #################################
 # Language of textual contribution, in English, can have more than 1 value/language per page (p.223)
    # Case 1: No lang of contrib is provided, eg. when the contribution is an image without caption
    # Case 2: Lang is dict (contrib has one single language)
    # Case 3: Lang is list of dicts (contrib has multiple languages)
    dclanguage=insdict.get('dc:language')
    langlist = []
    #print(str(dclanguage))
    if dclanguage == None:  #Case 1: No lang of contrib is provided eg. when the contribution is an image without caption
        print('No language of contribution given, is it an captionless image?')
        talen.append(dclanguage)
    elif isinstance(dclanguage, dict): #Case 2: Lang is dict (contrib has one single language)
        lang = dclanguage.get('#text')
        print('language of contribution:' + str(lang))
        talen.append(lang)
        langlist = [lang]
    elif isinstance(dclanguage, list): #Case 3: Lang is list of dicts (contrib has multiple languages)
        langlist = [dclanguage[i].get('#text') for i in range(len(dclanguage)) if dclanguage[i].get('xml:lang') == 'en']
        print('languages of contribution:' + str(langlist))
        [talen.append(langlist[j]) for j in range(len(langlist))]
    else: print("GEEEEN TAAAAAAAAALLLL")
    creatordictlist[pagelist[0]]['langlist'] = langlist

#TODO
################## Extract data from all dcterms:hasFormat fields

    hasformat=insdict.get('dcterms:hasFormat') #can be None, dict or list of dicts
    #print('format of contribution:'+str(hasformat))

    if hasformat == None:  #Case 1: No hasformat is provided
        print('No format of contribution given')
        formaten.append(hasformat)
    elif isinstance(hasformat, dict): #Case 2: hasformat is dict (
        format = hasformat.get('#text')
        print('format of contribution:' + str(format))
        formaten.append(format)
    elif isinstance(hasformat, list): #Case 3: Lang is list of dicts (contrib has multiple languages)
        formatlist = [hasformat[i].get('#text') for i in range(len(hasformat))]
        print('format of contribution:' + str(formatlist))
        [formaten.append(formatlist[j]) for j in range(len(formatlist))]
    else: print("GEEEEN FORMAAATTT")

# TODO ################## Extract data from all dcterms:extent fields
    # We'll interpet this field to be the materials used for the contribution --> https://www.wikidata.org/wiki/Property:P186 'Material used'
    extent=insdict.get('dcterms:extent')
    # print('Material of contribution:'+str(extent).split(','))
    #Inkt (kleur: bruin, zwart, ..) ,
    # linnen,
    # mica,
    # houtskool?,
    # leer + goud (boekbanden)
    # nog toevoegen --> Jeroen om hulp vragen . Deze info staat niet in de catalogus, ergens anders wel?

# TODO ################## Extract data from all dc:title fields
    title= insdict.get('dc:title').get('#text')
    print('Titel of contribution:'+str(title))
    creatordictlist[pagelist[0]]['title'] = str(title)

    # As the standard titles are often not good for Wikidata (180 occurances of just 'Albuminscriptie'), we'll need to construct
    # an improved title : title + 'door' + contributor

# TODO ################## Extract data from all dc:subject fields

# TODO ################## Extract data from all dcx:annotation fields --> <dcx:annotation dcx:label="illustratievermelding">ill</dcx:an
    annotations = []
    dcxannotation = [insdict.get('dcx:annotation'), insdict.get('dcx:annotation#1'), insdict.get('dcx:annotation#2')]
    for x in dcxannotation:
        if x != None:
            if isinstance(x, str):
                annotations.append(x)
            elif isinstance(x, dict):
                annotations.append(x.get('#text'))
            elif isinstance(x, list):
                for y in x:
                    if isinstance(y, str):
                        annotations.append(y)
                    elif isinstance(y, dict):
                        annotations.append(y.get('#text'))
    annotations.reverse()
    creatordictlist[pagelist[0]]['annotations'] = annotations     

#TODO Make Excel exports of data so far, for further processing and OpenRefine --> look at smart servier work
# Make small, individual Excels, not make one large one for all data
# for instance, make Excels of
# 1) Contributors
# 2) ....
# 3)
# 4)




# Make Excels of contributors + Check against exsisting 'jacob-heyblocq-bijdragers.xlsx'
# List all contributors, sorted by page number
print('/'*100)
print('All contributors to album, sorted by page number:')
#https://stackoverflow.com/questions/9001509/how-can-i-sort-a-dictionary-by-key
unique_contributors={}
maxNumImages = max([len(identifiers[page]['imagelinks']) for page in identifiers])
maxNumLanglist = max([len(creatordictlist[page]['langlist']) for page in creatordictlist])
maxNumAnnotations = max([len(creatordictlist[page]['annotations']) for page in creatordictlist])
dfcolumns = ['page','name', 'birthyear', 'deadyear','nta','nta-url','isni','isni-url', 'title', 'date', 'PPN kbcatlinks', 'oclc', 'shelfmark']
for i in range(maxNumImages):
    dfcolumns.append("pagina_"+ str(i))
    dfcolumns.append("url_"+ str(i))
for i in range(maxNumLanglist):
    dfcolumns.append("lang"+ str(i))
for i in range(maxNumAnnotations):
    dfcolumns.append("annotation"+ str(i))
df = pd.DataFrame(columns=dfcolumns)
for page in sorted(creatordictlist):
    row = creatordictlist[page]
    contribtuple= [page,
        row.get('name'),
        row.get('birthyear'),
        row.get('deadyear'),
        row.get('nta'),
        row.get('nta-url'),
        row.get('isni'),
        row.get('isni-url'),
        row.get('title'),
        row.get('date'),
        identifiers[page]['kbcatlinks'],
        identifiers[page]['oclc'],
        identifiers[page]['shelfmark']
        ]
    for j in range(len(identifiers[page]['imagelinks'])):
        contribtuple.append(identifiers[page]['pages'][j])
        contribtuple.append(identifiers[page]['imagelinks'][j])
    for k in range(2*(maxNumImages - len(identifiers[page]['imagelinks']))):
        contribtuple.append('')
    for j in range(len(row.get('langlist'))):
        contribtuple.append(row.get('langlist')[j])
    for k in range(maxNumLanglist - len(row.get('langlist'))):
        contribtuple.append('')
    for j in range(len(row.get('annotations'))):
        contribtuple.append(row.get('annotations')[j])
    for k in range(maxNumAnnotations - len(row.get('annotations'))):
        contribtuple.append('')

    #https://stackoverflow.com/questions/53500735/appending-a-list-as-dataframe-row
    s = pd.Series(contribtuple, index=df.columns)
    df = df.append(s, ignore_index=True)

        # Lijst met unieke bijdragers en de pagina's waaraan ze bijdroegen:
        # #Moet worden: unique_contributors={'Jacob van der Does' : ['291','297','298'], }
        #unique_contributors = set(row.values())
        #print(unique_contributors)#[naam] = pagelist

print(df)
df.to_excel("contributors-"+jsonfile[:-5]+".xlsx")



    #if dictiter >1 :
    #    print('XXXXXXXX LET OP: Aan pagina ' + str(key) + ' hebben meerdere personen bijgedragen')

#print(unique_contributors)


################## Extract data from all dcterms:isPartOf fields
# We will omit this one, as it always  <dcterms:isPartOf dcx:recordIdentifier="AC:310919592">Album amicorum van J. Heyblocq...

print('/'*100)
# Aggregates lists
print('-' * 100)
#print('List (and numbers) of distinct types of contribution formats')
#CountFrequency(formaten)
#print('-' * 100)
#print('List (and numbers) of languages of contributions')
#CountFrequency(talen)
#print('-' * 100)
#print('List (and numbers) of titles of contributions')
#CountFrequency(titels)

