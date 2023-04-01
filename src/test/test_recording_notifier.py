from freezegun import freeze_time

from recording_notifier import RecordingNotifier


class TestRecordingNotifier:
    def test_it_sends_recording_with_a_silly_caption_to_telegram_chat_when_notified(
        self, mock_telegram_bot
    ):
        recording_notifier = RecordingNotifier(
            mock_telegram_bot, telegram_chat_id="1234"
        )

        with freeze_time("2023-03-30T17:33:00+02:00"):
            recording_notifier.recording_finished("/tmp/watchbot-video.avi")

        mock_telegram_bot.send_video_to_chat.assert_called_once_with(
            "1234",
            "/tmp/watchbot-video.avi",
            caption="Movimiento detectado en el área del reloj\n30/03/2023 - 17:33",
        )
