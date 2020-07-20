### Speech to Text
#
# https://www.mitsue.co.jp/service/audio_and_video/audio_production/narrators_sample.html

import os
import sys
import time

from google.oauth2 import service_account
from google.cloud import storage
from google.cloud import speech_v1 as speech
from google.cloud.speech_v1 import enums
# from google.cloud.speech_v1p1beta1 import enums

from audio import Audio

_ENCODING = 'utf-8'

_LANGUAGE_CODE = 'ja-JP'

_FORMAT_TXT = 'txt'
_FORMAT_M4A = 'm4a'
_FORMAT_FLAC = 'flac'

_EXTENSION_FORMAT_TXT = '.' + _FORMAT_TXT
_EXTENSION_FORMAT_FLAC = '.' + _FORMAT_FLAC

_AUDIO_ENCODING_FLAC = enums.RecognitionConfig.AudioEncoding.FLAC
_AUDIO_ENCODING_LINEAR16 = enums.RecognitionConfig.AudioEncoding.LINEAR16

_KEY_ENCODING = 'encoding'
_KEY_SAMPLE_RATE_HERTZ = 'sample_rate_hertz'
_KEY_LANGUAGE_CODE = 'language_code'
_KEY_ENABLE_AUTO_PUCTUATION = 'enable_automatic_punctuation'
_KEY_DIARIZATION_CONFIG = 'diarization_config'
_KEY_ENABLE_SPEAKER_DIARIZATION = 'enable_speaker_diarization'
_KEY_MIN_SPEAKER_COUNT = 'min_speaker_count'
_KEY_MAX_SPEAKER_COUNT = 'max_speaker_count'
_KEY_USE_ENHANCED = 'use_enhanced'
_KEY_URI = 'uri'

_CURR_DIRECTORY_PATH = os.path.dirname(os.path.abspath(__file__))
_DATA_DIRECTORY_PATH \
    = os.path.abspath(os.path.join(_CURR_DIRECTORY_PATH,
                                   '..',
                                   'data'))
_OUT_DIRECTORY_PATH \
    = os.path.abspath(os.path.join(_CURR_DIRECTORY_PATH,
                                   '..',
                                   'out'))                             


