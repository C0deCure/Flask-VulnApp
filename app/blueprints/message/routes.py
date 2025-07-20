from flask import Blueprint
from . import message_bp

@message_bp.route("/ping", methods=["GET"])
def ping():
    return "테스트"