#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 17:37:09 2019

@author: ja18581
"""

from auto_label import app, db
from flask import render_template, request
import pandas as pd
from nltk import tokenize

from auto_label.forms import ArticleForm, PublicationsForm
from auto_label.models import Psentence, Nsentence, Pclause, Abstract


@app.route('/')
def index():
    abstract = pd.read_sql(sql=db.session.query(Abstract).filter(Abstract.count == 0).limit(5)\
                                .with_entities(Abstract.pmid,
                                               Abstract.abstract).statement, con=db.session.bind)
    #abstract = pd.DataFrame(articles_list)
    
    pub_form = PublicationsForm()
    pub_form.title.data = 'Publications List'
    
    abstracts = []
    
    for idx, article in abstract.iterrows():
        art_form = ArticleForm()
        art_form.number = article['pmid']
        abstracts.append({'Abstract': tokenize.sent_tokenize(article['abstract'])})
        art_form.sentence = '' 
        art_form.clause = ''
        #pub_form.abstract = article['abstract']
        
        
        pub_form.articles.append_entry(art_form)
    
    
    return render_template('index.html', pub_form = pub_form, pub=zip(pub_form.articles,abstracts))

@app.route('/process/', methods=['GET','POST'])
def process():
        
    pub_form = PublicationsForm()
        
    if request.method == 'POST':
        #update database
        positive_sent = []
        neg_sent = []
        clause_list = []
        
        for idx, form_data in enumerate(pub_form.articles.data):
            if form_data['rct'] == False or form_data['rct'] == '':
                abstr = Abstract.query.filter_by(pmid=form_data['number']).first()
                abstr.count += 1
                
                psent = {'sentence':form_data['sentence'], 'label':form_data['rct'], 'abstract_id':form_data['number'], 
                         'clause':form_data['clause']}#use this to query Abstarct Id
                positive_sent.append(psent)
                for s in form_data['sentence'].split('***'):
                    p = Psentence(sentence=s, label = True, abstract_id = abstr.id)
                    db.session.add(p)
                db.session.commit() #committed so that clause could have Id to relate to
                
                for s in form_data['clause'].split('***'):
                    source = Psentence.query.filter_by(abstract_id = abstr.id).first()
                    c = Pclause(clause=s, label = True, sentence_id = source.id)
                    clause_list.append(c)
                
                nl = tokenize.sent_tokenize(abstr.abstract)
                for n in (s for s in nl if s not in form_data['sentence'].split('***')):
                    ns = Nsentence(sentence=n, label = False, abstract_id = abstr.id)
                    neg_sent.append(ns)
        try:
            db.session.bulk_save_objects(neg_sent)
            db.session.bulk_save_objects(clause_list)
            db.session.commit()
        except:
            db.session.rollback()
            raise
            
        nsents = {'Item': 'negaitve sentences', 'Count': len(nl)}
        psents = {'Item': 'positve sentences', 'Count': len(form_data['sentence'].split('***'))}
        clause = {'Item': 'positve clause/phrase', 'Count': len(form_data['clause'].split('***'))}
        
        summary = pd.DataFrame([psents, nsents, clause])
        return render_template('process.html', msg = summary.to_html())#display temporary stats 
    
    return render_template('index.html', pub_form=pub_form)


@app.route('/progress_view/')
def view_progress():#query the clause, sentences tables to know count
    psents = {'Item': 'positve sentences', 'Count': Psentence.query.count()}
    nsents = {'Item': 'negaitve sentences', 'Count': Nsentence.query.count()}
    clause = {'Item': 'positve clause/phrase', 'Count': Pclause.query.count()}
    
    status_report = pd.DataFrame([psents, nsents, clause])
    
    return render_template('progress.html', report = status_report.to_html())