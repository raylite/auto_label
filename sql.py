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

if __name__=='__main__':
    
    engine = db.create_engine('mysql://labelling_admin:p@55w0rd@127.0.0.1/label_db?charset=utf8mb4')
   
    metadata = db.MetaData()
    connection = engine.connect()
    
    abstract = db.Table('abstract', metadata, autoload=True, autoload_with=engine)
    
    data = pd.read_csv(Path('.', 'data', 'rct_45.csv'))
    print ('Data successfully loaded to database')
    data.dropna(subset=['PMID', 'Abstract'], inplace=True)
    data['PMID'] = data['PMID'].astype('int64')
    data = data[['PMID', 'Abstract']].sample(n=50000)

    abstr = [{'pmid':content['PMID'], 'abstract':content['Abstract'], 'count':0} for idx, content in data.iterrows()]
    try:
        with connection as conn:
            query = db.insert(abstract)
    
            ResultProxy = connection.execute(query,abstr)
            results = connection.execute(db.select([abstract])).fetchall()
    except Exception as e:
        print(f'A fatal error occured. Code: {e}')
        
    
    print ('Extraction from the table just written')
    
    df = pd.DataFrame(results)
    df.columns = results[0].keys()
    print(df.head(4))
    
    print('Create operation successful')