from flask import Blueprint

message_bp = Blueprint("message", __name__)

from . import routes