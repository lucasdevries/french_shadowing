# Nieuw Frans transcript verwerken

Gebruik deze instructies wanneer er een nieuw `.txt` bestand in de map `transcripts/` is toegevoegd. De stappen maken drie afgeleide bestanden aan met exact dezelfde bestandsnaam (maar andere extensie of map).

---

## Vereisten

- Nieuw bestand staat in: `transcripts/<bestandsnaam>.txt`
- Doelmappen die al bestaan: `transcripts_cleaned/`, `transcripts_vertalingen/`, `woordenlijsten/`

---

## Stap 1 — Gecleand transcript (`transcripts_cleaned/`)

Lees het bronbestand volledig. Schrijf daarna een gecleand versie naar `transcripts_cleaned/<bestandsnaam>.txt` met deze regels:

**Structuur:**
- Elke zin staat op een eigen regel
- Tussen elke zin staat één lege regel
- Geen verdere opmaak

**Inhoudelijke correcties:**
- Splits grote blokken samenengevoegde tekst op in losse zinnen. Kijk naar de zinslengte van de rest van het bestand als maatstaf.
- Herstel foute hoofdletters na een punt (bijv. `". et"` → `". Et"` of nieuwe zin)
- Corrigeer duidelijke transcriptiefouten van de spraak-naar-tekst app. Voorbeelden uit eerdere bestanden:
  - `gris pain` → `grille-pain`
  - `hot` (als keukenapparaat) → `hotte`
  - `tronf` → `tronc`
  - `piétonfs` → `piétons`
  - `rembarbe` → `rambarde`
  - `l'air de jeu` → `l'aire de jeu`
  - `elles bat` → `elles battent`
  - `au bord d'œuf` → `au bord de quelque chose`
- Verwijder valse starts (bijv. `"Je me suis je suis"` → `"Je suis"`)
- De tekst blijft volledig in het Frans

---

## Stap 2 — Nederlandse vertaling (`transcripts_vertalingen/`)

Lees het gecleande bestand uit stap 1. Schrijf een vertaling naar `transcripts_vertalingen/<bestandsnaam>.txt` met deze regels:

- Identieke structuur als het gecleande bestand (elke zin op eigen regel, lege regel ertussen)
- Elke Franse zin wordt vervangen door een natuurlijke Nederlandse vertaling
- Geen Frans meer in het vertaalbestand
- Gebruik omgangstaal waar passend (de video's zijn informeel van toon)

---

## Stap 3 — Woordenlijst (`woordenlijsten/`)

### 3a. Woorden extraheren (Python-script)

Voer het volgende Python-script uit om alle unieke woorden te extraheren en op te slaan:

```python
import re, json

def extract_words(text):
    tokens = text.split()
    words = set()
    for token in tokens:
        token = re.sub(r'^[.,?!:;"\'«»—–;()\[\]/]+', '', token)
        token = re.sub(r'[.,?!:;"\'«»—–;()\[\]/]+$', '', token)
        token = token.lower()
        if not token or re.fullmatch(r'[\d\-.,/:]+', token):
            continue
        words.add(token)
    return sorted(words)

bestandsnaam = "VULDITHIERINMETNAAMZONDEREXTENSIE"
src = f"transcripts_cleaned/{bestandsnaam}.txt"

text = open(src, encoding='utf-8').read()
words = extract_words(text)
print(f"{len(words)} unieke woorden gevonden")
print(", ".join(words))
```

### 3b. Woorden vertalen en CSV schrijven

Gebruik de uitvoer van 3a als invoer. Schrijf een CSV naar `woordenlijsten/<bestandsnaam>.csv` met:

- Eerste regel: `nl,fr`
- Daarna per woord één regel: `nederlandsevertaling,franswoord`
- Volgorde: alfabetisch op het Franse woord (zoals de output van het script)
- Als een Nederlandse vertaling een komma bevat: zet die vertaling tussen dubbele aanhalingstekens
- Vertaal alle woorden, inclusief functiewoorden (`le` → `de`, `dans` → `in`) en vaste uitdrukkingen (`c'est` → `het is`, `j'ai` → `ik heb`, `il y a` → `er is`)

---

## Samenvatting uitvoer

Na het uitvoeren van alle stappen zijn er drie nieuwe bestanden:

| Map | Bestand | Inhoud |
|-----|---------|--------|
| `transcripts_cleaned/` | `<naam>.txt` | Gecorrigeerd Frans, één zin per regel |
| `transcripts_vertalingen/` | `<naam>.txt` | Nederlandse vertaling, zelfde structuur |
| `woordenlijsten/` | `<naam>.csv` | Woordenlijst met kolommen `nl,fr` |
