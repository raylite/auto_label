#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 17:37:09 2019

@author: ja18581
"""

from auto_label import db
from flask import render_template, url_for, redirect, session
import pandas as pd
from nltk import tokenize
from sqlalchemy.sql.expression import func

from auto_label.main import bp
from auto_label.main.forms import ArticleForm, PublicationsForm, SubmitForm, MoreForm, CloseForm
from auto_label.models import Psentence, Nsentence, Pclause, Abstract, Response, User
from auto_label.login_required import login_required




@bp.route('/')
@bp.route('/index/')
def index():
    return render_template('index.html', title = 'login')


@bp.route('/label')
@login_required
def label():
    user = User.query.filter_by(email=session['user']['email']).first()
    user_label_list = [abstract.pmid for abstract in user.abstracts]
    print (f'LIST: {user_label_list}')
    abstract = pd.read_sql(sql=db.session.query(Abstract).\
                           filter(Abstract.count < 2).\
                           filter(Abstract.pmid.notin_(user_label_list)).\
                           order_by(func.random()).limit(5).\
                           with_entities(Abstract.pmid, Abstract.abstract, Abstract.count).statement, con=db.session.bind)
   
    pub_form = PublicationsForm()
    submit_form = SubmitForm()
    
    
    pub_form.title.data = 'Publications List'
    
    abstracts = []
    
    for idx, article in abstract.iterrows():
        art_form = ArticleForm()
        art_form.number = article['pmid']
        abstracts.append({'Abstract': tokenize.sent_tokenize(article['abstract'])})
        art_form.sentence = '' 
        art_form.clause = ''
        print(f"{article['pmid']}: {article['count']}")
        pub_form.articles.append_entry(art_form)
        
    try:
        db.session.commit()
    except:
        db.session.rollback()
    
    
    return render_template('label.html', pub_form = pub_form, pub=zip(pub_form.articles,abstracts), 
                           sub_form = submit_form)

@bp.route('/process/', methods=['GET','POST'])
@login_required
def process():
        
    pub_form = PublicationsForm()
    submit_form = SubmitForm()
    loadmore_form = MoreForm()
    close_form = CloseForm()
    
    user = User.query.filter_by(email=session['user']['email']).first()
    
    if submit_form.validate_on_submit():
        #update database
        pos_sent_list = []
        neg_sent_list = []
        clause_list = []
        
        for idx, form_data in enumerate(pub_form.articles.data):
            if form_data['rct'] == True:
                abstr = Abstract.query.filter_by(pmid=form_data['number']).first()
                abstr.count += 1 #increase the number of times the abtract has been labelled
                user.abstracts.append(abstr)#add to users labelled list for many to may relnshp
                
                neg_sent = tokenize.sent_tokenize(abstr.abstract)
                neg_sent = [s for s in neg_sent if s not in form_data['sentence'].split('***')]
                response = Response(neg_sentence = ' '.join(neg_sent), pos_sent = form_data['sentence'], clause = form_data['clause'],
                                    len_of_neg = len(neg_sent), len_of_pos = len(form_data['sentence'].split('***')),
                                    len_of_clause = len(form_data['clause'].split('***')), abstract_id = abstr.id)
                db.session.add(response)
                db.session.commit()
                
                ab_source = Response.query.filter_by(abstract_id = abstr.id).first() #abstract source for the responses
                
                for s in form_data['sentence'].split('***'):
                    pos_sent_list.append(s)
                    p = Psentence(sentence=s, label = True, response_id = ab_source.id)
                    db.session.add(p)
                db.session.commit() #committed so that clause could have Id to relate to
                
                sen_source = Psentence.query.filter_by(response_id = ab_source.id).first() #sentence source for the clause
                
                for s in form_data['clause'].split('***'):
                    c = Pclause(clause=s, label = True, sentence_id = sen_source.id)
                    clause_list.append(c)
                
                nl = tokenize.sent_tokenize(abstr.abstract)
                for n in (s for s in nl if s not in form_data['sentence'].split('***')):
                    ns = Nsentence(sentence=n, label = False, response_id = ab_source.id)
                    neg_sent_list.append(ns)
        try:
            db.session.bulk_save_objects(neg_sent_list)
            db.session.bulk_save_objects(clause_list)
            db.session.commit()
        except:
            db.session.rollback()
            raise
            
        nsents = {'Item': 'negaitve sentences', 'Count': len(neg_sent_list)}
        psents = {'Item': 'positve sentences', 'Count': len(pos_sent_list)} #fix its capturing only d last one
        clause = {'Item': 'positve clause/phrase', 'Count': len(clause_list)}
        
        summary = pd.DataFrame([psents, nsents, clause])
        return render_template('process.html', msg = summary.to_html(), more_form = loadmore_form,
                               close_form = close_form)#display temporary stats 
    #elif loadmore_form.validate_on_submit():
        
    

@bp.route('/terminate/', methods=['GET','POST'])
@login_required
def terminate():
    close_form = CloseForm()
    
    if close_form.validate_on_submit():
        return render_template('terminate.html')   
    
    return render_template('terminate.html')

@bp.route('/loadmore/', methods=['GET','POST'])
def more():
    loadmore_form = MoreForm()
    
    if loadmore_form.validate_on_submit():
        return redirect(url_for('main.index'))  
    
    return redirect(url_for('main.label'))



@bp.route('/progress_view/')
@login_required
def view_progress():#query the clause, sentences tables to know count
    responses = {'Item': 'total abstracts labelled', 'Count': Response.query.count()}
    unique_resp = {'Item': 'unique abstracts labelled', 'Count': Response.query.with_entities(Response.abstract_id).distinct().count()}
    psents = {'Item': 'positve sentences', 'Count': Psentence.query.count()}
    nsents = {'Item': 'negaitve sentences', 'Count': Nsentence.query.count()}
    clause = {'Item': 'positve clause/phrase', 'Count': Pclause.query.count()}
    
    status_report = pd.DataFrame([responses, unique_resp, psents, nsents, clause])
    
    return render_template('progress.html', report = status_report.to_html())