#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 16:57:24 2019

@author: ja18581
"""

from ast import literal_eval
import pandas as pd
from pathlib import Path

def merge_mltiple_labelling(data):
    #first reformat list items turned to string back to list
    data.loc[:, 'Screeners'] = data.loc[:, 'Screeners'].apply(literal_eval)
    data.loc[:, 'Target Sentences'] = data.loc[:, 'Target Sentences'].apply(literal_eval)
    data.loc[:, 'Target Clauses'] = data.loc[:, 'Target Clauses'].apply(literal_eval)
    
    #extraxt each mebe rof the list to individual columns
    ts = data['Target Sentences'].apply(pd.Series)
    tc = data['Target Clauses'].apply(pd.Series)
    #sc = data.Screeners.apply(pd.Series)
    
    data = ts.merge(data, right_index = True, left_index = True).drop(['Target Sentences'], axis = 1)
    data = tc.merge(data, right_index = True, left_index = True).drop(['Target Clauses'], axis = 1)
    return data


if __name__=='__main__':
    path = Path('.', 'output_1.csv')
    db_report = pd.read_csv(path, index_col=[0])
    reformatted_report = merge_mltiple_labelling(db_report)
    reformatted_report.to_csv('label_test_reprort.csv', index=False)