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
                        if len(data_cells) < 7:
                            logging.warning('{} incomplete cases'.format(single_name))
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

### 4. separate missings ###

sex = 'm'
unknown_names = {}
for single_indeks in range(len(list(names.keys()))-1, -1, -1):
    single_name = list(names.keys())[single_indeks]
    if single_name[0] == 'A' and list(names.keys())[single_indeks-1][0] == 'Ż' and sex == 'm':
        sex = 'f'
    
    if names[single_name] in [None, 
    {'sex': None, 'pl': None, 'lat': None}, 
    {'sex': 'm', 'pl': None, 'lat': None}, 
    {'sex': 'f', 'pl': None, 'lat': None}] or 'http' in names[single_name]:
        unknown_names[single_name] = {'sex': sex}
        del names[single_name]

unknown_names_to_delete = []
### 5. check missing names with another page ### 
driver = webdriver.Chrome()
for single_name in tqdm(unknown_names.keys()):
    which_to_take = None
    driver.get('http://www.imiona.info/odmiana_{}'.format(single_name))
    time.sleep(1)
    error_page = driver.find_elements_by_css_selector('.error-number')
    if len(error_page) == 0:
        desired_sex = unknown_names[single_name]['sex']
        cases_box = driver.find_elements_by_css_selector('.list-unstyled')
        if len(cases_box) > 0:
            page_sex = driver.find_elements_by_css_selector('.x_title')[0].text
            if (re.search('Imię żeńskie', page_sex) is not None and desired_sex == 'f') or (re.search('Imię męskie', page_sex) is not None and desired_sex == 'm'):
                which_to_take = 0
            elif len(cases_box) > 1:
                # there are more than one sexes - the one that interests us is second on the list
                which_to_take = 1
                logging.warning('{} second on the list'.format(single_name))
            else:
                # there is a sex mismatch, still take the first one and change previous sex
                which_to_take = 0
                new_sex = 'f'
                if desired_sex == 'f':
                    new_sex = 'm'                   
                unknown_names[single_name]['sex'] = desired_sex
                logging.warning('{} sex type mismatch, changed from {} to {}'.format(single_name, desired_sex, new_sex))
        else:
            which_to_take = ''
            logging.warning('{} no name entry exists'.format(single_name))
        if which_to_take not in [None, '']:
            cases = cases_box[0].find_elements_by_css_selector('.title')
            if len(cases) < 7:
                logging.warning('{} incomplete cases'.format(single_name)) 
            temp_dict = unknown_names[single_name]
            temp_dict['pl'], temp_dict['lat'] = [{}, {}]
            # there could be less than 7 cases, therefore len in range
            for single_indeks in range(0, len(cases)):
                temp_dict['pl'][list(cases_in_latin.keys())[single_indeks]],\
                    temp_dict['lat'][list(cases_in_latin.values())[single_indeks]] = [
                        {'s': cases[single_indeks].text, 'pl': None}, {'s': cases[single_indeks].text, 'pl': None}]
            names[single_name] = temp_dict
            unknown_names_to_delete.append(single_name)
            logging.warning('{} name found'.format(single_name))
        elif which_to_take is None:
            logging.warning('{} weird error'.format(single_name))
    else:
        logging.warning('{} no name entry exists at all'.format(single_name)) 

for single_key in unknown_names_to_delete:
    del unknown_names[single_key]

### 6. save files ###
from utils.save_files import save_names_files
save_names_files(names, './data', unknown_names)