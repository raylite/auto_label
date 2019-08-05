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
    responses = db.relationship('Response', backref = 'root', lazy= 'dynamic')
    
    def __init__(self, pmid=None, abstract=None, count=None):
        self.data = (pmid, abstract)
    
    
    def __repr__(self):
        return (self.pmid, self.abstract)


class Psentence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sentence = db.Column(LONGTEXT())
    label = db.Column(db.Boolean)
    response_id = db.Column(db.Integer, db.ForeignKey('response.id'))
    
    
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
    response_id = db.Column(db.Integer, db.ForeignKey('response.id'))
    
    def __repr__(self):
        return f'<Source ID: {self.abstract_id}; Content: {self.sentence}; Label: {self.label}>'
    
class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    neg_sentence = db.Column(LONGTEXT()) #joined
    pos_sent = db.Column(LONGTEXT()) #joined
    clause = db.Column(LONGTEXT()) #joined
    len_of_neg = db.Column(db.Integer)
    len_of_pos = db.Column(db.Integer)
    len_of_clause = db.Column(db.Integer)
    abstract_id = db.Column(db.Integer, db.ForeignKey('abstract.id'))
    nsentences = db.relationship('Nsentence', backref = 'source', lazy= 'dynamic')
    psentences = db.relationship('Psentence', backref = 'source', lazy = 'dynamic')
    
    
    def __repr__(self):
        return f'<Source ID: {self.abstract_id.pmid}; Length of Neg: {self.len_of_neg}; Length of Pos: {self.len_of_pos}; Clause size: {self.len_of_clause}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), index = True, unique = True)
    name = db.Column(db.String(100), index = True)
    abstracts = db.relationship('Abstract', secondary='user_abstracts', lazy = 'subquery',
                               backref = db.backref('labellers', lazy = True))
    authenticated = db.Column(db.Boolean, default = False)
    
    def __repr__(self):
        return f'<User: {self.email}; Abstracts: {[abstract.pmid for abstract in self.abstracts]}>'
    
    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    
user_abstracts = db.Table('user_abstracts',
                          db.Column('user.id', db.Integer, db.ForeignKey('user.id'), primary_key = True),
                          db.Column('abstract.id', db.Integer, db.ForeignKey('abstract.id'), primary_key = True))
    

    
    