# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Speech to Text
#
# https://www.mitsue.co.jp/service/audio_and_video/audio_production/narrators_sample.html

import os
import sys
from moviepy.editor import *
from google.cloud import storage
from google.cloud import speech_v1p1beta1
from google.cloud.speech_v1p1beta1 import enums

# GCS: us-central1 (Iowa)
service_account_path = '../service-account.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path


def _speech_to_text(storage_uri):
    """
    Performs synchronous speech recognition on an audio file

    Args:
      storage_uri URI for audio file in Cloud Storage, e.g. gs://[BUCKET]/[FILE]
    """

    client = speech_v1p1beta1.SpeechClient()

    language_code = 'ja-JP'

    sample_rate_hertz = 44100

    encoding = enums.RecognitionConfig.AudioEncoding.MP3
    config = {
        'language_code': language_code,
        'sample_rate_hertz': sample_rate_hertz,
        'encoding': encoding,
    }
    audio = {'uri': storage_uri}

    response = client.recognize(config, audio)
    return response


def _upload_blob(bucket_name, source_file_name, destination_blob_name):
    """
    Uploads a file to the bucket.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(f'File {source_file_name} uploaded to {destination_blob_name}')


def _delete_blob(bucket_name, blob_name):
    """
    Deletes a blob from the bucket.
    """
    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()

    print(f'Blob {blob_name} deleted.')


def convert_mp4_to_mp3(mp4_file_path, export_file_path): 
    video = VideoFileClip(mp4_file_path)
    video.audio.write_audiofile(export_file_path)


def convert_speech_to_text(bucket_name, source_file_name, destination_blob_name, text_file_name):
    _upload_blob(bucket_name, mp3_file_path, destination_blob_name)

    storage_uri = f'gs://{bucket_name}/{destination_blob_name}'
    responses = _speech_to_text(storage_uri)
    for result in responses.results:
        alternative = result.alternatives[0]
        print(f'Transcript: {alternative.transcript}')
        break

    _delete_blob(bucket_name, destination_blob_name)

    with open(text_file, 'w') as f:
        f.write(alternative.transcript)
    print(f'File {text_file} created.')


mp4_file_path = '../data/sample.mp4'
mp3_file_path = sys.argv[1]

if mp3_file_path:
#     convert_mp4_to_mp3(mp4_file_path, mp3_file_path)
    bucket_name = 'negishi'
    destination_blob_name = 'sample.mp3'
    text_file = '../out/sample.txt'
    convert_speech_to_text(bucket_name, mp3_file_path, destination_blob_name, text_file)
