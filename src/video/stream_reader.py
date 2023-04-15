import cv2

from video.frame import Frame


class StreamReaderOpenStreamError(Exception):
    pass

class StreamReaderGetFrameError(Exception):
    pass

class StreamReader:
    def __init__(self):
        self._stream = None

    def open_stream(self, stream_uri):
        api = cv2.CAP_ANY
        parameters = [
            cv2.CAP_PROP_READ_TIMEOUT_MSEC, 3000,
            cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 3000
        ]
        self._stream = cv2.VideoCapture(stream_uri, api, parameters)

        if self._stream.isOpened() is False:
            raise StreamReaderOpenStreamError(f"Failed to open stream")

    def is_stream_open(self):
        if self._stream is None:
            return False

        return self._stream.isOpened()

    def close_stream(self):
        self._stream.release()

    def get_stream_width(self):
        return int(self._stream.get(cv2.CAP_PROP_FRAME_WIDTH))

    def get_stream_height(self):
        return int(self._stream.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def get_stream_framerate(self):
        return int(self._stream.get(cv2.CAP_PROP_FPS))

    def get_frame(self):
        read_successful, raw_frame = self._stream.read()

        if read_successful is False:
            raise StreamReaderGetFrameError(f"Failed to read frame")

        return Frame(raw_frame)
