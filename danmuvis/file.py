from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from flask.cli import with_appcontext

import click

from danmuvis.auth import login_required
from danmuvis.db import get_db

from . import video

from . import danmaku


bp = Blueprint('file', __name__, url_prefix='/file')


path = ''


videos = []
danmakus = []
clips = []


def update_files():
    db = get_db()
    pass


@click.command('update-files')
@with_appcontext
def update_files_command():
    update_files()
    click.echo('File updated.')


@bp.route('/video_list', methods=('POST',))
def get_video_list():
    keyword = request.form['keyword']
    streamer = request.form['streamer']
    date = request.form['date']
    pass


@bp.route('/clip_list', methods=('POST',))
def get_clip_list():
    keyword = request.form['keyword']
    streamer = request.form['streamer']
    date = request.form['date']
    state = request.form['state']
    pass


@bp.route('/video/<string:filename>')
def get_video(filename):
    pass


@bp.route('/danmaku/<string:filename>')
def get_danmaku(filename):
    pass


@bp.route('/highlight/<string:filename>')
def get_highlight(filename):
    pass


@bp.route('/clip/<string:filename>')
def get_clip(filename):
    pass


@bp.route('/clip', methods=('POST',))
@login_required
def clip():
    pass
