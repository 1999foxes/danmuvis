import os
import os.path
import re

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


def do_clip(filename, video_filename, start, end):
    # do clip, use executor, need implementation
    v = Video(video_filename, get_path())
    v.clip([start, end], filename)
    set_clip_state(filename, 1)


@bp.route('/do_clip', methods=('POST',))
def clip():
    filename = request.form.get('filename', '')
    video_filename = request.form.get('video_filename', '')
    start = request.form.get('start', '')
    end = request.form.get('end', '')
    if new_clip(filename, video_filename, start, end):
        # executor, do clip, not implemente
        do_clip(filename, video_filename, start, end)
        return 'ok'
    else:
        return 'clip failed'


@bp.route('/test_clip/<string:filename>')
def _test_clip(filename):
    for i in range(10):
        clipname = str(i) + '.mp4'
        if new_clip(clipname, filename, '0:00:0' + str(i) + '.000', '0:00:' + str(3 * i + 3) + '.000'):
            input()
            do_clip(clipname, filename,  '0:00:0' + str(i) + '.000', '0:00:' + str(3 * i + 3) + '.000')
    return 'done'
