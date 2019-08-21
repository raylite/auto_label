#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 16:57:36 2019

@author: ja18581
"""

import pandas as pd
from pathlib import Path
import sqlalchemy as db
import MySQLdb

def dev_load():
    
    
    data = pd.read_csv(Path('.', 'data', 'rct_0_0.csv'))
    print ('Data successfully loaded to database')
    data.dropna(subset=['PMID', 'Abstract', 'NCT_Number'], inplace=True)
    data['PMID'] = data['PMID'].astype('int64')
    #data = data[data['rct_balanced'] == True]
    print (data.shape)
    data = data[['PMID', 'Abstract']].sample(n=250)

    abstr = [{'pmid':content['PMID'], 'abstract':content['Abstract'], 'count':0} for idx, content in data.iterrows()]
    
    results = db_table_insert(abstr) 
    
    data.to_csv(Path('.', 'data', 'sample_rct.csv'), index = False)
    print ('Extraction from the table just written')
    
    return results
    
    

def prod_load():
    data = pd.read_csv(Path('.', 'data', 'sample_rct.csv'))
    data['PMID'] = data['PMID'].astype('int64')
    abstr = [{'pmid':content['PMID'], 'abstract':content['Abstract'], 'count':0} for idx, content in data.iterrows()]
    
    results = db_table_insert(abstr)
    
    return results

def db_table_insert(abstr):
    engine = db.create_engine('mysql://labelling_admin:p@55w0rd@127.0.0.1/label_db?charset=utf8mb4')
   
    metadata = db.MetaData()
    connection = engine.connect()
    
    abstract = db.Table('abstract', metadata, autoload=True, autoload_with=engine)
    
    try:
        with connection as conn:
            query = db.insert(abstract)
    
            ResultProxy = conn.execute(query,abstr)
            results = conn.execute(db.select([abstract])).fetchall()
    except Exception as e:
        print(f'A fatal error occured. Code: {e}')
    
    return results
    
    
if __name__=='__main__':
    
    load_option = input('Choose the platform to load data for (Development/Production): ')
    option = False
    
    while not option:
        if load_option.lower() == 'p':
            test_result = prod_load()
            option = True
        elif load_option.lower() == 'd':
            test_result = dev_load()
        else:
            print('Please inpur the right deployment platform option')
            
    df = pd.DataFrame(test_result)
    df.columns = test_result[0].keys()
    print(df.head(4))
    
    print('Create operation successful')