
class Frame:
    def __init__(self, stream_frame):
        self._frame = stream_frame

    def get_raw(self):
        return self._frame

    def copy(self):
        return Frame(self._frame.copy())
