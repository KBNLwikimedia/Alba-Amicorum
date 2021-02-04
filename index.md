![Banner alba](/banners/AlbaAmicorumKB_BannerWikimedia_EN.jpg)

## Alba amicorum of the KB

We are currently collecting data of the alba amicorum of the KB and structuring them on wikidata. We have three main sources we collect these data from: the KB catalogue, our LOD platform data.bibliotheken.nl and Europeana. 

We als maintain project pages about our alba amicorum [on Wikidata](https://www.wikidata.org/wiki/Wikidata:WikiProject_Alba_amicorum_National_Library_of_the_Netherlands) and on [Wikimedia Commons](https://commons.wikimedia.org/wiki/Category:Alba_amicorum_from_Koninklijke_Bibliotheek)

### Pilot project AA Jacob Heyblocq
The initial pilot project is about the data and images from the [Album amicorum Jacob Heyblocq](alba/AA-Jacob-Heyblocq) 

### Phase 2: focus list of 10 alba amicorum
In the second phase we collect data and images from ten alba amicorum: general scripts, workflows and manuals are shared in this repository. The ten alba amicorum on Wikidata and a couple of other non-Github sites) 
1. [Hiskia van Harinxma toe Slooten](https://www.wikidata.org/wiki/Wikidata:WikiProject_Alba_amicorum_National_Library_of_the_Netherlands/Hiskia_van_Harinxma) (WD)
1. [Samuel Johannes van den Bergh](https://www.wikidata.org/wiki/Wikidata:WikiProject_Alba_amicorum_National_Library_of_the_Netherlands/Samuel_Johannes_van_den_Bergh) (WD)
1. [Petronella Moens](https://www.wikidata.org/wiki/Wikidata:WikiProject_Alba_amicorum_National_Library_of_the_Netherlands/Petronella_Moens) (WD)
1. [Jacoba Cornelia Bolten](https://www.wikidata.org/wiki/Wikidata:WikiProject_Alba_amicorum_National_Library_of_the_Netherlands/Jacoba_Cornelia_Bolten) (WD)
1. [Jacob Heyblocq](https://www.wikidata.org/wiki/Wikidata:WikiProject_Alba_amicorum_National_Library_of_the_Netherlands/Jacob_Heyblocq) (WD)
1. [Geertruida Bosboom-Toussaint](https://geheugen.delpher.nl/nl/geheugen/pages/collectie/Album+amicorum+A.L.G.+Bosboom-Toussaint,+1882) (geheugen.delpher.nl)
1. [Burchard Grossmann](https://www.europeana.eu/nl/search?page=1&view=grid&query=Burchard%20Grossmann) (Europeana)
1. [Ernst Brinck](https://www.europeana.eu/nl/search?page=1&view=grid&query=ernst%20brinck) (Europeana)
1. [Janus Dousa](https://digitalcollections.universiteitleiden.nl/view/item/882520#page/1/mode/1up) (University library Leiden)
1. tbd

#### Workflow for uploading data
Via the how-to link you can find more information on how to perform these actions. If you already know how to perform the actions and are just here to get the scripts and other files, please use the shortcut links. 

1. download data (XML) from KB catalogue via jSRU API and put into csv-file ([how-to](https://github.com/KBNLwikimedia/Alba-Amicorum/blob/main/AA%20howto%20Query%20KB%20catalogue))
    1. we created a script for that ([shortcut](https://github.com/KBNLwikimedia/Alba-Amicorum/blob/main/scripts/extract-data2.py)) 
1. clean up and reconcile data in OpenRefine ([how-to](https://github.com/KBNLwikimedia/Alba-Amicorum/blob/main/AA%20howto%20Cleanup%20Reconcile%20with%20OpenRefine.md)
1. upload data for a **complete album amicorum** to Wikidata [using this datamodel](https://www.wikidata.org/wiki/Wikidata:WikiProject_Alba_amicorum_National_Library_of_the_Netherlands/Datamodel) (how-to)
1. upload data for **contributions to alba amicorum** to Wikidata [using this datamodel](https://www.wikidata.org/wiki/Wikidata:WikiProject_Alba_amicorum_National_Library_of_the_Netherlands/Datamodel/Album_contribution) (how-to)
    1. OR schema in JSON for creating the contributions: upload straight to Wikidata via OpenRefine ([shortcut](https://github.com/KBNLwikimedia/Alba-Amicorum/blob/main/scripts/schema%20AA%20-%201%20-%20creation.json)) 
    1. OR schema in JSON for creating the main body of properties of the contribution: upload to Wikidata via Quickstatements ([shortcut](https://github.com/KBNLwikimedia/Alba-Amicorum/blob/main/scripts/schema%20AA%20-%202%20-%20main%20part.json))
    1. OR schema in JSON for creating the properties concerning the image(s) of an album contribution: upload via Quickstatements ([shortcut](https://github.com/KBNLwikimedia/Alba-Amicorum/blob/main/scripts/schema%20AA%20-%203%20-%20P4765.json))
1. (In progress, not finished): your copy right free image on your url (P4765) can be automatically uploaded to Wikimedia Commons
1. Upload data for **contributors** to an album amicorum (how-to)
    1. OR schema in JSON for creating a Wikidata item for the contributors (shortcut)
    1. OR schema for adding the main information to a Wikidata item of a contributor (schortcut)

[test](https://github.com/KBNLwikimedia/Alba-Amicorum/blob/main/AA%20timeline.html)
