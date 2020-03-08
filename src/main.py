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
import time
from moviepy.editor import *
from pydub import AudioSegment
from google.cloud import storage
from google.cloud import speech_v1
from google.cloud.speech_v1 import enums
from google.cloud.speech_v1p1beta1 import enums

# GCS: us-central1 (Iowa)
service_account_path = '../service-account.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path


def _speech_to_text(storage_uri):
    """
    Transcribe a long audio file using asynchronous speech recognition

    Args:
      local_file_path Path to local audio file, e.g. /path/audio.wav
    """

    client = speech_v1.SpeechClient()

    # local_file_path = 'resources/brooklyn_bridge.raw'

    # The language of the supplied audio
    language_code = 'ja-JP'

    # Sample rate in Hertz of the audio data sent
    sample_rate_hertz = 32000

    # Encoding of audio data sent. This sample sets this explicitly.
    # This field is optional for FLAC and WAV audio formats.
    encoding = enums.RecognitionConfig.AudioEncoding.FLAC
    config = {
        'language_code': language_code,
        'sample_rate_hertz': sample_rate_hertz,
        'encoding': encoding,
    }
    audio = {'uri': storage_uri}

    operation = client.long_running_recognize(config, audio)

    print(u'Waiting for operation to complete...')
    response = operation.result()
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


def convert_m4a_flac(source_path, target_path):
    sound = AudioSegment.from_file(source_path, format='m4a')
#     if sr:
#         sound = sound.set_frame_rate(sr)
#     if db:
#         change_dBFS = db - sound.dBFS
#         sound = sound.apply_gain(change_dBFS)
    sound.export(target_path, 'flac') 


if __name__ == '__main__':
    start_time = time.time()

    audio_file_path = sys.argv[1]

    if audio_file_path:
        bucket_name = 'negishi'
        destination_blob_name = 'sample.flac'

        # Create a path to convert to a FLAC file
        flac_file_path = audio_file_path.split('.')[:-1]
        flac_file_path = '.'.join(flac_file_path) + '.flac'

        # Convert a m4a file to a flac file
        convert_m4a_flac(audio_file_path, flac_file_path)

        # Upload the converted file
        _upload_blob(bucket_name, flac_file_path, destination_blob_name)

        # Convert speech to text
        storage_uri = f'gs://{bucket_name}/{destination_blob_name}'
        responses = _speech_to_text(storage_uri)
        texts = ''
        for result in responses.results:
            alternative = result.alternatives[0]
            texts += alternative.transcript
            texts += '\n\n'

        # Delete the uploaded files
        _delete_blob(bucket_name, destination_blob_name)

        # Create a path to save the text file
        text_file_path = audio_file_path.split('/')[-1]
        text_file_path = text_file_path.split('.')[:-1]
        text_file_path = os.path.join('../out/', '.'.join(text_file_path) +'.txt')

        # Export to a text file
        with open(text_file_path, 'w') as f:
            f.write(texts)
        print(f'File {text_file_path} created.')

    print(time.time() - start_time)