class SpeechToText(object):

    def __init__(self, project, credential, bucket_name):
        self._project = project

        self._speech_client = speech.SpeechClient(credentials=service_account.Credentials.from_service_account_file(credential))
        self._storage_client = storage.Client(project=project,
                                              credentials=service_account.Credentials.from_service_account_file(credential))

        self._bucket_name = project + '-' + bucket_name
        self._storage_uri = None

        self._audio = None
        self._texts = None

        self._check_bucket()

    def _check_bucket(self):
        bucket = self._storage_client.bucket(bucket_name=self._bucket_name)

        if not bucket.exists():
            bucket.create()
            print(f'New bucket {bucket} created.')

    def _get_storage_uri(self, destination_blob_name):
        return f'gs://{self._bucket_name}/{destination_blob_name}'

    def _upload_blob(self, source_file_path):
        """Uploads a file to the bucket.

        Args:
            bucket_name: Bucket name.
            source_file_name: Source file name.
            destination_blob_name: Destination blob name.

        Returns:
            None.

        Raises:
            None.
        """

        if os.path.exists(source_file_path) and os.path.isfile(source_file_path):
            destination_blob_name = os.path.basename(source_file_path)

            bucket = self._storage_client.bucket(self._bucket_name)
            blob = bucket.blob(destination_blob_name)

            blob.upload_from_filename(source_file_path)

            print(f'File {destination_blob_name} uploaded to {blob.path}')
        else:
            error_message = f'{source_file_path} does not exist.'
            raise FileNotFoundError(error_message)

    def _delete_blob(self, source_file_path):
        """Deletes a blob from the bucket.

        Args:
            source_file_path: Source file path.

        Returns:
            None.

        Raises:
            None.
        """

        if os.path.exists(source_file_path) and os.path.isfile(source_file_path):
            destination_blob_name = os.path.basename(source_file_path)

            bucket = self._storage_client.bucket(self._bucket_name)
            blob = bucket.blob(destination_blob_name)

            blob.delete()

            print(f'Blob {destination_blob_name} deleted.')
        else:
            error_message = f'{source_file_path} does not exist.'
            raise FileNotFoundError(error_message)

    def _convert_speech_to_text_by_api(self, storage_uri):
        """Transcribes a long audio file using asynchronous speech recognition.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.
        """

        config = {
            _KEY_ENCODING: _AUDIO_ENCODING_FLAC,
            # _KEY_SAMPLE_RATE_HERTZ: _SAMPLE_RATE_HERTZ,
            _KEY_LANGUAGE_CODE: _LANGUAGE_CODE,
            _KEY_ENABLE_AUTO_PUCTUATION: True,
            _KEY_DIARIZATION_CONFIG: {
                _KEY_ENABLE_SPEAKER_DIARIZATION: True,
                _KEY_MIN_SPEAKER_COUNT: 2,
                _KEY_MAX_SPEAKER_COUNT: 3,
            },
            _KEY_USE_ENHANCED: True,
        }
        audio = {_KEY_URI: storage_uri}

        operation = self._speech_client.long_running_recognize(config, audio)

        def callback(operation_future):
            result = operation_future.result()
            progress = response.metadata.progress_percent
            print(result)

        operation.add_done_callback(callback)

        try:
            progress = 0

            while progress < 100:
                try:
                    progress = operation.metadata.progress_percent
                    print(f'Progress: {progress}%')
                except:
                    pass
                finally:
                    time.sleep(5)
        except NameError:
            pass
        except Exception as error:
            error_message = f'Error: {error}'
            print(error_message)
            raise error_message
        finally:
            print('Waiting for operation to complete...')
            response = operation.result()
            print('Operation done.')

        return response

    def _convert_speech_to_text(self, storage_uri):
        """Converts speech to text.

        Args:
            storage_uri: Storage URI.

        Returns:
            None.

        Raises:
            None.
        """

        responses = self._convert_speech_to_text_by_api(storage_uri)
        texts = [result.alternatives[0].transcript for result in responses.results]
        self._texts = '\n\n'.join(texts)

    def run(self, source_file_path):
        audio = Audio(file_path=source_file_path)

        base_name = os.path.basename(audio.filename)
        file_name_wo_ext = base_name.split(os.extsep)[0]
        export_file_name = file_name_wo_ext + _EXTENSION_FORMAT_FLAC
        export_file_dir_path = os.path.split(audio.filename)[0]
        export_file_path = os.path.join(export_file_dir_path, export_file_name)

        audio.to_flac(export_file_path=export_file_path)

        # if audio.channels != 1:
        #     print('Must use single channel (mono) audio.')
        #     print(f'Number of channels: {audio.channels}')
        #     sys.exit()

        self._upload_blob(source_file_path=export_file_path)

        destination_blob_name = os.path.basename(export_file_path)
        storage_uri = self._get_storage_uri(destination_blob_name)
        self._convert_speech_to_text(storage_uri)

        self._delete_blob(source_file_path=export_file_path)
        os.remove(export_file_path)

    def export(self, file_path):
        with open(file_path, 'w', encoding=_ENCODING) as f:
            f.write(self._texts)
        print(f'File {file_path} created.')


def main(argv):
    """Local Test Environment"""

    import argparse

    def _create_argument_parser():
        parser = argparse.ArgumentParser()

        parser.add_argument('-p',
                            '--project',
                            type=str,
                            required=True,
                            help='Project ID')
        parser.add_argument('--credential',
                            type=str,
                            required=True,
                            help='Credential')
        parser.add_argument('--bucket-name',
                            type=str,
                            required=True,
                            help='Bucket name')
        parser.add_argument('--audio-file',
                            type=str,
                            required=True,
                            help='Audio file')

        return parser

    parser = _create_argument_parser()

    args = parser.parse_args(sys.argv[1:])

    project = args.project
    credential = args.credential
    bucket_name = args.bucket_name
    audio_file = args.audio_file

    print(f'project: {project}')
    print(f'credential: {credential}')
    print(f'bucket_name: {bucket_name}')
    print(f'audio_file: {audio_file}')

    speech_to_text = SpeechToText(project=project,
                                  credential=credential,
                                  bucket_name=bucket_name)

    speech_to_text.run(source_file_path=audio_file)

    export_file_name = os.path.splitext(os.path.basename(audio_file))[0] + _EXTENSION_FORMAT_TXT
    export_file_path = os.path.join(_OUT_DIRECTORY_PATH, export_file_name)
    speech_to_text.export(file_path=export_file_path)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
