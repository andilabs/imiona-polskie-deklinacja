import json
import pandas as pd

def save_names_files(raw_names_json, filepath, unknown_names=None, raw_json=True, df_nested=True, df_wide=True, df_wide_missings=True):
    if raw_json:
        filename = '{}/output.json'.format(filepath)
        with open(filename, 'w') as fp:
            json.dump(raw_names_json, fp)
        print('raw_json saved successfully to: {}'.format(filename))

    if df_nested:
        filename = '{}/output.csv'.format(filepath)
        desired_columns = ['name', 'sex', 'declination_json_pl', 'declination_json_lat']
        names_df = pd.DataFrame().from_dict(raw_names_json, orient='index').rename(
                columns={
                    'lat': 'declination_json_lat',
                    'pl': 'declination_json_pl'
                    }
                )
        names_df['name'] = names_df.index
        names_df.reset_index(level=0, inplace=True)
        names_df.drop(columns='index')
        names_df[desired_columns].to_csv(filename)
        print('df_nested saved successfully to: {}'.format(filename))

    if df_wide:
        filename = '{}/output_wide.csv'.format(filepath)
        temp_lang_cases = None
        for single_lang_column in ['declination_json_pl', 'declination_json_lat']:
            names_cases = names_df[single_lang_column].apply(pd.Series)
            temp_cases = None
            for single_column in names_cases:
                temp_df = names_cases[single_column].apply(pd.Series).reset_index().rename(
                    columns={
                    'index':'name_id'
                    }
                )
                singular, plural = [
                    temp_df[['name_id', 's']].rename(columns={'s':single_column}),
                    temp_df[['name_id', 'pl']].rename(columns={'pl':single_column})
                ] 
                singular['category'], plural['category'] = ['s', 'pl']
                joined_case_df = singular.append(plural)
                if temp_cases is None:
                    temp_cases = joined_case_df[[joined_case_df.columns[i] for i in [0,2,1]]]
                else:
                    temp_cases = pd.merge(
                        temp_cases,
                        joined_case_df,
                        on=['name_id', 'category'],
                        how='left'
                    )
            if temp_lang_cases is None:
                temp_lang_cases = temp_cases
            else:
                temp_lang_cases = pd.merge(
                    temp_lang_cases,
                    temp_cases,
                    on=['name_id', 'category'],
                    how='left'
                )

        names_df['name_id'] = names_df.index
        names_df_wide = pd.merge(
            names_df[['name', 'sex', 'name_id']],
            temp_lang_cases,
            on=['name_id'],
            how='left').drop(columns='name_id')
        names_df_wide = names_df_wide[~names_df_wide.isna().any(axis=1)].sort_values(
            ['sex', 'name', 'category'],
            ascending=[True, True, False]
            ).reset_index().drop(columns='index')
        names_df_wide.to_csv(filename)
        print('df_wide saved successfully to: {}'.format(filename))
        missings_wide = names_df_wide[names_df_wide.isna().any(axis=1)]

    if df_wide_missings and df_wide and unknown_names is not None:
        filename = '{}/missings_wide.csv'.format(filepath)
        
        missings_wide_female_row = missings_wide[missings_wide['sex'] == 'f'].head(1)
        missings_wide_male_row = missings_wide[missings_wide['sex'] == 'm'].head(1)

        for single_name in list(unknown_names.keys())[::-1]:
            if unknown_names[single_name]['sex'] == 'f':
                double_row = missings_wide_female_row
            else:
                double_row = missings_wide_male_row
            
            for indeks in range(0,2):
                if indeks == 0:
                    double_row['category'] = 's'
                else:
                    double_row['category'] = 'pl'
                double_row['name'] = single_name
                missings_wide = missings_wide.append(double_row)

        missings_wide = missings_wide.sort_values(
            ['sex', 'name', 'category'],
            ascending = [True, True, False]
            ).reset_index().drop(columns='index')
        missings_wide.to_csv(filename)
        print('df_wide_missings saved successfully to: {}'.format(filename))
    else:
        print('To save wide-formed missing names with this function, you have to provide unknown_names dictionary and set df_wide argument to True!')
