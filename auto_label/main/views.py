#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 17:37:09 2019

@author: ja18581
"""

from auto_label import db
from flask import render_template, url_for, redirect, session, request, current_app
import pandas as pd
from sqlalchemy.sql.expression import func

from auto_label.main import bp
from auto_label.main.forms import ArticleForm, PublicationsForm, SubmitForm, MoreForm, CloseForm, LoadOptionForm
from auto_label.models import Psentence, Nsentence, Pclause, Abstract, Response, User, Removed
from auto_label.login_required import login_required

from utilities.paginator import PageResult #local class for displaying result in pages
from utilities.custom_tokenizer import sentence_tokenizer #local tokenizer



@bp.route('/')
@bp.route('/index/')
def index():
    return render_template('login.html', title = 'login')


@bp.route('/load_option/', methods=['GET','POST'])
@login_required(1)
def load():
    load_article_form = LoadOptionForm()
    if load_article_form.validate_on_submit():
        session['load_limit'] = load_article_form.number.data
        return redirect(url_for('main.label'))
    
    return render_template('index.html', load_article_form=load_article_form)


@bp.route('/label/', methods=['GET','POST'])
@login_required(1)
def label():
    user = User.query.filter_by(email=session['user']['email']).first() ##user object
    user_label_list = [abstract.pmid for abstract in user.abstracts]#list of abstracts labelled so far by the user
    
    abstract = pd.read_sql(sql=db.session.query(Abstract).
                           filter(Abstract.count < current_app.config['MAX_LABEL_ROUND_PER_ARTICLE'],
                                  Abstract.pmid.notin_(user_label_list), Abstract.is_locked == False).
                           order_by(func.random()).limit(session.get('load_limit', None)).
                           with_entities(Abstract.pmid, Abstract.abstract, Abstract.count).statement, con=db.session.bind)
    
    session['pmid_list'] = list(abstract['pmid'])
    Abstract.query.filter(Abstract.pmid.in_(session.get('pmid_list', None))).update({'is_locked': True}, synchronize_session = False)#lock loaded articles until released to prevent race condition in count updating and assignment
    db.session.commit()
        
    pub_form = PublicationsForm()
    submit_form = SubmitForm()
    
    
    pub_form.title.data = 'Publications List'
    
    abstracts = []
    
    for idx, article in abstract.iterrows():
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
    
    return render_template('label.html', pub_form = pub_form, pub=zip(pub_form.articles,abstracts), 
                           sub_form = submit_form)

@bp.route('/process/', methods=['GET','POST'])
@login_required(1)
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
        removed = 0
        clear = 0
        weak = 0
        
        for idx, form_data in enumerate(pub_form.articles.data):
            abstr = Abstract.query.filter_by(pmid=form_data['number']).first()
            if form_data['is_rct'] == True and form_data['sentence']:
                                
                if abstr.count + 1 < 2:
                    abstr.is_locked = False #release the lock
                abstr.count = abstr.count + 1 #increase the number of times the abtract has been labelled
                  
                user.abstracts.append(abstr)#add to users labelled list for many to may relnshp
                
                if form_data['clarity'] == 'Clear':
                    abstr.is_clear_to_label = True
                    clear += 1
                elif form_data['clarity'] == 'Weak':
                    abstr.is_clear_to_label = False
                    weak += 1
                
                neg_sent = sentence_tokenizer(abstr.abstract)
                neg_sent = [s for s in neg_sent if s not in form_data['sentence'].split('\n***')]
                response = Response(len_of_neg = len(neg_sent), 
                                    len_of_pos = len(form_data['sentence'].split('\n***')),
                                    len_of_clause = len(form_data['clause'].split('\n***')), 
                                    abstract_id = abstr.id, 
                                    screener = user)
                db.session.add(response)
                db.session.commit()
                
                response = Response.query.filter_by(abstract_id = abstr.id).first() #abstract source for the responses
                
                for s in neg_sent:
                    ns  = Nsentence(sentence=s, label = False, source = response)
                    neg_sent_list.append(ns)
                    
                for s in form_data['sentence'].split('\n***'):
                    pos_sent_list.append(s) #for display purpose
                    p = Psentence(sentence=s, label = True, source = response)
                    db.session.add(p)
                #db.session.commit() #committed so that clause could have Id to relate to
                
                                
                for s in form_data['clause'].split('\n***'):
                    c = Pclause(clause=s, label = True, source = response)
                    clause_list.append(c) #for display purpose
                
                           
            elif form_data['is_rct'] == False:
                rem = Removed(pmid = form_data['number'], abstract = abstr.abstract)
                removed += 1
                                
                db.session.delete(abstr)#remove the non RCTs
                db.session.add(rem)
                
            elif not form_data['sentence'] and form_data['is_rct']:
                abstr.is_locked = False #release the lock
        try:
            db.session.bulk_save_objects(neg_sent_list)
            db.session.bulk_save_objects(clause_list)
            db.session.commit()
        except:
            db.session.rollback()
            raise
    
    
        nsents = {'Item': 'other sentences', 'Count': len(neg_sent_list)}
        psents = {'Item': 'sentences indicating comparison', 'Count': len(pos_sent_list)} #fix its capturing only d last one
        clause = {'Item': 'clause/phrase indicating comparison', 'Count': len(clause_list)}
        non_rcts = {'Item': 'Non_RCTs (deleted)', 'Count': removed}
        clear = {'Item': 'Marked clear', 'Count': clear}
        weak = {'Item': 'Marked weak', 'Count': weak}
        
        summary = pd.DataFrame([psents, nsents, clause, non_rcts, clear, weak])
        return render_template('process.html', msg = summary.to_html(), more_form = loadmore_form,
                               close_form = close_form)#display temporary stats 

        
    

@bp.route('/terminate/', methods=['GET','POST'])
@login_required(1)
def terminate():
    close_form = CloseForm()
    
    if close_form.validate_on_submit():
        return render_template('terminate.html')   
    
    return render_template('terminate.html')


@bp.route('/loadmore/', methods=['GET','POST'])
@login_required(1)
def more():
    loadmore_form = MoreForm()
    
    if loadmore_form.validate_on_submit():
        return redirect(url_for('main.label'))  
    
    return render_template('label.html')



@bp.route('/progress_view/')
@login_required(2)
def view_progress():#query the clause, sentences tables to know count
    
    response_count = {'Item': 'total abstracts labelled', 'Count': Response.query.count()}
    unique_resp = {'Item': 'unique abstracts labelled', 'Count': Response.query.with_entities(Response.abstract_id).distinct().count()}
    psents = {'Item': 'Positve sentences', 'Count': Psentence.query.count()}
    nsents = {'Item': 'Negaitve sentences', 'Count': Nsentence.query.count()}
    clause = {'Item': 'Positve clause/phrase', 'Count': Pclause.query.count()}
    deleted = {'Item': 'Removed non_RCTs', 'Count': Removed.query.count()}
    total = {'Item': 'RCTs', 'Count': Abstract.query.count()}
    
    status_report = pd.DataFrame([response_count, unique_resp, psents, nsents, clause, deleted, total])
    articles_count = pd.DataFrame([{'Article': abstract.pmid, 'Count': abstract.count} for abstract in Abstract.query.all()])
    user_screening = pd.DataFrame([{'User': user.name, 'Total screening': len(user.abstracts), 'PMIDs': [abstract.pmid for abstract in user.abstracts],} for user in User.query.all()])
    article_screening = pd.DataFrame([{'Article': abstract.pmid, "Screeners\' Id": [user.name for user in abstract.labellers]} for abstract in Abstract.query.all()])
    responses = pd.DataFrame([{'Article': resp.root.pmid, 'Positive': ['.\n'.join(s.sentence) for s in resp.psentences], \
                               'Negative': ['.\n'.join(s.sentence) for s in resp.nsentences], \
                               'Clause':['.\n'.join(c.clause) for c in resp.pclauses], 'Screener': resp.screener} 
    for resp in Response.query.all()]).sort_values(by=['Article']).reset_index(drop=True)
    
   
    out_list = [status_report, articles_count, user_screening,article_screening, responses]
        
    page = request.args.get('page', 0, type=int)
    results = PageResult(out_list, page = page, list_paging =True)##activates the list based pager
    report = results.list_on_page()
    
    next_url = url_for('main.view_progress', page=results.next_page()) if results.has_next() else None
    prev_url = url_for('main.view_progress', page=results.prev_page()) if results.has_prev() else None
    
    pd.set_option('display.max_colwidth', -1)
    pd.set_option('large_repr', 'info')
    pd.set_option('max_seq_items', 10000)#to display all list values
    return render_template('progress.html', report = report.to_html(), next_url=next_url, prev_url=prev_url)











