De KB catalogues kan bevraagd worden met jSRU via de API op kb.nl. We (@VDK) hebben een (Python)script geschreven om de gewenste gegevens van de albumbijdragen van een album amicorum in de catalogus te verkrijgen in een excel-bestand

## Stap 1: Installeer Python
Als je nog geen Python op je computer hebt geïnstalleerd dan doe je dat als volgt. (Heb je al wel Python geïnstalleerd, dan kan je deze stap overslaan):
* Download Python
* Installeer Python 
Belangrijk: In de setup is er een vinkje met de strekking “installeer voor alle gebruikers”, als die ontvinkt wordt kan dit geïnstalleerd worden zonder Administrator-rechten. De environment variabele wil je wél. 
* Open de Opdrachtprompt (Windows-knop + R, type “cmd”, en druk op OK) 
* Navigeer naar de map met de python-bestanden met het commando "cd” (current directory), bijvoorbeeld cd C:\Users\Username\Documents\Scripts 
* Run het script extract-data2.py met het commando: python extract-data.py 
De eerste paar keer zal je de volgende error een aantal keren tegenkomen: zoals ModuleNotFoundError: No module named 'chardet' 
Dit betekent dat een module nog geïnstalleerd moet worden, in dit geval “chardet”.  
Dit doe je met het commando: pip install chardet 

## Stap 2:
* Download het KB-catalogus-script [extract-data2.py](https://github.com/KBNLwikimedia/Alba-Amicorum/blob/main/scripts/extract-data2.py)
* Voeg de signatuur-code van het album amicorum in de url in (zonder spaties) 
* http://jsru.kb.nl/sru?version=1.2&operation=searchRetrieve&x-collection=GGC&query=(EuropeanaTravel AND 121C11)&recordSchema=dcx&startRecord=1&maximumRecords=1000  

