from unittest import mock
from freezegun import freeze_time
from motion_watcher import MotionWatcher
from video.motion_detector import MotionDetector


class TestMotionWatcher:
    def test_it_does_nothing_when_motion_is_not_detected(
        self, mock_stream_reader, mock_video_writer, a_frame
    ):
        motion_watcher = MotionWatcher(
            "rtsp://video:stream/uri", mock_stream_reader, MotionDetector(), mock_video_writer
        )

        mock_stream_reader.get_frame.return_value = a_frame
        motion_watcher._read_and_process_frame()

        mock_video_writer.open.assert_not_called()

        mock_stream_reader.get_frame.return_value = a_frame
        motion_watcher._read_and_process_frame()

        mock_video_writer.open.assert_not_called()

    def test_it_starts_recording_video_when_motion_is_detected(
        self, mock_stream_reader, mock_video_writer, a_frame, a_different_frame
    ):
        motion_watcher = MotionWatcher(
            "rtsp://video:stream/uri", mock_stream_reader, MotionDetector(), mock_video_writer
        )

        mock_stream_reader.get_frame.return_value = a_frame
        motion_watcher._read_and_process_frame()

        mock_video_writer.open.assert_not_called()

        mock_stream_reader.get_frame.return_value = a_different_frame
        motion_watcher._read_and_process_frame()

        mock_video_writer.open.assert_called_once_with("/tmp/watchbot-video.avi", 640, 480, 24)
        mock_video_writer.write_frame.assert_called_once()

    def test_it_keeps_recording_video_until_10_seconds_after_first_motion_detection(
        self, mock_stream_reader, mock_video_writer, a_frame, a_different_frame
    ):
        motion_watcher = MotionWatcher(
            "rtsp://video:stream/uri", mock_stream_reader, MotionDetector(), mock_video_writer
        )

        mock_stream_reader.get_frame.return_value = a_frame
        with freeze_time("2023-03-31T16:53:00+02:00"):
            motion_watcher._read_and_process_frame()

        mock_stream_reader.get_frame.return_value = a_different_frame

        with freeze_time("2023-03-31T16:53:01+02:00"):
            motion_watcher._read_and_process_frame()
            mock_video_writer.open.assert_called_once_with("/tmp/watchbot-video.avi", 640, 480, 24)
            mock_video_writer.write_frame.assert_called_once()

        mock_video_writer.open.reset_mock()

        mock_video_writer.write_frame.reset_mock()
        with freeze_time("2023-03-31T16:53:01+02:00"):
            motion_watcher._read_and_process_frame()
            mock_video_writer.open.assert_not_called()
            mock_video_writer.write_frame.assert_called_once()

        mock_video_writer.write_frame.reset_mock()
        with freeze_time("2023-03-31T16:53:09+02:00"):
            motion_watcher._read_and_process_frame()
            mock_video_writer.open.assert_not_called()
            mock_video_writer.write_frame.assert_called_once()

        mock_video_writer.write_frame.reset_mock()
        with freeze_time("2023-03-31T16:53:11+02:00"):
            motion_watcher._read_and_process_frame()
            mock_video_writer.open.assert_not_called()
            mock_video_writer.write_frame.assert_called_once()
            mock_video_writer.close.assert_called_once()

    def test_it_does_not_starts_a_new_recording_when_the_last_one_was_less_than_3_minutes_ago(
        self, mock_stream_reader, mock_video_writer, a_frame, a_different_frame
    ):
        motion_watcher = MotionWatcher(
            "rtsp://video:stream/uri", mock_stream_reader, MotionDetector(), mock_video_writer
        )

        mock_stream_reader.get_frame.return_value = a_frame
        with freeze_time("2023-03-31T16:53:00+02:00"):
            motion_watcher._read_and_process_frame()

        mock_stream_reader.get_frame.return_value = a_different_frame

        with freeze_time("2023-03-31T16:53:01+02:00"):
            motion_watcher._read_and_process_frame()
            mock_video_writer.open.assert_called_once_with("/tmp/watchbot-video.avi", 640, 480, 24)
            mock_video_writer.write_frame.assert_called_once()

        mock_video_writer.open.reset_mock()

        mock_video_writer.write_frame.reset_mock()
        with freeze_time("2023-03-31T16:53:11+02:00"):
            motion_watcher._read_and_process_frame()
            mock_video_writer.open.assert_not_called()
            mock_video_writer.write_frame.assert_called_once()
            mock_video_writer.close.assert_called_once()

        mock_video_writer.close.reset_mock()

        mock_video_writer.write_frame.reset_mock()
        mock_stream_reader.get_frame.return_value = a_frame
        with freeze_time("2023-03-31T16:53:12+02:00"):
            motion_watcher._read_and_process_frame()
            mock_video_writer.open.assert_not_called()
            mock_video_writer.write_frame.assert_not_called()
            mock_video_writer.close.assert_not_called()

        mock_stream_reader.get_frame.return_value = a_different_frame
        with freeze_time("2023-03-31T16:56:10+02:00"):
            motion_watcher._read_and_process_frame()
            mock_video_writer.open.assert_not_called()
            mock_video_writer.write_frame.assert_not_called()
            mock_video_writer.close.assert_not_called()

        mock_stream_reader.get_frame.return_value = a_frame
        with freeze_time("2023-03-31T16:56:11+02:00"):
            motion_watcher._read_and_process_frame()
            mock_video_writer.open.assert_called_once_with("/tmp/watchbot-video.avi", 640, 480, 24)
            mock_video_writer.write_frame.assert_called_once()
            mock_video_writer.close.assert_not_called()

    def test_it_notifies_when_a_recording_has_been_done(
        self, mock_stream_reader, mock_video_writer, a_frame, a_different_frame
    ):
        recording_finished_callback = mock.MagicMock()
        motion_watcher = MotionWatcher(
            "rtsp://video:stream/uri", mock_stream_reader, MotionDetector(), mock_video_writer
        )
        motion_watcher.install_recording_finished_callback(recording_finished_callback)

        mock_stream_reader.get_frame.return_value = a_frame
        with freeze_time("2023-03-31T16:53:00+02:00"):
            motion_watcher._read_and_process_frame()

        mock_stream_reader.get_frame.return_value = a_different_frame

        with freeze_time("2023-03-31T16:53:01+02:00"):
            motion_watcher._read_and_process_frame()
            mock_video_writer.open.assert_called_once_with("/tmp/watchbot-video.avi", 640, 480, 24)
            mock_video_writer.write_frame.assert_called_once()

        mock_video_writer.open.reset_mock()
        mock_video_writer.write_frame.reset_mock()
        with freeze_time("2023-03-31T16:53:11+02:00"):
            motion_watcher._read_and_process_frame()
            mock_video_writer.open.assert_not_called()
            mock_video_writer.write_frame.assert_called_once()
            mock_video_writer.close.assert_called_once()
            recording_finished_callback.assert_called_once_with("/tmp/watchbot-video.avi")
