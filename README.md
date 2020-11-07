odmiana polskich imion 🇵🇱💁‍♀️💁‍♂️
=================

# Conversion scripts and csv/json files
collected that info to make people life easier in generating in automated way nicely personalized messages with proper declination of polish names.

## Repository structure:
* `data` - folder with various datasets
  * `output.csv` - nested csv with pandas-friendly encoding of declination in both Latin/Polish forms,
  * `output_wide.csv` - wide csv with pandas-friendly encoding of declination in both Latin/Polish forms,
  * `output.json` - json with raw declination dictionary in both Latin/Polish forms,
  * `missings_wide.csv` - wide csv with pandas-friendly encoding of missing declination in both Latin/Polish forms (it would be nice to fill these gaps), 
* `utils` - folder with support functions
  * `save_files.py` - code for saving scrapers' output appropriately
* `scraper.py` - Python file with websites' scraping code, 
* `changelog.md` - Markdown file with list of changes to repository, 
* `README.md` - readme file with repository description.

## References:
- [Wikipedia Dictionary of Polish Names](https://pl.wiktionary.org/wiki/Indeks:Polski_-_Imiona) (as well as following name pages), 
- [Wikipedia on: Polish declension of nouns](https://en.wikipedia.org/wiki/Polish_grammar#Declension), 
- [Imiona.info](http://www.imiona.info), 
- [Polish Grammar: Case](https://www.youtube.com/watch?v=33FdP6q1D-c).

