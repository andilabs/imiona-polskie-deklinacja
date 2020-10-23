odmiana polskich imion 🇵🇱💁‍♀️💁‍♂️
=================

# conversion scripts and csv/json files
collected that info to make people life easier in generating in automated way nicely personalized messages with proper declination of polish names.

## files structure:
* wiki_scraper.py - Python file with Wikipedia Dictionary scraping code, 
* output.csv - csv with double-quoted declintation in both Latin/Polish forms,
* output_pd.csv - csv with pandas-friendly encoding of declination in both Latin/Polish forms,
* output.json - json with raw declination dictionary in both Latin/Polish forms,
* output_missing.json - json with raw dictionary of names missing declination forms (it would be nice to fill these gaps).

### with following collumns:
`name,sex,declination_json,declination_json_pl`

* `name` - singular in nominativus (pl. Mianownik - kto co?)
* `sex` - sex (either `m` for male or `f` for female)
* `declination_json_pl` - in double quotes (Polish form)
* `declination_json_lat` - in double quotes (Latin form)


### example record:
`Andrzej,m,"{"nominativus": {"s": "Andrzej", "pl": "Andrzejowie"}, "genetivus": {"s": "Andrzeja", "pl": "Andrzej\u00f3w"}, "dativus": {"s": "Andrzejowi", "pl": "Andrzejom"}, "accusativus": {"s": "Andrzeja", "pl": "Andrzej\u00f3w"}, "instrumentalis": {"s": "Andrzejem", "pl": "Andrzejami"}, "locativus": {"s": "Andrzeju", "pl": "Andrzejach"}, "vocativus": {"s": "Andrzeju", "pl": "Andrzejowie"}}"`

### the Latin json has following structure:
* for each of the cases (latin names) info about proper form for `s` singular and `pl` plural is provided.
* cases:
    * `nominativus` - mianownik
    	* kto? co? (jest)	
    * `genetivus` - dopełniacz
    	* kogo? czego? (nie ma) 
    * `dativus` - celownik
    	* komu? czemu? (się przyglądam)	
    * `accusativus` - biernik
    	* kogo? co? (widzę)	
    * `instrumentalis` - narzędnik
    	* (z) kim? (z) czym? (idę)	
    * `locativus` - miejscownik
    	* (o) kim? (o) czym? (mówię)	
    * `vocativus` - wołacz
    	* zwrot do kogoś lub czegoś

```json
{
  "nominativus": {
    "s": "Andrzej",
    "pl": "Andrzejowie"
  },
  "genetivus": {
    "s": "Andrzeja",
    "pl": "Andrzejów"
  },
  "dativus": {
    "s": "Andrzejowi",
    "pl": "Andrzejom"
  },
  "accusativus": {
    "s": "Andrzeja",
    "pl": "Andrzejów"
  },
  "instrumentalis": {
    "s": "Andrzejem",
    "pl": "Andrzejami"
  },
  "locativus": {
    "s": "Andrzeju",
    "pl": "Andrzejach"
  },
  "vocativus": {
    "s": "Andrzeju",
    "pl": "Andrzejowie"
  }
}
```
### the Polish json has following structure:
* for each of the cases (Polish names) info about proper form for `s` singular and `pl` plural is provided.
* cases:
    * `mianownik` - kto? co? (jest)	
    * `dopełniacz` - kogo? czego? (nie ma) 
    * `celownik` - komu? czemu? (się przyglądam)	
    * `biernik` - kogo? co? (widzę)	
    * `narzędnik` - (z) kim? (z) czym? (idę)	
    * `miejscownik` - (o) kim? (o) czym? (mówię)	
    * `wołacz` - zwrot do kogoś lub czegoś

```json
{
  "mianownik": {
    "s": "Andrzej",
    "pl": "Andrzejowie"
  },
  "dopełniacz": {
    "s": "Andrzeja",
    "pl": "Andrzejów"
  },
  "celownik": {
    "s": "Andrzejowi",
    "pl": "Andrzejom"
  },
  "biernik": {
    "s": "Andrzeja",
    "pl": "Andrzejów"
  },
  "narzędnik": {
    "s": "Andrzejem",
    "pl": "Andrzejami"
  },
  "miejscownik": {
    "s": "Andrzeju",
    "pl": "Andrzejach"
  },
  "wołacz": {
    "s": "Andrzeju",
    "pl": "Andrzejowie"
  }
}
```

### references:
[Wikipedia Dictionary of Polish Names](https://pl.wiktionary.org/wiki/Indeks:Polski_-_Imiona) (as well as following name pages), [Wikipedia on: Polish declension of nouns](https://en.wikipedia.org/wiki/Polish_grammar#Declension), [Polish Grammar: Case](https://www.youtube.com/watch?v=33FdP6q1D-c)

