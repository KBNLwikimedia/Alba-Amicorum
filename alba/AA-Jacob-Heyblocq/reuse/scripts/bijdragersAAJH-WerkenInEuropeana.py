# Aim: Find works in Europeana by/from/about/related to the contributors to the Album amicorum Jacob Heyblocq

# Output of this script: https://github.com/KBNLwikimedia/Alba-Amicorum/blob/main/alba/AA-Jacob-Heyblocq/reuse/excels/AAJH-contributors-works-Europeana.xlsx

# Script is not fully finished and/or 100% reliable

# Last update dd 16-06-2021 by Olaf Janssen

# https://www.wikidata.org/wiki/Wikidata:WikiProject_Alba_amicorum_National_Library_of_the_Netherlands/Jacob_Heyblocq/Contributors#Europeana
# https://kbnlwikimedia.github.io/KBCollectionHighlights/stories/Cool%20new%20things%20you%20can%20now%20do%20with%20the%20KB's%20collection%20highlights/Part%205%2C%20Reuse.html (item 48)

######################################################################
import json
import requests
from googletrans import Translator
import pandas as pd
import openpyxl
import os

translator = Translator()  # Use Google Translate for translations from English into Dutch - https://pypi.org/project/googletrans/

eurapi_baseurl="https://www.europeana.eu/api"
eurdata_baseurl="http://data.europeana.eu"
eurapi_key="?wskey=apidemo"
eurapi2_key="?wskey=api2demo"

dcTypelist = []
dctermsIssuedlist = []
dcDatelist= []
dcCoveragelist=[]
dctermsTemporallist=[]
dctermsCreatedlist=[]
dctypes_allowed = ['tekening', 'grafiek','prent', 'etsen', 'handschrift','ornamentprent', 'graveren (drukprocedé)',
                    'prenttekening','pen','kostuumprent','boekillustratie','albumblad', 'doordruk', 'kleurendruk',
                    'schilderij', 'crayonmanier', 'roulette','droge naald','penseel','mezzotint','toonlithografie',
                    'lithografie','lithografie (techniek)','historieprent','aquatint','titelpagina', 'met de hand kleuren',
                    'kopergravure (prent)','Grafiek Drukwerk', 'Portretten','Portret','Aquarel', 'miniatuur',
                    'Monograph','print', 'etching','Painting','engraving','drawing','pen','Line etching','Miniatures',
                    'Miniature','text','counterproof', 'brush','drypoint', 'graphics', 'handwriting', 'ornament print',
                    'engraving (printing process)','print drawing', 'costume print','book illustration', 'album page',
                    'blow-through', 'color printing', 'crayon way', 'roulette', 'paintbrush', 'mezzotint', 'tone lithography',
                    'lithography', 'lithography (technique)', 'history print', 'aquatint', 'title page', 'coloring by hand',
                    'copper engraving (print)', 'Graphic Print', 'Portraits', 'Portrait', 'Watercolor']

# Setup empty Pandas Dataframe
contribs_works_df = pd.DataFrame(columns=[
'Contributor',
'ContributorLabel',
'EuropeanaAgentID',
'EuropeanaAgentJsonURL',
'EuropeanaAgentBioInfoEN',
'EuropeanaAgentBioInfoNL',
'EuropeanaAgentWorksJsonURL',
'WorkJsonURL',
'Title',
'Description',
'Creators',
'ThumbURL',
'ImageURL',
'Institution',
'NativeInterface',
'EuropeanaInterface',
'WorkSuitableForHackaLOD',
'Year',
'dctermsIssued',
'dcDate',
'dcCoverage',
'dctermsTemporal',
'dctermsCreated'
])

