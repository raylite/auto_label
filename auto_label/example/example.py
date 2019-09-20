#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 17:37:09 2019

@author: ja18581
"""
import os
import random
from pathlib import Path

from auto_label import db
from flask import render_template, url_for, redirect, session, current_app
import pandas as pd

from auto_label.example import bp
from auto_label.example.forms import ArticleForm, PublicationsForm, SubmitForm, MoreForm, CloseForm
from auto_label.login_required import login_required

from utilities.custom_tokenizer import sentence_tokenizer #local tokenizer



@bp.route('/practice/', methods=['GET','POST'])
@login_required(1)
def sample():
    sample_file_path = os.path.join(current_app.config['DATA_DIR'], 
                                        random.choice(os.listdir(Path(current_app.config['DATA_DIR']))))
    session['sample_file'] = sample_file_path
    
    abstract = pd.read_csv(sample_file_path)
    print (abstract)
    
    pub_form = PublicationsForm()
    submit_form = SubmitForm()
    
    
    pub_form.title.data = 'Publications List'
    
    abstracts = []
    
    for idx, article in abstract.iterrows():
        print(article)
        art_form = ArticleForm()
        art_form.number = article['pmid']
        abstracts.append({'Abstract': sentence_tokenizer(article['abstract'])})
        art_form.sentence = '' 
        art_form.clause = ''
        
        pub_form.articles.append_entry(art_form)
        
    try:
        db.session.commit()
    except:
        db.session.rollback()
    
    return render_template('example/sample.html', pub_form = pub_form, pub=zip(pub_form.articles,abstracts), 
                           sub_form = submit_form)
    

@bp.route('/evaluate/', methods=['GET','POST'])
@login_required(1)
def assess():
        
    pub_form = PublicationsForm()
    submit_form = SubmitForm()
    close_form = CloseForm()
    loadmore_form = MoreForm()
    
    
    if submit_form.validate_on_submit():
        
        response = pd.read_csv(session.get('sample_file'), dtype=object)
        
        for idx, form_data in enumerate(pub_form.articles.data):
            
            if form_data['is_rct'] == True and form_data['sentence']:
                
                if form_data['clarity'] == 'Clear':
                    response.at[idx, 'response_clarity'] = 'clear'
                elif form_data['clarity'] == 'Weak':
                    response.at[idx, 'response_clarity'] = 'weak'
                
                response.at[idx, 'response_sentences'] = ''.join(form_data['sentence'].split('\n***'))
                response.at[idx, 'response_clauses'] = ''.join(form_data['clause'].split('\n***'))
                response.at[idx, 'response_RCT'] = True
                #response.at[idx, 'oracle_sentences'] = response.at[idx, 'oracle_sentences'].split('\n')
                #response.at[idx, 'oracle_clauses'] = response.at[idx, 'oracle_clauses'].split('\n')
                           
            elif form_data['is_rct'] == False:
                response.at[idx, 'response_rct'] = False
                
        #response = response.replace(to_replace= r'\r|\\n', value=r'<br />', regex=True)
            
            
        pd.set_option('display.max_colwidth', -1)
        pd.set_option('large_repr', 'info')
        pd.set_option('max_seq_items', 10000)#to display all list values
        return render_template('example/evaluate.html', msg = (response.to_html().replace(r'\n', '<hr />')).replace(r'\r', '<hr/>'),
                              more_form = loadmore_form, close_form = close_form) #display temporary stats 
        
    
@bp.route('/terminate/', methods=['GET','POST'])
@login_required(1)
def terminate():
    close_form = CloseForm()
    
    if close_form.validate_on_submit():
        return redirect(url_for('main.load')) 
    


@bp.route('/loadmore/', methods=['GET','POST'])
@login_required(1)
def more():
    loadmore_form = MoreForm()
    
    if loadmore_form.validate_on_submit():
        return redirect(url_for('example.sample'))  
    
