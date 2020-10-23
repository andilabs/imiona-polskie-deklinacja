from selenium import webdriver
import re
import time
from tqdm import tqdm
import Levenshtein
import logging
import numpy as np 
import json
import ast
import pandas as pd

### 0. do setup ###

def fill_in_list(r1, r2): 
    return list(map(str, np.round(np.arange(r1, r2+0.1, 0.1),2)))

cases_in_latin = {
    'mianownik': 'nominativus',
    'dopełniacz': 'genetivus',
    'celownik': 'dativus',
    'biernik': 'accusativus',
    'narzędnik': 'instrumentalis',
    'miejscownik': 'locativus',
    'wołacz': 'vocativus'
}
names_url = 'https://pl.wiktionary.org/wiki/Indeks:Polski_-_Imiona'
names = {}

### 1. get name links from pl.wiktionary.org ###
driver = webdriver.Chrome()
driver.get(names_url)
# if link is about name, not sth else (e.g. special pages)
links = driver.find_elements_by_xpath("//ul//a[not(@accesskey) and contains(@href,'/w') and not(contains(@href, ':')) and not(contains(@href, '_'))]")
for single_link in tqdm(links):
    if single_link.text != '':
        if single_link.get_attribute('class') == '':
            names[single_link.text] = single_link.get_attribute('href')
        else:
            names[single_link.text] = None
    time.sleep(0.5)

