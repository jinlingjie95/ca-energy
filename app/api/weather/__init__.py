# app/api/weather/__init__.py
from flask import Blueprint

bp = Blueprint('weather_api', __name__)

from app.api.weather import routes