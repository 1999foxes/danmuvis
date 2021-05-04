import os
import os.path

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory, jsonify
)
from werkzeug.exceptions import abort

from danmuvis.auth import login_required
from danmuvis.db import get_db

from .file import get_path, has_video, has_clip, new_clip, set_clip_state
from .video import Video


bp = Blueprint('player', __name__)


@bp.route('/')
def index():
    db = get_db()
    return render_template('player/index.html')


@bp.route('/play/<string:filename>')
def play(filename):
    return render_template('player/player.html', filename=filename)


@bp.route('/video/<string:filename>')
def get_video(filename):
    if has_video(filename):
        path = get_path()
        return send_from_directory(path, filename)
    else:
        abort(404)


@bp.route('/image/<string:filename>')
def get_image(filename):
    if has_video(filename):
        path = get_path()
        return send_from_directory(path, filename.replace('.ready', '').replace('.flv', '.jpg'))
    else:
        abort(404)


@bp.route('/danmaku/<string:filename>')
def get_danmaku(filename):
    if has_video(filename):
        path = get_path()
        return send_from_directory(path, filename.replace('.ready', '').replace('.flv', '.xml'))
    else:
        abort(404)


@bp.route('/ass/<string:filename>')
def get_ass(filename):
    if has_video(filename):
        path = get_path()
        return send_from_directory(path, filename.replace('.ready', '').replace('.flv', '.ass'))
    else:
        abort(404)


@bp.route('/highlight/<string:filename>')
def get_highlight(filename):
    if has_video(filename):
        path = get_path()
        return send_from_directory(path, filename.replace('.ready', '').replace('.flv', '.json'))
    else:
        abort(404)


@bp.route('/clip/<string:filename>')
def get_clip(filename):
    if has_clip(filename):
        path = get_path()
        return send_from_directory(path, filename)
    else:
        abort(404)


@bp.route('/do_clip', methods=('POST',))
@login_required
def clip():
    pass


@bp.route('/test_clip/<string:filename>')
def _test_clip(filename):
    v = Video(filename, get_path())
    for i in range(10):
        clipname = 'test_clip_' + str(i) + '.mp4'
        new_clip(clipname, filename)
        v.clip([i + 1, 3 * i + 3], clipname)
        input()
        set_clip_state(clipname, 1)
    return 'done'
