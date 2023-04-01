from motion_watcher import MotionWatcher


class TestMotionWatcher:
    def test_it_opens_video_stream_on_creation(self, mock_stream_motion_detector, mock_video_writer):
        MotionWatcher("rtsp://video:stream/uri", mock_stream_motion_detector)

        mock_stream_motion_detector.open_stream.assert_called_once_with("rtsp://video:stream/uri")
        mock_video_writer.open.assert_not_called()

    def test_it_does_nothing_when_motion_is_not_detected(self, mock_stream_motion_detector, mock_video_writer):
        stream_frame = "a frame"
        is_motion_detected = False
        mock_stream_motion_detector.get_frame_with_motion_detected.return_value = stream_frame, is_motion_detected

        motion_recorder = MotionWatcher("rtsp://video:stream/uri", mock_stream_motion_detector)

        motion_recorder._poll_motion_detector_and_record_video_when_detecting_motion()

        mock_stream_motion_detector.get_frame_with_motion_detected.assert_called_once()
        mock_video_writer.open.assert_not_called()
