import os
import os.path

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory, jsonify
)
from werkzeug.exceptions import abort

from danmuvis.auth import login_required
from danmuvis.db import get_db

from . import danmaku
from . import video


bp = Blueprint('player', __name__)


@bp.route('/')
def index():
    db = get_db()
    return render_template('player/index.html')


@bp.route('/play/<string:filename>')
def play(filename):
    return filename


@bp.route('/video/<string:filename>')
def get_video(filename):
    cur = get_db().cursor()
    if cur.execute("SELECT * FROM video WHERE filename='" + filename + "'").fetchone() is not None:
        path = cur.execute("SELECT * FROM path").fetchone()['p']
        return send_from_directory(path, filename)
    else:
        abort(404)


@bp.route('/image/<string:filename>')
def get_image(filename):
    cur = get_db().cursor()
    if cur.execute("SELECT * FROM video WHERE filename='" + filename + "'").fetchone() is not None:
        path = cur.execute("SELECT * FROM path").fetchone()['p']
        return send_from_directory(path, filename.replace('.metadata', '').replace('.flv', '.jpg'))
    else:
        abort(404)


@bp.route('/danmaku/<string:filename>')
def get_danmaku(filename):
    cur = get_db().cursor()
    if cur.execute("SELECT * FROM video WHERE filename='" + filename + "'").fetchone() is not None:
        path = cur.execute("SELECT * FROM path").fetchone()['p']
        return send_from_directory(path, filename.replace('.metadata', '').replace('.flv', '.xml'))
    else:
        abort(404)


@bp.route('/highlight/<string:filename>')
def get_highlight(filename):
    cur = get_db().cursor()
    if cur.execute("SELECT * FROM video WHERE filename='" + filename + "'").fetchone() is not None:
        path = cur.execute("SELECT * FROM path").fetchone()['p']
        filepath = os.path.join(path, filename.replace('.metadata', '').replace('.flv', '.xml'))
        d = danmaku.Danmaku(filepath)
        return jsonify(d.highlight)
    else:
        abort(404)


@bp.route('/clip/<string:filename>')
def get_clip(filename):
    cur = get_db().cursor()
    if cur.execute("SELECT * FROM clip WHERE filename='" + filename + "'").fetchone() is not None:
        path = cur.execute("SELECT * FROM path").fetchone()['p']
        return send_from_directory(path, filename)
    else:
        abort(404)


@bp.route('/clip', methods=('POST',))
@login_required
def clip():
    pass
