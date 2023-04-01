import cv2

from video.frame import Frame


class VideoWriter:
    def __init__(self):
        self._writer = None

    def open(self, output_path, width, height):
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        fps = 5
        dimensions = (width, height)
        self._writer = cv2.VideoWriter(output_path, fourcc, fps, dimensions)

    def write_frame(self, frame: Frame):
        self._writer.write(frame.get_raw())

    def close(self):
        self._writer.release()
