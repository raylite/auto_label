#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 15:21:45 2019

@author: ja18581
"""

#import click
from auto_label import db
from auto_label.models import Psentence, Nsentence, Pclause, Abstract
from sqlalchemy import exists
import pandas as pd
from pathlib import Path
from flask import current_app, g
#from flask.cli import with_appcontext

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
        print (exist)
        if exist:
            print(f'Table {Abstract.__table__} is not empty. You do not need to do anything further')
        else:
            print(f'Table {Abstract.__table__} is empty. Call populate() to pre-load data')
        
        pass
    
    @dbprep.command()
    def populate():
        try:
            data = pd.read_csv(Path(current_app.config['DATA_FOLDER'], 'rct_45.csv'))
            print ('Data successfully loaded to database')
            data.dropna(subset=['PMID', 'Abstract'], inplace=True)
            data['PMID'] = data['PMID'].astype('int64')
            data = data[['PMID', 'Abstract']].sample(n=5)
            for idx, content in data.iterrows():
                print(f'CONTENT {content.PMID}; {content.Abstract}')
                abstr = Abstract(pmid=content['PMID'], abstract=content['Abstract'], count=0)
                print(f'ABSTRACT: {abstr.pmid}, {abstr.abstract}')
                db.session.add(abstr)
            db.session.commit()
            print('Successful committed to database')
            
        except Exception as e:
            print('Data cannot be loaded. Check that the path data/rct_045.csv exists in project home')
            db.session.rollback()
            print(f'Error committing. Error code/info: {str(e)}')
            
    
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
            print('Unable to delete tables')
        
