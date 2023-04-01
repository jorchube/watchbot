from unittest import mock
from freezegun import freeze_time
from motion_watcher import MotionWatcher


class TestMotionWatcher:
    def test_it_opens_video_stream_on_creation(self, mock_stream_motion_detector, mock_video_writer):
        MotionWatcher("rtsp://video:stream/uri", mock_stream_motion_detector, mock_video_writer)

        mock_stream_motion_detector.open_stream.assert_called_once_with("rtsp://video:stream/uri")
        mock_video_writer.open.assert_not_called()

    def test_it_does_nothing_when_motion_is_not_detected(self, mock_stream_motion_detector, mock_video_writer):
        stream_frame = "a frame"
        is_motion_detected = False
        mock_stream_motion_detector.get_frame_with_motion_detected.return_value = stream_frame, is_motion_detected

        motion_recorder = MotionWatcher("rtsp://video:stream/uri", mock_stream_motion_detector, mock_video_writer)
        motion_recorder._poll_motion_detector_and_record_video_when_detecting_motion()

        mock_stream_motion_detector.get_frame_with_motion_detected.assert_called_once()
        mock_video_writer.open.assert_not_called()

    def test_it_starts_recording_video_when_motion_is_detected(self, mock_stream_motion_detector, mock_video_writer):
        stream_frame = "a frame"
        is_motion_detected = True
        mock_stream_motion_detector.get_frame_with_motion_detected.return_value = stream_frame, is_motion_detected
        mock_stream_motion_detector.get_stream_width.return_value = 640
        mock_stream_motion_detector.get_stream_height.return_value = 480

        motion_recorder = MotionWatcher("rtsp://video:stream/uri", mock_stream_motion_detector, mock_video_writer)

        with freeze_time("2023-03-31T16:53:00+02:00"):
            motion_recorder._poll_motion_detector_and_record_video_when_detecting_motion()

        mock_stream_motion_detector.get_frame_with_motion_detected.assert_called_once()
        mock_video_writer.open.assert_called_once_with("/tmp/watchbot-video.avi", 640, 480)
        mock_video_writer.write_frame.assert_called_once_with("a frame")

    def test_it_keeps_recording_video_until_10_seconds_after_first_motion_detection(self, mock_stream_motion_detector, mock_video_writer):
        motion_recorder = MotionWatcher("rtsp://video:stream/uri", mock_stream_motion_detector, mock_video_writer)
        motion_detected = True
        motion_not_detected = False

        mock_stream_motion_detector.get_frame_with_motion_detected.return_value = "frame 1", motion_detected
        with freeze_time("2023-03-31T16:53:00+02:00"):
            motion_recorder._poll_motion_detector_and_record_video_when_detecting_motion()
            mock_video_writer.write_frame.assert_called_with("frame 1")
            mock_video_writer.close.assert_not_called()

        mock_stream_motion_detector.get_frame_with_motion_detected.return_value = "frame 2", motion_not_detected
        with freeze_time("2023-03-31T16:53:01+02:00"):
            motion_recorder._poll_motion_detector_and_record_video_when_detecting_motion()
            mock_video_writer.write_frame.assert_called_with("frame 2")
            mock_video_writer.close.assert_not_called()

        mock_stream_motion_detector.get_frame_with_motion_detected.return_value = "frame 3", motion_not_detected
        with freeze_time("2023-03-31T16:53:07+02:00"):
            motion_recorder._poll_motion_detector_and_record_video_when_detecting_motion()
            mock_video_writer.write_frame.assert_called_with("frame 3")
            mock_video_writer.close.assert_not_called()

        mock_video_writer.reset_mock()
        mock_stream_motion_detector.get_frame_with_motion_detected.return_value = "frame 4", motion_not_detected
        with freeze_time("2023-03-31T16:53:11+02:00"):
            motion_recorder._poll_motion_detector_and_record_video_when_detecting_motion()
            mock_video_writer.write_frame.assert_not_called()
            mock_video_writer.close.assert_called_once()

    def test_it_does_not_starts_a_recording_when_the_last_one_was_less_than_3_minutes_ago(self, mock_stream_motion_detector, mock_video_writer):
        motion_recorder = MotionWatcher("rtsp://video:stream/uri", mock_stream_motion_detector, mock_video_writer)
        stream_frame = "a frame"
        is_motion_detected = True
        mock_stream_motion_detector.get_frame_with_motion_detected.return_value = stream_frame, is_motion_detected
        mock_stream_motion_detector.get_stream_width.return_value = 640
        mock_stream_motion_detector.get_stream_height.return_value = 480

        with freeze_time("2023-03-31T16:53:00+02:00"):
            motion_recorder._poll_motion_detector_and_record_video_when_detecting_motion()
            mock_video_writer.open.assert_called_once_with("/tmp/watchbot-video.avi", 640, 480)
            mock_video_writer.write_frame.assert_called_once_with("a frame")

        mock_video_writer.reset_mock()
        with freeze_time("2023-03-31T16:53:11+02:00"):
            motion_recorder._poll_motion_detector_and_record_video_when_detecting_motion()
            mock_video_writer.write_frame.assert_not_called()
            mock_video_writer.close.assert_called_once()

        mock_video_writer.reset_mock()
        with freeze_time("2023-03-31T16:56:10+02:00"):
            motion_recorder._poll_motion_detector_and_record_video_when_detecting_motion()
            mock_video_writer.open.assert_not_called()
            mock_video_writer.write_frame.assert_not_called()

        with freeze_time("2023-03-31T16:56:12+02:00"):
            motion_recorder._poll_motion_detector_and_record_video_when_detecting_motion()
            mock_video_writer.open.assert_called_once_with("/tmp/watchbot-video.avi", 640, 480)
            mock_video_writer.write_frame.assert_called_once_with("a frame")

    def test_it_notifies_when_a_recording_has_been_done(self, mock_stream_motion_detector, mock_video_writer):
        motion_recorder = MotionWatcher("rtsp://video:stream/uri", mock_stream_motion_detector, mock_video_writer)
        stream_frame = "a frame"
        is_motion_detected = True
        mock_stream_motion_detector.get_frame_with_motion_detected.return_value = stream_frame, is_motion_detected
        mock_stream_motion_detector.get_stream_width.return_value = 640
        mock_stream_motion_detector.get_stream_height.return_value = 480

        recording_finished = mock.MagicMock()
        motion_recorder.install_recording_finished_callback(recording_finished)

        with freeze_time("2023-03-31T16:53:00+02:00"):
            motion_recorder._poll_motion_detector_and_record_video_when_detecting_motion()
            mock_video_writer.open.assert_called_once_with("/tmp/watchbot-video.avi", 640, 480)
            mock_video_writer.write_frame.assert_called_once_with("a frame")
            recording_finished.assert_not_called()

        mock_video_writer.reset_mock()
        with freeze_time("2023-03-31T16:53:11+02:00"):
            motion_recorder._poll_motion_detector_and_record_video_when_detecting_motion()
            mock_video_writer.write_frame.assert_not_called()
            mock_video_writer.close.assert_called_once()
            recording_finished.assert_called_once_with("/tmp/watchbot-video.avi")
