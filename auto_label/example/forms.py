#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 17:37:47 2019

@author: ja18581
"""

from flask_wtf import FlaskForm
from wtforms.fields import BooleanField, FieldList, FormField, IntegerField, StringField, SubmitField, RadioField
from wtforms.widgets import TextArea
#from auto_label.models import *

class ArticleForm(FlaskForm):
    number = IntegerField('number', render_kw={'readonly': True})
    sentence = StringField('Sentence', widget=TextArea(), render_kw={'readonly': True})
    clause = StringField('Clause', widget=TextArea(), render_kw={'readonly': True})
    is_rct = BooleanField('RCT', false_values=('False', '', None))
    clarity = RadioField('Clarity', choices=[('Clear', 'Clear'), ('Weak', 'Weak')])
    
class PublicationsForm(FlaskForm):
    title = StringField('Publications', render_kw={'readonly': True})
    articles = FieldList(FormField(ArticleForm))#
    
class SubmitForm(FlaskForm):
    submit = SubmitField('Submit responses')
    
class MoreForm(FlaskForm):
    subandloadmore = SubmitField('Try again')
    
class CloseForm(FlaskForm):
    submit = SubmitField('End process')
    

    