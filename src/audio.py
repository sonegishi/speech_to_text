from pydub import AudioSegment
from pydub.utils import mediainfo


_FORMAT_FLAC = 'flac'

_KEY_FILENAME = 'filename'
_KEY_CHANNELS = 'channels'
_KEY_CODEC_TYPE = 'codec_type'
_KEY_DURATION = 'duration'
_KEY_DURATION_TS = 'duration_ts'
_KEY_FORMAT_NAME = 'format_name'
_KEY_SAMPLE_RATE = 'sample_rate'
_KEY_SIZE = 'size'


class Audio(object):

    def __init__(self, file_path):
        self._filename = None

        self._channels = None
        self._codec_type = None
        self._duration = None
        self._duration_ts = None
        self._format_name = None
        self._sample_rate = None
        self._size = None

        self._set_info(file_path=file_path)

    @property
    def filename(self):
        return self._filename

    @property
    def channels(self):
        return self._channels

    @property
    def codec_type(self):
        return self._codec_type

    @property
    def duration(self):
        return self._duration

    @property
    def duration_ts(self):
        return self._duration_ts

    @property
    def format_name(self):
        return self._format_name

    @property
    def sample_rate(self):
        return self._sample_rate

    @property
    def size(self):
        return self._size

    def __repr__(self):
        return self.__string()

    def __str__(self):
        return self.__string()

    def __string(self):
        return f'filename: {self._filename}, channels: {self._channels}, codec_type: {self._codec_type}, duration: {self._duration}, duration_ts: {self._duration_ts}, format_name: {self._format_name}, sample_rate: {self._sample_rate}, size: {self._size}'

    def _set_info(self, file_path):
        info = mediainfo(file_path)

        self._filename = str(info[_KEY_FILENAME])
        self._channels = int(info[_KEY_CHANNELS])
        self._codec_type = str(info[_KEY_CODEC_TYPE])
        self._duration = float(info[_KEY_DURATION])
        self._duration_ts = int(info[_KEY_DURATION_TS])
        self._format_name = str(info[_KEY_FORMAT_NAME])
        self._sample_rate = int(info[_KEY_SAMPLE_RATE])
        self._size = int(info[_KEY_SIZE])

    def to_flac(self, export_file_path=None):
        """

        Args:
            export_file_path: Exporting file path.

        Returns:
            target_path: Target path.

        Raises:
            None.
        """

        sound = AudioSegment.from_file(self._filename)
        # if sr:
        #     sound = sound.set_frame_rate(sr)
        # if db:
        #     change_dBFS = db - sound.dBFS
        #     sound = sound.apply_gain(change_dBFS)
        sound.export(export_file_path, _FORMAT_FLAC)
