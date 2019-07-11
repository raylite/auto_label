#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 17:37:31 2019

@author: ja18581
"""

from auto_label import db
from sqlalchemy.dialects.mysql import LONGTEXT

class Abstract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pmid = db.Column(db.Integer, index=True, unique=True)
    abstract = db.Column(LONGTEXT())
    count = db.Column(db.Integer)
    non_rct = db.Column(db.Boolean, default=False)
    nsentences = db.relationship('Nsentence', backref = 'source', lazy= 'dynamic')
    
    def __init__(self, pmid=None, abstract=None, count=None):
        self.data = (pmid, abstract)
    
    
    def __repr__(self):
        return (self.pmid, self.abstract)


class Psentence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sentence = db.Column(LONGTEXT())
    label = db.Column(db.Boolean)
    abstract_id = db.Column(db.Integer, db.ForeignKey('abstract.id'))
    abstract = db.relationship('Abstract', backref='source')
    
    def __repr__(self):
        return f'<Source ID: {self.abstract_id}; Content: {self.sentence}; Label: {self.label}>'

class Pclause(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clause = db.Column(LONGTEXT())
    label = db.Column(db.Boolean)
    sentence_id = db.Column(db.Integer, db.ForeignKey('psentence.id'))
    #sentence = db.relationship('Psentence', backref='source')
    
    def __repr__(self):
        return f'<Source ID: {self.sentence_id}; Content: {self.clause}; Label: {self.label}>'
    
class Nsentence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sentence = db.Column(LONGTEXT())
    label = db.Column(db.Boolean)
    abstract_id = db.Column(db.Integer, db.ForeignKey('abstract.id'))
    
    def __repr__(self):
        return f'<Source ID: {self.abstract_id}; Content: {self.sentence}; Label: {self.label}>'
