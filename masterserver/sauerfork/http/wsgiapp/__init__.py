# -*- coding: utf-8 -*-

import os

from flask import Flask, jsonify, request
from masterserver.exc import ServerCollisionError
from .models import Server

app = Flask(__name__)

# The latest Revelade Revolution version string the game client reports
# (RR_VERSION_STRING in the game's src/shared/rr_version.h). The client's
# version check asks /version/check-last whether its own string is the
# latest; override with MASTERSERVER_LATEST_VERSION when it changes.
LATEST_VERSION = os.environ.get(
    "MASTERSERVER_LATEST_VERSION", "0.1.0-alpha-4-r-1"
)


@app.route("/")
def index():
    # The game client parses the response body as a bare JSON array of
    # server objects and keys each one by its "uuid" field; the old
    # {"serverlist": [...]} wrapper without uuids cannot be parsed by it.
    return jsonify([srv.to_dict() for srv in Server.getlist()])


@app.route("/version/check-last")
def check_last():
    # The client treats the version as current when the first byte of the
    # response body is "1", and outdated when it is "0".
    current = request.args.get("version", "") == LATEST_VERSION
    return ("1" if current else "0"), 200, {"Content-Type": "text/plain"}


def _register(ip, port, name, playercount):
    existing = Server.find(ip, port)
    if existing is not None:
        existing.name = name or existing.name
        existing.playercount = int(playercount)
        return existing
    return Server.register(ip, port, name=name, playercount=playercount)


@app.route("/register")
def register():
    # Lets a game server (or a test script with curl) join the master
    # list over HTTP: /register?port=27960&name=My+Server&playercount=0
    try:
        port = int(request.args.get("port", ""))
        name = request.args.get("name", "")
        playercount = int(request.args.get("playercount", "0"))
        server = _register(request.remote_addr, port, name, playercount)
    except (ValueError, ServerCollisionError):
        return ("failreg"), 400, {"Content-Type": "text/plain"}
    return jsonify(server.to_dict())


@app.route("/servers", methods=["POST"])
def register_json():
    data = request.get_json(silent=True) or {}
    try:
        port = int(data.get("port", ""))
        name = data.get("name", "")
        playercount = int(data.get("playercount", 0))
        server = _register(request.remote_addr, port, name, playercount)
    except (ValueError, ServerCollisionError):
        return jsonify({"error": "failreg"}), 400
    return jsonify(server.to_dict())


@app.route("/unregister")
def unregister():
    removed = Server.remove_by_uuid(request.args.get("uuid", ""))
    return ("1" if removed else "0"), 200, {"Content-Type": "text/plain"}
