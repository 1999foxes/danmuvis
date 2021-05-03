import os
import os.path

import subprocess

import click
from flask import (
    Blueprint, request, jsonify, send_from_directory
)
from flask.cli import with_appcontext

from werkzeug.exceptions import abort

from danmuvis.auth import login_required
from danmuvis.db import get_db


bp = Blueprint('file', __name__, url_prefix='/file')

video_ext = ['flv', 'mp4', 'FLV', 'MP4']


def update_files(path=None):
    db = get_db()
    cur = db.cursor()
    if path is None:
        path = cur.execute('SELECT p from path').fetchone()['p']
    else:
        cur.execute('DELETE FROM path')
        cur.execute("INSERT INTO path(p) VALUES('" + path + "')")

    cur.execute(
        'DELETE FROM video'
    )
    cur.execute(
        'DELETE FROM clip'
    )
    for filename in os.listdir(path):
        if os.path.isfile(os.path.join(path, filename)):
            if filename.split('.')[-1] in video_ext:
                if 'clip' in filename.split('.'):
                    cur.execute(
                        'INSERT INTO clip(filename, video_filename_no_ext, state)'
                        'VALUES (?, ?, ?)',
                        (filename, '.'.join(filename.split('.')[0:3]), 1)
                    )
                else:
                    if 'metadata' not in filename.split('.'):
                        # generate thumbnails
                        cmd = './danmuvis/tools/ffmpeg.exe -i "' + os.path.join(path, filename) + '" ' \
                              + '-ss 00:00:00.000 -vframes 1 "' + os.path.join(path, filename.replace('flv', 'jpg')) + '"'
                        print(cmd)
                        subprocess.call(cmd, shell=False)

                        # inject metadata
                        new_filename = filename[0:-3] + 'metadata.flv'
                        cmd = './danmuvis/tools/yamdi.exe -i "' + os.path.join(path, filename) \
                              + '" -o "' + os.path.join(path, new_filename) + '"'
                        print(cmd)
                        subprocess.call(cmd, shell=False)

                        # replace old file
                        os.remove(os.path.join(path, filename))
                        filename = new_filename
                    cur.execute(
                        'INSERT INTO video(filename, filename_no_ext, streamer, date, title)'
                        'VALUES (?, ?, ?, ?, ?)',
                        (filename,
                         '.'.join(filename.split('.')[0:3]),
                         filename.split('.')[0],
                         filename.split('.')[1],
                         filename.split('.')[2]
                         )
                    )
    db.commit()
    pass


@click.command('update-files')
@click.option('-p', '--path')
@with_appcontext
def update_files_command(path=None):
    update_files(path)
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
    video_filename_no_ext = request.form.get('video_filename_no_ext', '')
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
    if len(video_filename_no_ext) > 0:
        cur.execute(
            "DELETE from temp.clip"
            " WHERE video_filename_no_ext <> '" + video_filename_no_ext + "'"
        )
    if len(state) > 0:
        cur.execute(
            "DELETE from temp.clip"
            " WHERE state < '" + state + "'"
        )

    cur.execute(
        "select filename, state from temp.clip"
    )
    clip_list = list(map(lambda row: list(row), cur.fetchall()))
    return jsonify(clip_list)