############ Wikidata: Retrieve AAJH contributors that have a Europeana ID P7704
wd_jsonurl = "https://query.wikidata.org/sparql?query=SELECT%20DISTINCT%20%3Fentity%20%3FentityLabel%20%3Fvalue%20%3FvalueLabel%20WHERE%20%7B%20%20%3Fentity%20wdt%3AP31%20wd%3AQ5%3Bwdt%3AP3919%20wd%3AQ72752496%20.%20%20%3Fentity%20wdt%3AP3919%20wd%3AQ72752496%20.%20%20%3Fentity%20p%3AP7704%20%3Fprop%20.%20OPTIONAL%20%7B%20%3Fprop%20ps%3AP7704%20%3Fvalue%20%7D%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22%5BAUTO_LANGUAGE%5D%2Cen%22.%20%7D%7D&format=json"
wdr = requests.get(wd_jsonurl)
wddata = json.loads(wdr.content) # utf-8, see https://stackoverflow.com/questions/44203397/python-requests-get-returns-improperly-decoded-text-instead-of-utf-8
wdcontribs = list(wddata['results']['bindings'])
#print(wdcontribs)
for c in wdcontribs: # [0:1]: #Iterate over AAJH contributors
    if c.get('entityLabel', 'aa') != 'aa':
        contributorLabel = c.get('entityLabel').get('value')
        print(' '*40)
        print(f"************* {contributorLabel.upper()} ************************")
        print(f"-- Info about this contributor from Wikidata --")
        print(f" * ContributorLabel: {contributorLabel}")
    if c.get('entity', 'aa') != 'aa':
        contributor = c.get('entity').get('value')
        print(f" * Contributor: {contributor}")
    if c.get('value', 'aa') != 'aa':
        euragent = c.get('value').get('value')
        print(f" * EuropeanaAgent: {euragent}")

########## Europeana: Retrieve data about this contributor from the Europeana API / json
    euragent_jsonurl=f"{eurapi_baseurl}/entities/{euragent}.json{eurapi_key}"
    euragentr = requests.get(euragent_jsonurl)
    euragentdata = json.loads(euragentr.content)
    if euragentdata.get('biographicalInformation', 'aa') != 'aa': #bio info is available from Europeana,
        biolist = euragentdata.get('biographicalInformation')
        biographicalInformationEN= [bio['@value'] for bio in biolist if bio['@language'] == 'en'][0] #Bio info in English is always present
        print(f"-- Info about this contributor from Europeana --")
        print(f" * euragent_jsonurl: {euragent_jsonurl}")
        print(f" * BiographicalInformationEN: {biographicalInformationEN}")
        #biographicalInformationNL = translator.translate(biographicalInformationEN, dest='nl')
        biographicalInformationNL = 'ToEnableInScript'
        #print(f"biographicalInformationNL (Google Translate): {biographicalInformationNL.text}")

