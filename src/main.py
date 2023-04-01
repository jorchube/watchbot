import logging
from configuration import Configuration
from motion_watcher import MotionWatcher
from recording_notifier import RecordingNotifier
from telegram.bot import Bot
from video.stream_motion_detector import StreamMotionDetector
from video.video_writer import VideoWriter


LOGLEVEL = logging.DEBUG


def run(configuration: Configuration):
    motion_watcher = MotionWatcher(
        video_stream_uri=configuration.VIDEO_STREAM_URI,
        stream_motion_detector=StreamMotionDetector(),
        video_writer=VideoWriter()
    )
    recording_notifier = RecordingNotifier(
        telegram_bot=Bot(configuration.TELEGRAM_BOT_AUTH_TOKEN),
        telegram_chat_id=configuration.TELEGRAM_CHAT_ID
    )

    motion_watcher.install_recording_finished_callback(recording_notifier.recording_finished)
    motion_watcher.start()

if __name__ == "__main__":
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s: %(message)s",
        level=LOGLEVEL,
        handlers=[logging.FileHandler("watchbot.log"), logging.StreamHandler()],
    )

    configuration = Configuration("configuration.json")
    run(configuration)
