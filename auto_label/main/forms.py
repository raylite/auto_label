#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 17:37:47 2019

@author: ja18581
"""

from flask_wtf import FlaskForm
from wtforms.fields import BooleanField, FieldList, FormField, IntegerField, StringField, SubmitField
from wtforms.widgets import TextArea
#from auto_label.models import *

class ArticleForm(FlaskForm):
    number = IntegerField('number', render_kw={'readonly': True})
    #abstract = HiddenField('Abstract')#, render_kw={'readonly': True})
    sentence = StringField('Sentence', widget=TextArea(), render_kw={'readonly': True})
    clause = StringField('Clause', widget=TextArea(), render_kw={'readonly': True})
    rct = BooleanField('RCT', false_values=('False', ''))
    
class PublicationsForm(FlaskForm):
    title = StringField('Publications', render_kw={'readonly': True})
    articles = FieldList(FormField(ArticleForm))#
    
class SubmitForm(FlaskForm):
    submit = SubmitField('Click to submit and end')
    
class MoreForm(FlaskForm):
    subandloadmore = SubmitField('Click to save response and load more')
    
    