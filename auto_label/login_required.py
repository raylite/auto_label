#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 10:50:39 2019

@author: ja18581
"""
import functools 
from flask import session, redirect, url_for
from auto_label.models import User

def login_required(access_level):
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('auth.login'))
            
            user = User.query.filter_by(email=session['user']['email']).first()
    
            if not user.allowed(access_level):
                return redirect(url_for('main.label', message="YSorry, you have to be the ADMIN to access the requested page."))
            return f(*args, **kwargs)
    
        return decorated_function
    return decorator


