#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 15:21:45 2019

@author: ja18581
"""

import click
from auto_label import db
from auto_label.models import Psentence, Nsentence, Pclause, Abstract
from sqlalchemy import exists
import pandas as pd
from pathlib import Path
import os

basedir = os.path.abspath(os.path.dirname(__file__))

def register(app):
    @app.cli.group()
    def dbprep():
        """Initial preparation and population of data to use into Abstract Table."""
       
        pass
    
    @dbprep.command()
    #@click.argument('tbl_name')
    def init():
        """Connect to a new database table
        check if its empty to populate or
        report if has content"""
        
        exist = db.session.query(exists().where(Abstract.count==0)).scalar()
        if exist:
            print(f'Table {Abstract.__table__} is not empty. You do not need to do anything further')
        else:
            print(f'Table {Abstract.__table__} is empty. Call load() to pre-load data')
        
        pass
    
    @dbprep.command()
    def populate():
        try:
            data = pd.read_csv(Path(basedir, 'data', 'rct_045.csv'))
            data.dropna(subset=['PMID', 'Abstract'], inplace=True)
            data['PMID'] = data['PMID'].astype('int64')
            data = data[['PMID', 'Abstract']].sample(n=50000)
            for idx, content in data.iterrows():
                abstr = Abstract(pmid=content['PMID'], abstract=content['Abstract'], count=0)
                db.session.add(abstr)
            db.session.commit()
            
            print ('Data successfully loaded to database')
        except:
            print('Data cannot be loaded. Check that the path data/rct_045.csv exists in project home')
    
    @dbprep.command()
    def wipeall():
        try:
            abs_rows_deleted = db.session.query(Abstract).delete()
            print (f'Abstract: {abs_rows_deleted} rows deleted')
            ps_rows_deleted = db.session.query(Psentence).delete()
            print (f'Abstract: {ps_rows_deleted} rows deleted')
            ns_rows_deleted = db.session.query(Nsentence).delete()
            print (f'Abstract: {ns_rows_deleted} rows deleted')
            cls_rows_deleted = db.session.query(Pclause).delete()
            print (f'Abstract: {cls_rows_deleted} rows deleted')
            db.session.commit()
        except:
            db.session.rollback()
        
