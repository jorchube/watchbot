class MotionWatcher:
    def __init__(self, video_stream_uri, stream_motion_detector) -> None:
        self._stream_motion_detector = stream_motion_detector
        self._stream_motion_detector.open_stream(video_stream_uri)

    def _poll_motion_detector_and_record_video_when_detecting_motion(self):
        frame, is_motion_detected = self._stream_motion_detector.get_frame_with_motion_detected()
