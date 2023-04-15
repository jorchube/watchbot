import cv2
import numpy as np
from video.frame import Frame


class MotionDetector:
    def __init__(self) -> None:
        self._current_frame = None
        self._previous_frame = None

    def feed_frame(self, frame):
        self._previous_frame = self._current_frame
        self._current_frame = frame

    def is_there_motion_in_frame(self) -> bool:
        if self._previous_frame is None:
            return False

        return _FrameDelta(self._previous_frame, self._current_frame).is_significative()

    def get_frame_with_motion_highlights(self):
        frame_delta = _FrameDelta(self._previous_frame, self._current_frame)
        return frame_delta.copy_frame_with_deltas_drawn_as_bounding_boxes(self._current_frame)


class _FrameDelta:
    def __init__(self, frame1, frame2):
        timestamp_mask = cv2.imread("timestamp-mask.png")
        self._diff_threshold = 20
        self._significative_diff_area = 25

        raw_frame1 = cv2.bitwise_and(frame1.get_raw(), timestamp_mask)
        raw_frame2 = cv2.bitwise_and(frame2.get_raw(), timestamp_mask)

        raw_diff = self._diff(raw_frame1, raw_frame2)
        self._significative_contours = self._get_contours(
            raw_diff, min_contour_area=self._significative_diff_area
        )

    def copy_frame_with_deltas_drawn_as_bounding_boxes(self, frame):
        frame_copy = frame.copy()

        for contour in self._significative_contours:
            self._draw_contour_bounds_on_frame(contour, frame_copy.get_raw())

        return frame_copy

    def is_significative(self):
        return len(self._significative_contours) > 0

    def _diff(self, frame1, frame2):
        gaussian_kernel_size = (5, 5)

        f1 = self._get_raw_grayscale(frame1)
        f2 = self._get_raw_grayscale(frame2)
        soft_f1 = cv2.GaussianBlur(src=f1, ksize=gaussian_kernel_size, sigmaX=0)
        soft_f2 = cv2.GaussianBlur(src=f2, ksize=gaussian_kernel_size, sigmaX=0)

        diff = cv2.absdiff(src1=soft_f1, src2=soft_f2)
        return diff

    def _get_raw_grayscale(self, frame):
        return cv2.cvtColor(src=frame, code=cv2.COLOR_RGB2GRAY)

    def _draw_contour_bounds_on_frame(self, contour, raw_frame):
        (x, y, width, height) = cv2.boundingRect(contour)
        cv2.rectangle(
            img=raw_frame,
            pt1=(x, y),
            pt2=(x + width, y + height),
            color=(0, 0, 255),
            thickness=1,
        )

    def _get_contours(self, raw_diff, min_contour_area=100):
        kernel = np.ones((5, 5))
        dilated_diff = cv2.dilate(raw_diff, kernel, 1)
        success, threshold_frame = cv2.threshold(
            src=dilated_diff,
            thresh=self._diff_threshold,
            maxval=255,
            type=cv2.THRESH_BINARY,
        )
        if not success:
            return list()

        contours, _ = cv2.findContours(
            image=threshold_frame,
            mode=cv2.RETR_EXTERNAL,
            method=cv2.CHAIN_APPROX_SIMPLE,
        )
        significative_contours = list(
            filter(
                lambda contour: cv2.contourArea(contour) >= min_contour_area, contours
            )
        )

        return significative_contours