### 2. get name cases ###
# multiple-gender names (e.g. Andrea / Maria) will occur only once, with the first appearing gender
for single_name in tqdm(names.keys()):
    # if entry for name exists
    if names[single_name] is not None:
        logging.warning('{} started'.format(single_name)) 
        cases_dict = {'sex': None, 'pl': None, 'lat': None}
        driver.get(names[single_name])
        time.sleep(1)
        meanings = driver.find_elements_by_css_selector('dd.lang-pl.fldt-znaczenia')
        table_of_interest, desired_meaning = [None, None]
        meanings_assignments = []
        # if meanings for a name occur
        if len(meanings) > 0:
            for single_meaning in meanings:
                desired_meaning_candidate = re.sub(r'\(|\)', '', single_meaning.text.split(' ')[0])
                meanings_assignments.append(desired_meaning_candidate)
                # if meaning is about a name; multiple-gender names (e.g. Andrea/Maria) will be assigned with first appearing gender
                if re.search('imię żeńskie', single_meaning.text) is not None:
                    desired_meaning = desired_meaning_candidate
                    cases_dict['sex'] = 'f'
                    break
                elif re.search('imię męskie', single_meaning.text) is not None:
                    desired_meaning = desired_meaning_candidate
                    cases_dict['sex'] = 'm'
                    break
            # figure out which table is about a name (on the basis of meanings and table assignments)
            meanings_table_assignments = driver.find_elements_by_css_selector('span.lang-pl.fldt-odmiana.term-lookup')
            table = driver.find_elements_by_css_selector('table.odmiana.lang-pl.fldt-odmiana')
            assignments_separated_final = []
            for single_assignment in meanings_table_assignments:
                single_assignment_replaced = re.sub(r'\(|\)', '', single_assignment.text)
                # if there are 2 main points with no subpoints
                if '.' not in single_assignment_replaced:
                    single_assignment_replaced = '{}.1'.format(single_assignment_replaced.replace('–', '.1,'))
                main_number = single_assignment_replaced.split('.')[0]
                # table assignments of meanings can be bound to multiple meanings with different main points 
                assignments_separated = single_assignment_replaced.split(',')
                for indeks in range(0, len(assignments_separated)):
                    single_separated = assignments_separated[indeks]
                    # if table assignments of meanings are incorrectly bound to multiple meanings with the same main point 
                    if single_separated not in meanings_assignments:
                        single_separated = '{}.{}'.format(main_number, single_separated)
                    # table assignments of meanings can be bound to multiple meanings with the same main point 
                    splitted_subnumbers = single_separated.split('–')
                    # reproduce table meaning main point on the basis of only subpoint
                    missing_numbers = []
                    for indeks2 in range(0, len(splitted_subnumbers)):
                        splitted_subnumbers[indeks2] = '{}.{}'.format(
                            main_number, 
                            splitted_subnumbers[indeks2].replace('{}.'.format(main_number), '')
                            )
                    assignments_separated[indeks] = splitted_subnumbers
                assignments_separated_flat = [item for sublist in assignments_separated for item in sublist]
                assignments_separated_final.append(assignments_separated_flat)
            assignments_separated_final_flat = [item for sublist in assignments_separated_final for item in sublist]
            for indeks in range(0, len(assignments_separated_final)):
                single_assignment = assignments_separated_final[indeks]
                # choose correctly name-based table on the basis of provided meanings
                if desired_meaning in single_assignment:
                    table_of_interest = indeks
                    break
                else:
                    # if there is bigger break between meanings (e.g. 1.1-4), we have to replicate every single one
                    if desired_meaning not in assignments_separated_final_flat:
                        for indeks_inside in range(0, len(single_assignment)):
                            if indeks_inside+1 < len(single_assignment):
                                if float(single_assignment[indeks_inside+1]) - float(single_assignment[indeks_inside]) > 0.1:
                                    single_assignment += fill_in_list(
                                        round(float(single_assignment[indeks_inside]),2),
                                        round(float(single_assignment[indeks_inside+1]),2)
                                        )
                        single_assignment_new = sorted(list(set(single_assignment)))
                        if desired_meaning in single_assignment_new:
                            table_of_interest = indeks
                            break
            # if meaning-suggested cases table exists 
            if table_of_interest is not None:
                # logging.warning('{} taking table: {}'.format(single_name, table_of_interest+1))
                table = driver.find_elements_by_css_selector('table.odmiana.lang-pl.fldt-odmiana')
                # if meaning-suggested cases table actually exists 
                if table_of_interest < len(table):
                    data_cells = table[table_of_interest].find_elements_by_css_selector('td.lang-pl.fldt-odmiana')
                    # if cases exist
                    if len(data_cells) > 0:
                        # if there are is any merged data row, remove it
                        if len(data_cells[-1].text.split(' ')) > 4:
                            del data_cells[-1]
                        # determine whether there is plural on the basis of cases placement
                        if data_cells[2].text == list(cases_in_latin.keys())[1]:
                            cases_range = 2
                        else: 
                            cases_range = 3
                        # there could be less than 7 cases, therefore len in range
                        temp_dict_pl, temp_dict_latin = [{}, {}]
                        for indeks in range(0, len(data_cells), cases_range):
                            single_row = data_cells[indeks:indeks+cases_range]
                            # if there are actual proper cases (and not any merged column)
                            if cases_range in [2, 3] and len(single_row) > 1:
                                single_case = single_row[0].text
                                # remove old versions of cases and leave only unicode letters
                                case_splitted = re.sub(r'[\W\d_]', '', single_row[1].text.split('/')[0])
                                # if there is anything before cased name itself, leave only cased name
                                case_splitted_spaced = ''.join(' '+x if x.isupper() else x for x in case_splitted).split(' ')
                                max_ratio_dict = {}
                                # determine what to leave on the basis of Levenshtein distance
                                for single_word in case_splitted_spaced:
                                    max_ratio_dict[single_word] = Levenshtein.ratio(single_name, single_word)
                                case_splitted = max(max_ratio_dict, key=max_ratio_dict.get)
                                temp_dict_pl[single_case], temp_dict_latin[cases_in_latin[single_case]] = [{'s': case_splitted},{'s': case_splitted}]
                                # if cases for plural form exist
                                if cases_range == 3:
                                    # remove old versions of cases and leave only unicode letters
                                    case_splitted = re.sub(r'[\W\d_]', '', single_row[2].text.split('/')[0])
                                    # if there is anything before cased name itself, leave only cased name
                                    case_splitted_spaced = ''.join(' '+x if x.isupper() else x for x in case_splitted).split(' ')
                                    max_ratio_dict = {}
                                    # determine what to leave on the basis of Levenshtein distance
                                    for single_word in case_splitted_spaced:
                                        max_ratio_dict[single_word] = Levenshtein.ratio(single_name, single_word)
                                    case_splitted = max(max_ratio_dict, key=max_ratio_dict.get)
                                    temp_dict_pl[single_case]['pl'], temp_dict_latin[cases_in_latin[single_case]]['pl'] = [case_splitted, case_splitted]
                                else:
                                    logging.warning('{} {} no plural cases exist'.format(single_name, single_case))
                                    temp_dict_pl[single_case]['pl'], temp_dict_latin[cases_in_latin[single_case]]['pl'] = [None, None]
                            else:
                                logging.warning('{} row of a merged column'.format(single_name))
                        cases_dict['pl'], cases_dict['lat'] = [temp_dict_pl, temp_dict_latin]
                    else:
                        logging.warning('{} no cases exist'.format(single_name))
                else:
                    logging.warning('{} no meaning-suggested name table actually exists'.format(single_name))
            else:
                # if meaning is not about a name (e.g. a place), it has no gender
                cases_dict['sex'] = None
                logging.warning('{} no meaning-suggested name table exists'.format(single_name))
            names[single_name] = cases_dict
        else:
            logging.warning('{} no name entry exists'.format(single_name)) 
    else:
        logging.warning('{} no name entry exists at all'.format(single_name))

