
# Datasets' examples
## output.json
`output.json` - JSON form of a Python dictionary with names cases

### cases have the following structure:
* for each of the cases info about proper form for `s` singular and `pl` plural is provided.
* cases:
    * `mianownik`/`nominativus`- kto? co? (jest)	
    * `dopełniacz`/`genetivus` - kogo? czego? (nie ma) 
    * `celownik`/`dativus` - komu? czemu? (się przyglądam)	
    * `biernik`/`accusativus` - kogo? co? (widzę)	
    * `narzędnik`/`instrumentalis` - (z) kim? (z) czym? (idę)	
    * `miejscownik`/`locativus` - (o) kim? (o) czym? (mówię)	
    * `wołacz`/`vocativus` - zwrot do kogoś lub czegoś

### JSON file header
```
{
    "Ada": {
        "sex": "f", 
        "pl": {
            "mianownik": {
                "s": "Ada", 
                "pl": "Ady"
                }, 
            "dope\u0142niacz": {
                "s": "Ady", 
                "pl": "Ad"
                }, 
            "celownik": {
                "s": "Adzie", 
                "pl": "Adom"
                }, 
            "biernik": {
                "s": "Ad\u0119", 
                "pl": "Ady"
                }, 
            "narz\u0119dnik": {
                "s": "Ad\u0105",
                "pl": "Adami"
                },
            "miejscownik": {
                "s": "Adzie", 
                "pl": "Adach"
                }, 
            "wo\u0142acz": {
                "s": "Ado",
                "pl": "Ady"
                }
            }, 
        "lat": {
            "nominativus": {
                "s": "Ada", 
                "pl": "Ady"
                }, 
            "genetivus": {
                    "s": "Ady", 
                    "pl": "Ad"
                }, 
            "dativus": {
                    "s": "Adzie", 
                    "pl": "Adom"
                }, 
            "accusativus": {
                    "s": "Ad\u0119",
                    "pl": "Ady"
                }, 
            "instrumentalis": {
                    "s": "Ad\u0105",
                    "pl": "Adami"
                }, 
            "locativus": {
                    "s": "Adzie", 
                    "pl": "Adach"
                }, 
            "vocativus": {
                    "s": "Ado",
                    "pl": "Ady"
                }
            }
    },
    (other names...)
}
```

## output.csv
`output.csv` - dataset with name cases enclosed in dictionaries

### Example record with header
- `name`: name singular form in nominativus/mianownik (kto? co?),
- `sex`: name-associated gender (`f` for female, `m` for male),
- `declination_json_pl`: double-quoted dictionary of cases for Polish case-form,
- `declination_json_lat`: double-quoted dictionary of cases for Latin case-form.
```
,name,sex,declination_json_pl,declination_json_lat
0,Ada,f,"{'mianownik': {'s': 'Ada', 'pl': 'Ady'}, 'dopełniacz': {'s': 'Ady', 'pl': 'Ad'}, 'celownik': {'s': 'Adzie', 'pl': 'Adom'}, 'biernik': {'s': 'Adę', 'pl': 'Ady'}, 'narzędnik': {'s': 'Adą', 'pl': 'Adami'}, 'miejscownik': {'s': 'Adzie', 'pl': 'Adach'}, 'wołacz': {'s': 'Ado', 'pl': 'Ady'}}","{'nominativus': {'s': 'Ada', 'pl': 'Ady'}, 'genetivus': {'s': 'Ady', 'pl': 'Ad'}, 'dativus': {'s': 'Adzie', 'pl': 'Adom'}, 'accusativus': {'s': 'Adę', 'pl': 'Ady'}, 'instrumentalis': {'s': 'Adą', 'pl': 'Adami'}, 'locativus': {'s': 'Adzie', 'pl': 'Adach'}, 'vocativus': {'s': 'Ado', 'pl': 'Ady'}}"
```

## output_wide.csv
`output_wide.csv` - wide-form of the above dataset (cases are spread across the dataset)

### Example record with header
- `name`/`sex`: same as above,
- `category`: indication whether name form is singular (`s` value) or plural (`pl` value),
- `mianownik`, `dopełniacz`, `celownik`, `biernik`, `narzędnik`,`miejscownik`, `wołacz`: particular cases,
- `nominativus`, `genetivus`,`dativus`,`accusativus`,`instrumentalis`,`locativus`,`vocativus`: particular cases.
```
,name,sex,category,mianownik,dopełniacz,celownik,biernik,narzędnik,miejscownik,wołacz,nominativus,genetivus,dativus,accusativus,instrumentalis,locativus,vocativus
0,Ada,f,s,Ada,Ady,Adzie,Adę,Adą,Adzie,Ado,Ada,Ady,Adzie,Adę,Adą,Adzie,Ado
```

## missings_wide.csv
`missings_wide.csv` - **missing-names only** wide-form of the `output.csv` dataset (empty cases are spread across the dataset to enable comfortable editing e.g. in Google Sheets)

### Example record with header
- `name`/`sex`: same as above,
- `category`: same as above,
- _(pl_cases)_: same as above,
- _(lat_cases)_: same as above.
```
,name,sex,category,mianownik,dopełniacz,celownik,biernik,narzędnik,miejscownik,wołacz,nominativus,genetivus,dativus,accusativus,instrumentalis,locativus,vocativus
0,Adamina,f,pl,,,,,,,,,,,,,,
```