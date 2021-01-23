![Banner alba](/images/AlbaAmicorumKB_BannerWikimedia_EN.jpg)

## Alba amicorum of the KB

We are currently collecting data of the alba amicorum of the KB and structuring them on wikidata. We have three main sources we collect these data from: the KB catalogue, our LOD platform data.bibliotheken.nl and Europeana. 

### Pilot project AA Jacob Heyblocq
The initial pilot project is the data and images from the Album amicorum Jacob Heyblocq that currently [has its own repository](https://github.com/KBNLwikimedia/AlbumAmicorumJacobHeyblocq). 

### Phase 2: focus list of 10 alba amicorum
In the second phase we collect data and images from ten alba amicorum: general scripts, workflows and manuals are shared in this repository. 
1. [Hiskia van Harinxma toe Slooten](https://www.wikidata.org/wiki/Wikidata:WikiProject_Alba_amicorum_National_Library_of_the_Netherlands/Hiskia_van_Harinxma)
1. [Samuel Johannes van den Bergh](https://www.wikidata.org/wiki/Wikidata:WikiProject_Alba_amicorum_National_Library_of_the_Netherlands/Samuel_Johannes_van_den_Bergh)
1. [Petronella Moens](https://www.wikidata.org/wiki/Wikidata:WikiProject_Alba_amicorum_National_Library_of_the_Netherlands/Petronella_Moens)
1. [Jacoba Cornelia Bolten](https://www.wikidata.org/wiki/Wikidata:WikiProject_Alba_amicorum_National_Library_of_the_Netherlands/Jacoba_Cornelia_Bolten)
1. [Jacob Heyblocq](https://www.wikidata.org/wiki/Wikidata:WikiProject_Alba_amicorum_National_Library_of_the_Netherlands/Jacob_Heyblocq)
1. Geertruida Bosboom-Toussaint
1. Burchard Grossmann
1. Ernst Brinck
1. Janus Dousa

Workflow for uploading data
1. download data (XML) from KB catalogue via jSRU API and put into csv-file 
    1. we created a script for that
1. clean up and reconcile data in OpenRefine
1. upload data for a **complete album amicorum** to Wikidata
1. upload data for **contributions to alba amicorum** to Wikidata
    1. OR schema in JSON for creating the contributions (upload straight to Wikidata via OpenRefine)
    1. OR schema in JSON for creating the main body of properties of the contribution (upload to Wikidata via Quickstatements)
    1. OR schema in JSON for creating the properties concerning the image(s) of the album contributions to Wikidata
1. (In progress): your copy right free image on your url (P4765) can be automatically uploaded to Wikimedia Commons
1. Upload data for **contributors** to an album amicorum
