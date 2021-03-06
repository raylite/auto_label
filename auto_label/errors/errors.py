#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 12 18:27:45 2018

@author: kazeem
"""
from flask import render_template
from auto_label import db
from auto_label.errors import bp

@bp.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 400

@bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500