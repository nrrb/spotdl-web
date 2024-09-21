import boto3
from celery import Celery
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from loguru import logger
import json
import os
import re
from db import connect_to_db
import subprocess

S3_BUCKET_NAME = 'nrrb-music-downloader'

app = Flask(__name__, static_folder='frontend/dist', static_url_path='/')
CORS(app)
celery = Celery(app.name, backend='redis://localhost:6379/0', broker='redis://localhost:6379/0')

conn = connect_to_db()
s3_client = boto3.client('s3')

def is_valid_spotify_url(spotify_url):
    # URL should look like this:
    # https://open.spotify.com/track/0OtHWXvDph6gelVHNMjf1D?si=ea0d789e6e224a8e
    url_pattern = r'^https:\/\/open\.spotify\.com\/track\/[a-zA-Z0-9]{22}\?si=[a-zA-Z0-9]{16}$'
    if not re.match(url_pattern, spotify_url):
        logger.debug('Invalid Spotify URL', spotify_url)
        return False
    logger.debug('Valid Spotify URL', spotify_url)
    return True

def extract_track_id(spotify_url):
    pattern = r'https:\/\/open\.spotify\.com\/track\/([a-zA-Z0-9]{22})\?si=[a-zA-Z0-9]{16}'
    match = re.search(pattern, spotify_url)
    if match:
        return match.group(1)
    else:
        return None

@celery.task
def get_song_info(spotify_url):
    song_id = extract_track_id(spotify_url)
    info_file = f"songinfo/{song_id}.spotdl"
    spotdl_command = ['spotdl', 'save', spotify_url, '--save-file', info_file]
    logger.debug('Running spotdl command in get_song_info', spotdl_command)
    subprocess.run(spotdl_command)
    with open(info_file, 'r') as f:
        song_info = json.load(f)
    return song_info[0]

@celery.task
def download_song(spotify_url):
    song_info = get_song_info(spotify_url)
    subprocess.run(['spotdl', spotify_url])
    mp3_file = f"{song_info['artist']} - {song_info['name']}.mp3"
    logger.debug('Uploading file to S3', mp3_file)
    s3_client.upload_file(mp3_file, S3_BUCKET_NAME, mp3_file)
    s3_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{mp3_file}"
    os.remove(mp3_file)
    return s3_url

@app.route('/', methods=['GET'])
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/get-song-info', methods=['POST'])
def get_song_info_index():
    if request.method == 'POST':
        request_data = request.get_json()
        spotify_url = request_data['spotify_url']
        if not is_valid_spotify_url(spotify_url):
            logger.error('Invalid Spotify URL', spotify_url)
            return jsonify({'error': 'Invalid Spotify URL'})
        task = get_song_info.delay(spotify_url)
        return jsonify({'task_id': task.id}), 202


@app.route('/start-download', methods=['POST'])
def start_download():
    if request.method == 'POST':
        request_data = request.get_json()
        spotify_url = request_data['spotify_url']
        if not is_valid_spotify_url(spotify_url):
            logger.error('Invalid Spotify URL', spotify_url)
            return jsonify({'error': 'Invalid Spotify URL'})
        task = download_song.delay(spotify_url)
        return jsonify({"task_id": task.id}), 202

@app.route('/task/song_info/<task_id>', methods=['GET'])
def task_status_song_info(task_id):
    task = get_song_info.AsyncResult(task_id)
    if task.state == 'PENDING':
        logger.debug('Task is pending')
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        logger.debug('Task is not failure')
        response = {
            'state': task.state,
            'result': task.result
        }
    else:
        logger.debug('Task is failure')
        response = {
            'state': task.state,
            'status': str(task.info)
        }
    return jsonify(response)

@app.route('/task/download/<task_id>', methods=['GET'])
def task_status_download(task_id):
    task = download_song.AsyncResult(task_id)
    if task.state == 'PENDING':
        logger.debug('Task is pending')
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        logger.debug('Task is not failure')
        response = {
            'state': task.state,
            'result': task.result
        }
    else:
        logger.debug('Task is failure')
        response = {
            'state': task.state,
            'status': str(task.info)
        }
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True) 