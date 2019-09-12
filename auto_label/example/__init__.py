from flask import Blueprint

bp = Blueprint('example', __name__)

from auto_label.example import example
