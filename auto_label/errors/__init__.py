from flask import Blueprint

bp = Blueprint('errors', __name__)

from auto_label.errors import errors