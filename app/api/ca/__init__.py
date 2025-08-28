from flask import Blueprint

bp = Blueprint('ca_api', __name__)

from app.api.ca import routes