### 4. do comparisons with previous version and separate missings ###

f = open("output.csv", "r")
pl_names = f.read().split('\n')
pl_names_full = {}
for single_name in pl_names[1:]:
    temp = single_name.split(',')
    replaced_dict = ''.join(temp[2:])[1:-1].replace('" "', '", "').replace('} ', '}, ').replace('null', '""')
    forms_dict = ast.literal_eval(replaced_dict)
    for single_key in forms_dict.keys():
        forms_dict[single_key] = forms_dict[single_key]['s']
    pl_names_full[temp[0]] = forms_dict

# see what names are missing from original file
list(set(list(pl_names_full.keys())) - set(list(names.keys())))

unknown_names = {}
for single_name in list(names):
    if names[single_name] in [None, 
    {'sex': None, 'pl': None, 'lat': None}, 
    {'sex': 'm', 'pl': None, 'lat': None}, 
    {'sex': 'f', 'pl': None, 'lat': None}] or 'http' in names[single_name]:
        unknown_names[single_name] = None
        del names[single_name]

### 5. save files ###
with open('output.json', 'w') as fp:
    json.dump(names, fp)

# conversion to nested csv
names_df = pd.DataFrame().from_dict(names, orient='index').rename(columns={'lat': 'declination_json_lat', 'pl': 'declination_json_pl'})
names_df['name'] = names_df.index
names_df.reset_index(level=0, inplace=True)
names_df = names_df.drop(columns='index')
names_df = names_df[['name', 'sex', 'declination_json_pl', 'declination_json_lat']]
names_df.to_csv('output_pd_nested.csv')

# conversion to unnested csv
temp_lang_cases = None
for single_lang_column in names_df.columns[-2:]:
    names_cases = names_df[single_lang_column].apply(pd.Series)
    temp_cases = None
    for single_column in names_cases:
        temp_df = names_cases[single_column].apply(pd.Series).reset_index().rename(columns={'index':'name_id'})
        singular = temp_df[['name_id', 's']].rename(columns={'s':single_column})
        singular['category'] = 's'
        plural = temp_df[['name_id', 'pl']].rename(columns={'pl':single_column})
        plural['category'] = 'pl'
        joined_case_df = singular.append(plural)
        if temp_cases is None:
            temp_cases = joined_case_df[[joined_case_df.columns[i] for i in [0,2,1]]]
        else:
            temp_cases = pd.merge(temp_cases, joined_case_df, on=['name_id', 'category'], how='left')
    if temp_lang_cases is None:
        temp_lang_cases = temp_cases
    else:
        temp_lang_cases = pd.merge(temp_lang_cases, temp_cases, on=['name_id', 'category'], how='left')

names_df['name_id'] = names_df.index
names_df_wide = pd.merge(names_df[['name', 'sex', 'name_id']], temp_lang_cases, on=['name_id'], how='left').drop(columns='name_id')
names_df_wide.to_csv('output_pd_wide.csv')

missings_wide = names_df_wide[names_df_wide.isna().any(axis=1)]
missings_wide_female_row = missings_wide[missings_wide['sex'] == 'f'].head(1)
missings_wide_male_row = missings_wide[missings_wide['sex'] == 'm'].head(1)

unknown_first_male_indeks = None
for single_indeks in range(0, len(list(unknown_names.keys()))):
    if list(unknown_names.keys())[single_indeks][0] == 'Ż' and list(unknown_names.keys())[single_indeks+1][0] == 'A':
        unknown_first_male_indeks = single_indeks+1
        break

unknown_females = list(unknown_names.keys())[0:unknown_first_male_indeks]
unknown_males = list(unknown_names.keys())[unknown_first_male_indeks:]

for single_name in unknown_females:
    for indeks in range(0,2):
        if indeks == 0:
            missings_wide_female_row['category'] = 's'
        else:
            missings_wide_female_row['category'] = 'pl'
        missings_wide_female_row['name'] = single_name
        missings_wide = missings_wide.append(missings_wide_female_row)

for single_name in unknown_males:
    for indeks in range(0,2):
        if indeks == 0:
            missings_wide_female_row['category'] = 's'
        else:
            missings_wide_female_row['category'] = 'pl'
        missings_wide_male_row['name'] = single_name
        missings_wide = missings_wide.append(missings_wide_male_row)

missings_wide = missings_wide.sort_values(['sex', 'name', 'category'], ascending = [True, True, False]).reset_index().drop(columns='index')
missings_wide.to_csv('missings_pd_wide.csv')

