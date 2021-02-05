De KB catalogues kan bevraagd worden met jSRU via de API op kb.nl. We (@VDK) hebben een (Python)script geschreven om de gewenste gegevens van de albumbijdragen van een album amicorum in de catalogus te verkrijgen in een excel-bestand

## Stap 1: Installeer Python
Als je nog geen Python op je computer hebt geïnstalleerd dan doe je dat als volgt. (Heb je al wel Python geïnstalleerd, dan kan je deze stap overslaan):
* [Download Python](https://www.python.org/downloads/) en Installeer Python 
**Belangrijk**: In de setup is er een vinkje met de strekking “installeer voor alle gebruikers”, als die ontvinkt wordt kan dit geïnstalleerd worden zonder Administrator-rechten. De environment variabele wil je namelijk wél! 
* Open de Opdrachtprompt (Windows-knop + R, type “cmd” en druk op OK) 
* Navigeer naar de map met de python-bestanden met het commando "cd” (current directory), bijvoorbeeld cd C:\Users\Username\Documents\Scripts 
* Run het script extract-data2.py met het commando: python extract-data2.py 
De eerste paar keer zal je de volgende error een aantal keren tegenkomen: zoals ModuleNotFoundError: No module named 'chardet' 
Dit betekent dat een module nog geïnstalleerd moet worden, in dit geval “chardet”.
Dit doe je met het commando: pip install chardet 

## Stap 2: Gebruik het KB-catalogus-script extra-data2.py
* Download het KB-catalogus-script [extract-data2.py](https://github.com/KBNLwikimedia/Alba-Amicorum/blob/main/scripts/extract-data2.py)
* Voeg de juiste signatuur-code van het album amicorum in de volgende url in (zonder spaties) 
http://jsru.kb.nl/sru?version=1.2&operation=searchRetrieve&x-collection=GGC&query=(EuropeanaTravel AND 121C11)&recordSchema=dcx&startRecord=1&maximumRecords=1000  
* Na deze query komt er een xml-output in je browser; kopieer deze xml (met een notepas editor) en plaats het in de map waarin ook je extract-data2.py script staat. 
* Voer de bestandsnaam van dit xml-bestand in op regel 45 van het extract-data2.py script 
* Run het Python-script extract-data2.py en de data uit het xml-wordt omgezet in een excel-bestand. 
* Dit excel-bestand kan je gebruiken om de data uit de KB-catalogus in OpenRefine aan te vullen en te reconciliëren (how-to)
