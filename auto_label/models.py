#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 17:37:31 2019

@author: ja18581
"""

from auto_label import db
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql import expression

ROLE = {
    'guest': 0,
    'user': 1,
    'admin': 2
}

class Abstract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pmid = db.Column(db.Integer, index=True, unique=True)
    abstract = db.Column(LONGTEXT())
    count = db.Column(db.Integer, default = 0)
    responses = db.relationship('Response', backref = 'root', lazy= 'dynamic')
    is_locked = db.Column(db.Boolean, default = False, server_default = expression.false(), nullable=False)
    is_clear_to_label = db.Column(db.Boolean, default = False, server_default = expression.false(), nullable=False)
    
    
    def __init__(self, pmid=None, abstract=None, count=None):
        self.data = (pmid, abstract)
    
    
    def __repr__(self):
        return (self.pmid, self.abstract)
    
class Removed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pmid = db.Column(LONGTEXT())
    abstract = db.Column(LONGTEXT())
    
    def __repr__(self):
        return f'<{self.pmid}>'

class Psentence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sentence = db.Column(LONGTEXT())
    label = db.Column(db.Boolean, default = True, server_default = expression.true(), nullable=False)
    response_id = db.Column(db.Integer, db.ForeignKey('response.id', ondelete='CASCADE'))
    
    
    def __repr__(self):
        return f'<Source ID: {self.abstract_id}; Content: {self.sentence}; Label: {self.label}>'

class Pclause(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clause = db.Column(LONGTEXT())
    label = db.Column(db.Boolean, default = True, server_default = expression.true(), nullable=False)
    response_id = db.Column(db.Integer, db.ForeignKey('response.id', ondelete='CASCADE'))
    #sentence = db.relationship('Psentence', backref='source')
    
    def __repr__(self):
        return f'<Source ID: {self.sentence_id}; Content: {self.clause}; Label: {self.label}>'
    
class Nsentence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sentence = db.Column(LONGTEXT())
    label = db.Column(db.Boolean, default = False, server_default = expression.false(), nullable=False)
    response_id = db.Column(db.Integer, db.ForeignKey('response.id', ondelete='CASCADE'))
    
    def __repr__(self):
        return f'<Source ID: {self.abstract_id}; Content: {self.sentence}; Label: {self.label}>'
    
class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #neg_sentence = db.Column(LONGTEXT()) #joined
    #pos_sent = db.Column(LONGTEXT()) #joined
    #clause = db.Column(LONGTEXT()) #joined
    len_of_neg = db.Column(db.Integer)
    len_of_pos = db.Column(db.Integer)
    len_of_clause = db.Column(db.Integer)
    abstract_id = db.Column(db.Integer, db.ForeignKey('abstract.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    nsentences = db.relationship('Nsentence', backref = 'source', lazy= 'dynamic')
    psentences = db.relationship('Psentence', backref = 'source', lazy = 'dynamic')
    pclauses = db.relationship('Pclause', backref = 'source', lazy = 'dynamic')
    
        
    def __repr__(self):
        return f'<Labeller: {self.user_id}; Source ID: {self.abstract_id}; Length of Neg: {self.len_of_neg}; Length of Pos: {self.len_of_pos}; Clause size: {self.len_of_clause}>'



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), index = True, unique = True)
    name = db.Column(db.String(100), index = True)
    abstracts = db.relationship('Abstract', secondary='user_abstracts', lazy = 'dynamic',
                               backref = db.backref('labellers', lazy = True))
    is_authenticated = db.Column(db.Boolean, default = False, server_default = expression.false(), nullable=False)
    is_admin = db.Column(db.Boolean, default = False, server_default = expression.false(), nullable=False)
    responses = db.relationship('Response', backref='screener', lazy='dynamic')
    role = db.Column(db.Integer, default = 1)
    
    def __repr__(self):
        return f'<{self.name}>'
    
    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.is_authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False
    
    def is_admin(self):
        return self.role == ROLE['admin']
    
    def allowed(self, access_level):
        return self.role >= access_level


    
user_abstracts = db.Table('user_abstracts',
                          db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key = True),
                          db.Column('abstract_id', db.Integer, db.ForeignKey('abstract.id'), primary_key = True))
    

    
    