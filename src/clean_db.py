import pandas as pd
import numpy as np
import re
from sys import argv

import metadata_handler as mdh

'''
Take json file created by metadata_handler
Return cleaned dataframe for use in wildlife_id model
(cleaned dataframe contains many extra columns - drop as needed in model)
cmd terminal usage: clean_db.py <raw_database.json> <destination.csv>
'''

# Remove " ", "-", "/" from colunm names
def fix_col_names(db):

    dd = {}
    for col in db.columns:
        new_col = col
        new_col = new_col.replace(' ', '_')
        new_col = new_col.replace('-', '_')
        new_col = new_col.replace('/', '_')
        if new_col != col:
            dd[col] = new_col
    db = db.rename(columns = dd)
    return db

def _fix_date(date):
    #TODO: not working as intended
    date = str(date)
    if date == 'nan':
        return None
    else:
        return re.sub('(....)(..)(..)(..)', '\\1-\\2-\\3', date)

def _fix_time(time):
    #TODO: not working as intended
    time = str(time)
    if time == 'nan':
        return None
    elif len(time) == 7:
        return re.sub('(.)(..)(..)(..)', '\\1:\\2:\\3', time)
    else:
        return re.sub('(..)(..)(..)(..)', '\\1:\\2:\\3', time)


# vectorize above methods for better parallelization
def fix_date_and_time(db):
    fix_date = np.vectorize(_fix_date)
    fix_time = np.vectorize(_fix_time)

    db.date_created = fix_date(db.date_created)
    db.time_created = fix_time(db.time_created)
    return db


#  add dummies from keywords column
def add_dummies(db):
    db = pd.concat([db, db.keywords.str.join(sep = ' ')\
                            .str.get_dummies(sep=',')], axis=1)
    return db


def process_data(file_name):
    db = pd.read_json(file_name)
    db = fix_col_names(db)
    db = fix_date_and_time(db)
    db = add_dummies(db)

    return db

def create_csv(raw_json, dest_csv):
    df = process_data(raw_json)
    df.to_csv(dest_csv)
    return df

if __name__ == '__main__':

    create_csv(argv[1], argv[2])
