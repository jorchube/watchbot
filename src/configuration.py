from dataclasses import dataclass
import json


@dataclass(init=True)
class Configuration:
    TELEGRAM_BOT_AUTH_TOKEN: str
    TELEGRAM_CHAT_ID: int
    VIDEO_STREAM_URI: str

    def __init__(self, configuration_file):
        configuration_file = self._get_file_content(configuration_file)

        self.TELEGRAM_BOT_AUTH_TOKEN = configuration_file["telegram_bot_auth_token"]
        self.TELEGRAM_CHAT_ID = configuration_file["telegram_chat_id"]
        self.VIDEO_STREAM_URI = configuration_file["video_stream_uri"]

    def _get_file_content(self, json_file_path):
        file = open(json_file_path, "r")
        content = file.read()

        json_content = json.loads(content)

        return json_content
