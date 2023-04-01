import cv2

from video.frame import Frame


class VideoWriter:
    def __init__(self, output_path, width, height):
        self._width = width
        self._height = height
        self._output_path = output_path
        self._writer = None

    def open(self):
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        fps = 5
        dimensions = (self._width, self._height)
        self._writer = cv2.VideoWriter(self._output_path, fourcc, fps, dimensions)

    def write_frame(self, frame: Frame):
        self._writer.write(frame.get_raw())

    def close(self):
        self._writer.release()
