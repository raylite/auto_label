#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 12:17:22 2019

@author: ja18581
"""
from flask import request, url_for, redirect, current_app, session
from flask_oauthlib.client import OAuth
import uuid
import os

from auto_label import db
from auto_label.auth import bp
from auto_label.models import User, Abstract


oauth = OAuth(bp)

ms_graph = oauth.remote_app('microsoft',
                            consumer_key = os.getenv('CLIENT_ID'),
                            consumer_secret = os.getenv('CLIENT_SECRET'),
                            request_token_params={'scope': 'User.Read'},
                            
                            base_url=os.getenv('RESOURCE') + os.getenv('API_VERSION') + '/',
                            request_token_url=None, 
                            access_token_method='POST',
                            access_token_url=os.getenv('AUTHORITY_URL') + os.getenv('TOKEN_ENDPOINT'),
                            authorize_url=os.getenv('AUTHORITY_URL') + os.getenv('AUTH_ENDPOINT'))

@bp.route('/login/', methods = ['POST', 'GET'])
def login():
    """Prompt user to authenticate."""
    session['state'] = str(uuid.uuid4())
    return ms_graph.authorize(callback=current_app.config['REDIRECT_URI'], state=session['state'])

@bp.route('/logout')
#@login_required
def logout():
    """Clear the current session, including the stored user id."""
    user = User.query.filter_by(email=session['user']['email']).first()
    user.is_authenticated = False
    if session.get('pmid_list'):
        Abstract.query.filter(Abstract.pmid.in_(session.get('pmid_list')), 
                          Abstract.count < current_app.config['MAX_LABEL_ROUND_PER_ARTICLE']).\
                          update({'is_locked': False}, synchronize_session = False)#release any locked articles in case of logging out without labelling
    
    db.session.commit()
    session.pop('user', None)
    return redirect(url_for('main.index'))


@bp.route('/login/authorized/')
def authorized():
    """Handler for the application's Redirect Uri."""
    if str(session.get("state")) != str(request.args['state']):
        raise Exception('state returned to redirect URL does not match!')
    response = ms_graph.authorized_response()
    session['access_token'] = response['access_token']
    
    
    
    
    """ Get user details from ms graph"""
    endpoint = 'me'
    headers = {'SdkVersion': 'sample-python-flask',
               'x-client-SKU': 'sample-python-flask',
               'client-request-id': str(uuid.uuid4()),
               'return-client-request-id': 'true'}
    response = ms_graph.get(endpoint, headers=headers).data
    
    'add user to OR load user from db'
    user = User.query.filter_by(email=response['mail']).first()
    if user:
        user.is_authenticated = True
        if response['displayName'] == os.getenv('ADMIN'):
            user.role = 2
        else:
            user.role = 1
            
        db.session.add(user)
        db.session.commit()
    else:
        user = User(
                email=response['mail'], 
                name=response['displayName'], 
                is_authenticated = True
                )
        if response['displayName'] == os.getenv('ADMIN'):
            user.role = 2
        else:
            user.role = 1
            
        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(email=response['mail']).first()
        
    session['user'] = {'email': user.email, 'name': user.name, 'is_authenticated': user.is_authenticated}
    
    return redirect(url_for('main.load'))

    
@ms_graph.tokengetter
def get_token():
    """Called by flask_oauthlib.client to retrieve current access token."""
    return (session.get('access_token'), '')
