from unittest import mock
import pytest


@pytest.fixture
def mock_stream_motion_detector():
    return mock.MagicMock()


@pytest.fixture
def mock_video_writer():
    return mock.MagicMock()
