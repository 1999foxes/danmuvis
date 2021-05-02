from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from danmuvis.auth import login_required
from danmuvis.db import get_db

bp = Blueprint('player', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('player/index.html', posts=posts)


@bp.route('/play/<string:filename>')
def play(filename):
    return filename
