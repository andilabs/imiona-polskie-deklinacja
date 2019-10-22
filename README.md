odmiana polskich imion 🇵🇱💁‍♀️💁‍♂️
=================

# csv file
collected that info to make people life easier in generating in automated way nicely personalized messages with proper declination of polish names.

### with following collumns:
`name,sex,declination_json`

* `name` - singular in nominativus (pl. Mianownik - kto co?)
* `sex` - sex (either `m` for male or `f` for female)
* `declination_json` - in double quotes

### example record:
`Andrzej,m,"{"nominativus": {"s": "Andrzej", "pl": "Andrzejowie"}, "genetivus": {"s": "Andrzeja", "pl": "Andrzej\u00f3w"}, "dativus": {"s": "Andrzejowi", "pl": "Andrzejom"}, "accusativus": {"s": "Andrzeja", "pl": "Andrzej\u00f3w"}, "instrumentalis": {"s": "Andrzejem", "pl": "Andrzejami"}, "locativus": {"s": "Andrzeju", "pl": "Andrzejach"}, "vocativus": {"s": "Andrzeju", "pl": "Andrzejowie"}}"`

### the json has following structure:
* for each of the cases (latin names) info about proper form for `s` singular and `pl` plural is provideed.
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
Reference:
[Wikipedia on: Polish declension of nouns](https://en.wikipedia.org/wiki/Polish_grammar#Declension), [Polish Grammar: Case](https://www.youtube.com/watch?v=33FdP6q1D-c)

