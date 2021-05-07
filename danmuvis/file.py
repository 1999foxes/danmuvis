import os
import os.path
import re

import sqlite3

import subprocess

import click
from flask import (
    Blueprint, request, jsonify, send_from_directory
)
from flask.cli import with_appcontext

from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db
from .danmaku import Danmaku
from .video import Video


bp = Blueprint('file', __name__, url_prefix='/file')

video_ext = ['flv', 'FLV']
danmaku_ext = ['xml', 'XML']


def set_path(path):
    db = get_db()
    cur = db.cursor()
    cur.execute('DELETE FROM path')
    cur.execute("INSERT INTO path(p) VALUES('" + path + "')")
    db.commit()


def get_path():
    path = get_db().execute('SELECT p from path').fetchone()['p']
    return path


def update_files():
    path = get_path()

    db = get_db()
    cur = db.cursor()

    cur.execute(
        'DELETE FROM video'
    )
    # cur.execute(
    #     'DELETE FROM clip'
    # )
    for filename in os.listdir(path):
        if os.path.isfile(os.path.join(path, filename)):
            if filename.split('.')[-1] in video_ext:
                # if 'clip' in filename.split('.'):
                #     # insert clip info into database
                #     cur.execute(
                #         'INSERT INTO clip(filename, video_filename, state)'
                #         'VALUES (?, ?, ?)',
                #         (filename, '.'.join(filename.split('.')[0:-3]), 1)
                #     )
                # else:
                if 'ready' not in filename.split('.'):
                    # generate thumbnails
                    cmd = './danmuvis/tools/ffmpeg.exe -i "' + os.path.join(path, filename) + '" ' \
                          + '-ss 00:00:00.000 -vframes 1 "' + os.path.join(path, filename.replace('flv', 'jpg')) + '"'
                    print(cmd)
                    subprocess.call(cmd, shell=False)

                    # inject metadata
                    new_filename = filename[0:-4] + '.ready.flv'
                    cmd = './danmuvis/tools/yamdi.exe -i "' + os.path.join(path, filename) \
                          + '" -o "' + os.path.join(path, new_filename) + '"'
                    print(cmd)
                    subprocess.call(cmd, shell=False)

                    # replace old file
                    os.remove(os.path.join(path, filename))
                    filename = new_filename

                # insert video info into database
                cur.execute(
                    'INSERT INTO video(filename, title, streamer, date)'
                    'VALUES (?, ?, ?, ?)',
                    (filename,
                     filename.split('.')[0],
                     filename.split('.')[1],
                     filename.split('.')[2]
                     )
                )
            elif filename.split('.')[-1] in danmaku_ext:
                if 'ready' not in filename.split('.'):
                    d = Danmaku(filename, path)
                    d.generateHighlight()
                    d.generateASS()
                    os.rename(os.path.join(path, filename), os.path.join(path, filename[0:-4] + '.ready.xml'))

    cur.execute("SELECT filename FROM clip WHERE video_filename NOT IN (SELECT filename FROM video)")
    for row in cur.fetchall():
        remove_clip(row['filename'])

    db.commit()
    pass


@click.command('update-files')
@click.option('-p', '--path')
@with_appcontext
def update_files_command(path=None):
    if path is not None:
        set_path(path)
    update_files()
    click.echo('File updated.')


def init_app(app):
    app.cli.add_command(update_files_command)


@bp.route('/video_list', methods=('POST',))
def get_video_list():
    keyword = request.form.get('keyword', '')
    streamer = request.form.get('streamer', '')
    dateFrom = request.form.get('dateFrom', '')
    dateTo = request.form.get('dateTo', '')
    cur = get_db().cursor()
    cur.execute(
        "CREATE TEMP TABLE video AS SELECT * FROM video"
    )

    if len(keyword) > 0:
        cur.execute(
            "DELETE from temp.video"
            " WHERE filename NOT LIKE '%" + keyword + "%'"
        )
    if len(streamer) > 0:
        cur.execute(
            "DELETE from temp.video"
            " WHERE streamer <> '" + streamer + "'"
        )
    if len(dateFrom) > 0:
        cur.execute(
            "DELETE from temp.video"
            " WHERE date < '" + dateFrom + "'"
        )
    if len(dateTo) > 0:
        cur.execute(
            "DELETE from temp.video"
            " WHERE date > '" + dateTo + "'"
        )

    cur.execute(
        "select filename, streamer, date from temp.video"
    )
    video_list = list(map(lambda row: list(row), cur.fetchall()))
    return jsonify(video_list)


@bp.route('/streamer_list', methods=('POST',))
def get_streamer_list():
    cur = get_db().cursor()
    cur.execute(
        "SELECT DISTINCT streamer FROM video"
    )
    streamer_list = list(map(lambda row: list(row), cur.fetchall()))
    return jsonify(streamer_list)


@bp.route('/clip_list', methods=('POST',))
def get_clip_list():
    keyword = request.form.get('keyword', '')
    video_filename = request.form.get('video_filename', '')
    state = request.form.get('state', '')
    cur = get_db().cursor()
    cur.execute(
        "CREATE TEMP TABLE clip AS SELECT * FROM clip"
    )

    if len(keyword) > 0:
        cur.execute(
            "DELETE from temp.clip"
            " WHERE filename NOT LIKE '%" + keyword + "%'"
        )
    if len(video_filename) > 0:
        cur.execute(
            "DELETE from temp.clip"
            " WHERE video_filename <> '" + video_filename + "'"
        )
    if len(state) > 0:
        cur.execute(
            "DELETE from temp.clip"
            " WHERE state <> " + state + ""
        )

    cur.execute(
        "select start, end, state, filename from temp.clip"
    )
    clip_list = list(map(
        lambda row: {"range": [row["start"], row["end"]], "state": row["state"], "filename": row["filename"]},
        cur.fetchall()
        )
    )
    return jsonify(clip_list)


def has_video(filename):
    cur = get_db().cursor()
    return cur.execute("SELECT * FROM video WHERE filename='" + filename + "'").fetchone() is not None


def has_clip(filename):
    cur = get_db().cursor()
    return cur.execute("SELECT * FROM clip WHERE filename='" + filename + "'").fetchone() is not None


def clip_state(filename):
    cur = get_db().cursor()
    row = cur.execute("SELECT * FROM clip WHERE filename='" + filename + "'").fetchone()
    if row is not None:
        return row['state']
    else:
        return -1


def valid_clip_filename(filename):
    return re.match(r'\d+\.mp4$', filename) is not None


def valid_time(time):
    return re.match(r'\d:\d\d:\d\d.\d\d\d$', time) is not None


def new_clip(filename, video_filename, start, end):
    db = get_db()
    cur = db.cursor()
    if not valid_clip_filename(filename) or not valid_time(start) or not valid_time(end) or not has_video(video_filename):
        return False
    try:
        cur.execute(
            'INSERT INTO clip(filename, video_filename, start, end, state)'
            'VALUES (?, ?, ?, ?, ?)',
            (filename, video_filename, start, end, 0)
        )
        db.commit()
    except sqlite3.IntegrityError:
        return False

    return True


def set_clip_state(filename, state=1):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "UPDATE clip SET state=" + str(state) + " WHERE filename='" + filename + "'"
    )
    db.commit()


@bp.route('/remove_clip/<string:filename>')
def remove_clip(filename):
    if clip_state(filename) != 1:
        abort(404)
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute("DELETE FROM clip WHERE filename='" + filename + "'")
        db.commit()
        os.remove(os.path.join(get_path(), filename))
    except:
        abort(404)

    return 'ok'
