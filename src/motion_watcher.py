from datetime import datetime, timedelta
import logging
from typing import Callable
from video.motion_detector import MotionDetector

from video.stream_reader import StreamReader, StreamReaderGetFrameError, StreamReaderOpenStreamError
from video.video_writer import VideoWriter


class MotionWatcher:
    _RECORDING_DURATION_SECONDS = 20
    _RECORDING_COOLDOWN_SECONDS = 3 * 60
    _RECORDING_OUTPUT_PATH = "/tmp/watchbot-video.avi"

    def __init__(
        self,
        video_stream_uri: str,
        stream_reader: StreamReader,
        motion_detector: MotionDetector,
        video_writer: VideoWriter,
    ) -> None:
        self._stream_uri = video_stream_uri
        self._stream_reader = stream_reader
        self._motion_detector = motion_detector
        self._video_writer = video_writer

        self._dont_start_recording_until = datetime.min
        self._keep_recording_until = None
        self._recording_finished_callback = lambda _: None

        self._state = _MotionWatcherState.WATCHING

    def start(self):
        while True:
            try:
                self._run()
            except (StreamReaderOpenStreamError, StreamReaderGetFrameError) as e:
                logging.info(e)

    def _run(self):
        try:
            if self._is_recording():
                self._stop_recording()
            self._stream_reader.close_stream()
        except Exception as e:
            logging.info(f"Unable to close stream: {e}")

        self._stream_reader.open_stream(self._stream_uri)
        logging.info("Stream opened")

        while True:
            self._read_and_process_frame()

    def _read_and_process_frame(self):
        frame = self._stream_reader.get_frame()
        self._motion_detector.feed_frame(frame)

        if self._is_watching():
            if self._should_start_recording():
                self._start_recording()

        if self._is_recording():
            self._video_writer.write_frame(self._motion_detector.get_frame_with_motion_highlights())
            if self._should_stop_recording():
                self._stop_recording()

    def _is_recording(self):
        return self._state == _MotionWatcherState.RECORDING

    def _is_watching(self):
        return self._state == _MotionWatcherState.WATCHING

    def _should_start_recording(self):
        if self._dont_start_recording_until > datetime.now():
            return False

        if self._motion_detector.is_there_motion_in_frame() is False:
            return False

        return True

    def _start_recording(self):
        self._keep_recording_until = datetime.now() + timedelta(seconds=self._RECORDING_DURATION_SECONDS)
        self._state = _MotionWatcherState.RECORDING

        width = self._stream_reader.get_stream_width()
        height = self._stream_reader.get_stream_height()
        framerate = self._stream_reader.get_stream_framerate()
        self._video_writer.open(self._RECORDING_OUTPUT_PATH, width, height, framerate)

        logging.info(f"Started recording stream {self._stream_uri}")

    def _should_stop_recording(self):
        return datetime.now() >= self._keep_recording_until

    def _stop_recording(self):
        self._video_writer.close()
        self._dont_start_recording_until = datetime.now() + timedelta(seconds=self._RECORDING_COOLDOWN_SECONDS)
        self._state = _MotionWatcherState.WATCHING
        self._recording_finished_callback(self._RECORDING_OUTPUT_PATH)

        logging.info(f"Finished recording stream {self._stream_uri}")

    def install_recording_finished_callback(
        self, callback: Callable[[str], None]
    ) -> None:
        self._recording_finished_callback = callback


class _MotionWatcherState:
    WATCHING = "watching"
    RECORDING = "recording"
