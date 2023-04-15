from unittest import mock
import numpy as np
import pytest

from video.frame import Frame


@pytest.fixture
def a_frame():
    return Frame(np.zeros((500, 500, 3), dtype = "uint8"))


@pytest.fixture
def a_different_frame():
    return Frame(np.ones((500, 500, 3), dtype = "uint8")*255)


@pytest.fixture
def mock_stream_motion_detector():
    return mock.MagicMock()


@pytest.fixture
def mock_stream_reader():
    _mock = mock.MagicMock()
    _mock.get_stream_width.return_value = 640
    _mock.get_stream_height.return_value = 480
    _mock.get_stream_framerate.return_value = 24
    return _mock


@pytest.fixture
def mock_video_writer():
    return mock.MagicMock()


@pytest.fixture
def mock_telegram_bot():
    return mock.MagicMock()