########## Europeana: Retrieve works (books, poems, paintings..) from/by this contributor from the Europeana search API in json.
    # Maximum = 100 works, but pagination to the next 100 results is possible, see https://pro.europeana.eu/page/search#pagination
    # API docs: https://pro.europeana.eu/page/search
    # Europeana portal: https://www.europeana.eu/nl/collections/person/148386 --> 147 results
    # Europeana search API: https://www.europeana.eu/api/v2/search.json?wskey=api2demo&media=true&start=1&rows=100&profile=minimal&query=%22http://data.europeana.eu/agent/base/148386%22
    # --> also 147 results

    eurworks_jsonurl = f"{eurapi_baseurl}/v2/search.json{eurapi2_key}&media=true&start=1&rows=100&profile=minimal&query=%22{eurdata_baseurl}/{euragent}%22"
    print(f"-- Info about works by this contributor from Europeana --")
    print(f" * eurworks_jsonurl (max. 100 rows per page, see https://pro.europeana.eu/page/search#pagination): {eurworks_jsonurl}")
    eurworksr = requests.get(eurworks_jsonurl)
    eurworksdata = json.loads(eurworksr.content)
    items = eurworksdata['items']
    for item in items:
    # For each work (item/object) we want to retrieve the following fields

    # - Title of the work --> title
        if item.get('title', 'aa') != 'aa':
            # if wtitle is a list with 2 or more items, concat list items with "/" inbetween
            # https://stackoverflow.com/questions/12453580/how-to-concatenate-items-in-a-list-to-a-single-string
            wtitle = ' // '.join(item.get('title'))
            print(f" ----WORK: {wtitle} ----")
            print(f"   * Title: {wtitle}")
        else: wtitle =''
    # - Description of the work --> dcDescription
        if item.get('dcDescription', 'aa') != 'aa':
            wdescription = ' // '.join(item.get('dcDescription'))
            print(f"   * Description: {wdescription}")
        else: wdescription =''
    # - Creator(s) --> dcCreator
        if item.get('dcCreator', 'aa') != 'aa':
            wcreators = item.get('dcCreator')
            print(f"   * Creators: {wcreators}")
            # TODO - Creators: nog verder uitsplitsen -- Creators: ['Constantijn Huygens', 'http://data.europeana.eu/agent/base/147162']
        else: wcreators =''
    # - Date of creation --> year
        if item.get('year', 'aa') != 'aa':
            wyear = item.get('year')[0]
            print(f"   * Year created: {wyear}")
        else: wyear =''
    # - Thumb/Preview --> edmPreview
        if item.get('edmPreview', 'aa') != 'aa':
            wthumb = item.get('edmPreview')[0]
            print(f"   * Preview: {wthumb}")
        else: wthumb =''
    # - Full image ('.jpg') --> edmIsShownBy
        if item.get('edmIsShownBy', 'aa') != 'aa':
            wimage = item.get('edmIsShownBy')[0]
            print(f"   * Full image: {wimage}")
        else: wimage =''
    # - Institution/ data provider --> dataProvider
        if item.get('dataProvider', 'aa') != 'aa':
            winstitution = item.get('dataProvider')[0]
            print(f"   * Institution: {winstitution}")
        else: winstitution =''
    # - URL of work in native interface of institution --> edmIsShownAt
        if item.get('edmIsShownAt', 'aa') != 'aa':
            wnatinterface = item.get('edmIsShownAt')[0]
            print(f"   * Work in interface of {winstitution}: {wnatinterface}")
        else: wnatinterface =''
    # - URL of work in Europeana interface --> guid
        if item.get('guid', 'aa') != 'aa':
            weurinterface = item.get('guid')
            print(f"   * Work in Europeana: {weurinterface}")
        else: weurinterface =''

