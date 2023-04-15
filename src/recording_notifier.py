from datetime import datetime
import logging
from zoneinfo import ZoneInfo
from telegram.bot import Bot


class RecordingNotifier:
    def __init__(self, telegram_bot: Bot, telegram_chat_id: int) -> None:
        self._telegram_bot = telegram_bot
        self._telegram_chat_id = telegram_chat_id

    def recording_finished(self, recording_file_path: str) -> None:
        caption = self._generate_video_notification_caption()
        self._telegram_bot.send_video_to_chat(
            self._telegram_chat_id, recording_file_path, caption=caption
        )

        logging.info(f"Sent video {recording_file_path} to chat {self._telegram_chat_id}")

    def _generate_video_notification_caption(self):
        now = datetime.now(tz=ZoneInfo("Europe/Madrid"))
        now_formatted = now.strftime("%d/%m/%Y - %H:%M")
        return f"Motion detected\n{now_formatted}"
