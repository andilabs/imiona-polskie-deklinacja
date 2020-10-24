# v1.2
## Added 
- submitted changelog file `changelog.md`

## Changed
- improved checking of `output.csv` file
- improved generation of empty rows in `missings_pd_wide.csv` file

## Fixed
- fixed doubled category for male names in `missings_pd_wide.csv`

# v1.1
## Added
- submitted Python source code for scraper
- created other dataset files for easier usage

## Changed
- updated corpus with actual Wiktionary pages and extended it with 30 new names
- temporairly removed 24 shady names from main corpus for completeness:
  - missing cases: `Henrieta`, 
  - name is uncaseable: `Rut`,
  - no Polish cases available: `Milena, Romana, Donald, Zoja, Leo, Herakles, Pamela, Norman, Rebeka, Marianna, Gizela, Blanka, Marta, Iwon`
  - word is not a name (e.g. a city, a river): `Kama, Samara, Jana, Borysław, Ilia, Inka`
  - corner-cases of the above: `Minerwa, Sławek`

## Fixed
- improved 10 names:
  - wrong plural form: `Diana, Flora, Hestia, Iryda, Kasandra, Luna, Achilles, Kastor, Lew, Syriusz`

# v1.0
## Added
- contributed raw files with names