########## Europeana: Retrieve additional details from each work separately
    # 1) type of work (etching, painting, book, poem...)
    # 2) year of publication/creation/issuance/
    # 3) lat-long

    # - Json representation of the work --> link
        if item.get('link', 'aa') != 'aa':
            wjsonurl = item.get('link')
            print(f"   * Json representation URL of this work: {wjsonurl}")
            wr = requests.get(wjsonurl)
            workdata = json.loads(wr.content)
            work = workdata['object']
            print(f"   * Work dictionary: {work}")

            if work.get('proxies', 'aa') != 'aa':
                proxies=work.get('proxies')[0]
                print(f"   * Proxies: {proxies}")
                # 1) type of work (etching, painting, book, poem...) --> proxies/dctype
                if proxies.get('dcType', 'aa') != 'aa':
                   wdctype = proxies.get('dcType')
                   print(f"   * Type of work: {wdctype}")
                   # dcTypelist.append(wdctype)
                   # For HackaLOD purposes we want to filter the types of works/objects, based on (the value of) the dcType field
                   # For convenience/uncomplications we'll only use NL and EN as filter languages
                   # Allowed values of dcType for HackaLOD: see list 'dctypes_allowed' above
                   for allowtype in dctypes_allowed:
                        if str(allowtype).lower() in str(wdctype).lower():
                            suitableforHackaLOD = "True"
                            break
                        else:
                            suitableforHackaLOD = "False"
                   print(f"   * Object is of suitable type for HackaLOD: {suitableforHackaLOD}")
                else:
                    print(f"   * No dcType specified, object excluded for HackaLOD")
                    suitableforHackaLOD = "False"


                # 2) year of publication/issuance -->
                # a) proxies/dctermsIssued or
                # b) proxies/dcDate or
                # c) proxies/dcCoverage
                # d) dctermsTemporal
                # e) dctermsCreated

                if proxies.get('dctermsIssued', 'aa') != 'aa':
                    #dctermsIssued = proxies.get('dctermsIssued').get('def')[0]
                    # https://stackoverflow.com/questions/33709331/dictionary-get-value-without-knowing-the-key
                    dctermsIssued=list(proxies.get('dctermsIssued').values())[0][0]
                    if dctermsIssued.startswith('http://semium.org/time/'):
                        dctermsIssued = dctermsIssued.split('/time/')[1]
                    dctermsIssuedlist.append(dctermsIssued)
                    print(f"   * dctermsIssued: {dctermsIssued}")
                else: dctermsIssued = ''

                if proxies.get('dcDate', 'aa') != 'aa':
                    dcDate = list(proxies.get('dcDate').values())[0][0]
                    # Do some dates cleaning
                    if dcDate.startswith('http://semium.org/time/'):
                        dcDate = dcDate.split('/time/')[1]
                    if dcDate.startswith('geboorte\xa0'):
                        dcDate = dcDate.split('geboorte\xa0')[1]
                    if dcDate.startswith('\xa0'):
                        dcDate = dcDate.split('\xa0')[1]
                    dcDatelist.append(dcDate)
                    print(f"   * dcDate: {dcDate}")
                else: dcDate = ''

                if proxies.get('dcCoverage', 'aa') != 'aa':
                    dcCoverage = list(proxies.get('dcCoverage').values())[0][0]
                    dcCoveragelist.append(dcCoverage)
                    print(f"   * dcCoverage: {dcCoverage}")
                else: dcCoverage = ''

                if proxies.get('dctermsTemporal', 'aa') != 'aa':
                    dctermsTemporal = list(proxies.get('dctermsTemporal').values())[0][0]
                    dctermsTemporallist.append(dctermsTemporal)
                    print(f"   * dctermsTemporal: {dctermsTemporal}")
                else: dctermsTemporal = ''

                if proxies.get('dctermsCreated', 'aa') != 'aa':
                    dctermsCreated = list(proxies.get('dctermsCreated').values())[0][0]
                    dctermsCreatedlist.append(dctermsCreated)
                    print(f"   * dctermsCreated: {dctermsCreated}")
                else: dctermsCreated = ''


                # 3) TODO Places and lat-long
        else: wjsonurl =''

        # Create 1 row in dataframe
        df_row = {
         'Contributor' : contributor ,
         'ContributorLabel' : contributorLabel ,
         'EuropeanaAgentID' : euragent ,
         'EuropeanaAgentJsonURL' : euragent_jsonurl,
         'EuropeanaAgentBioInfoEN' : biographicalInformationEN,
         'EuropeanaAgentBioInfoNL' : biographicalInformationNL,
         'EuropeanaAgentWorksJsonURL': eurworks_jsonurl,
         'WorkJsonURL': wjsonurl,
         'Title' : wtitle,
         'Description' : wdescription,
         'Creators' : wcreators,
         'ThumbURL' : wthumb,
         'ImageURL' : wimage,
         'Institution' : winstitution,
         'NativeInterface' : wnatinterface,
         'EuropeanaInterface' : weurinterface,
         'WorkSuitableForHackaLOD' : suitableforHackaLOD,
         'Year' : wyear,
         'dctermsIssued' : dctermsIssued,
         'dcDate' : dcDate,
         'dcCoverage' : dcCoverage,
         'dctermsTemporal' : dctermsTemporal,
         'dctermsCreated' : dctermsCreated
        }

        print(f"   * Dataframe row: {str(df_row)}")
        # add row to df
        contribs_works_df = contribs_works_df.append(df_row, ignore_index = True)

print(contribs_works_df)
# Export df tot Excel
file_name = '../excels/AAJH-contributors-works-Europeana.xlsx'
contribs_works_df.to_excel(file_name, index = True, header=True, sheet_name='AAJHContributors-Works')

print(' '*40)
print(f"* dcTypelist: {dcTypelist}")
print(' ' * 40)
print(f"* dctermsIssuedlist: {dctermsIssuedlist}")
print(' ' * 40)
print(f"* dcDatelist: {dcDatelist}")
print(' ' * 40)
print(f"* dcCoveragelist: {dcCoveragelist}")
print(' ' * 40)
print(f"* dctermsTemporallist: {dctermsTemporallist}")
print(' ' * 40)
print(f"* dctermsCreatedlist: {dctermsCreatedlist}")
