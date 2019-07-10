from flask import Blueprint

bp = Blueprint('main', __name__)

from auto_label.main import views