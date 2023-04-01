from datetime import datetime, timedelta
from typing import Callable

from video.stream_motion_detector import StreamMotionDetector
from video.video_writer import VideoWriter


class MotionWatcher:
    _RECORDING_DURATION_SECONDS = 10
    _RECORDING_COOLDOWN_MINUTES = 3
    _RECORDING_OUTPUT_PATH = "/tmp/watchbot-video.avi"

    def __init__(self, video_stream_uri: str, stream_motion_detector: StreamMotionDetector, video_writer: VideoWriter) -> None:
        self._stream_motion_detector = stream_motion_detector
        self._video_writer = video_writer

        self._dont_start_recording_until = datetime.min
        self._keep_recording_until = None
        self._recording_finished_callback = lambda _: None

        self._state = _MotionWatcherState.WATCHING
        self._stream_motion_detector.open_stream(video_stream_uri)

    def install_recording_finished_callback(self, callback: Callable[[str], None]) -> None:
        self._recording_finished_callback = callback

    def start(self):
        while True:
            self._poll_motion_detector_and_record_video_when_detecting_motion()

    def _poll_motion_detector_and_record_video_when_detecting_motion(self):
        frame, is_motion_detected = self._stream_motion_detector.get_frame_with_motion_detected()

        if self._should_start_recording(is_motion_detected):
            self._start_recording()

        if self._is_recording():
            if self._should_stop_recording():
                self._stop_recording()
                return
            self._video_writer.write_frame(frame)

    def _start_recording(self):
        width = self._stream_motion_detector.get_stream_width()
        height = self._stream_motion_detector.get_stream_height()
        self._video_writer.open(self._RECORDING_OUTPUT_PATH, width, height)

        self._keep_recording_until = datetime.now() + timedelta(seconds=self._RECORDING_DURATION_SECONDS)
        self._state = _MotionWatcherState.RECORDING

    def _should_start_recording(self, is_motion_detected):
        return is_motion_detected and not self._is_recording() and self._recording_cooldown_finished()

    def _is_recording(self):
        return self._state == _MotionWatcherState.RECORDING

    def _should_stop_recording(self):
        return self._recording_duration_reached()

    def _recording_duration_reached(self):
        return datetime.now() > self._keep_recording_until

    def _recording_cooldown_finished(self):
        return datetime.now() > self._dont_start_recording_until

    def _stop_recording(self):
        self._state = _MotionWatcherState.WATCHING
        self._dont_start_recording_until = datetime.now() + timedelta(minutes=self._RECORDING_COOLDOWN_MINUTES)
        self._video_writer.close()
        self._recording_finished_callback(self._RECORDING_OUTPUT_PATH)


class _MotionWatcherState:
    WATCHING = "watching"
    RECORDING = "recording"
