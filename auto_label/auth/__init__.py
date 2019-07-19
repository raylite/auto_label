from flask import Blueprint

bp = Blueprint('auth', __name__)

from auto_label.auth import auth
