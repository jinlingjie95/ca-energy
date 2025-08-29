# app/api/fire/__init__.py
from flask import Blueprint

bp = Blueprint('fire_api', __name__)

from app.api.fire import routes