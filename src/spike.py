import cv2
from video.stream_motion_detector import StreamMotionDetector
from video.video_writer import VideoWriter



def draw_frame_in_window(frame, window):
    cv2.imshow(window, frame)
    if (cv2.waitKey(30) == 27):
        raise Exception("Exitting...")


def run():
    uri = "http://162.191.11.144:8000/-wvhttp-01-/GetOneShot?image_size=640x480&frame_count=1000000000"
    uri = "http://85.158.74.11:80/mjpg/video.mjpg"

    stream_motion_detector = StreamMotionDetector()
    stream_motion_detector.open_stream(uri)

    width = stream_motion_detector.get_stream_width()
    height = stream_motion_detector.get_stream_height()

    video_writer = VideoWriter()
    video_writer.open("/var/home/jorchube/Desktop/output.avi", width, height)

    while True:
        frame, is_motion_detected = stream_motion_detector.get_frame_with_motion_detected()
        if is_motion_detected:
            print(f">>> Motion detected")

        try:
            draw_frame_in_window(frame.get_raw(), "Stream")
        except Exception as e:
            stream_motion_detector.close_stream()
            video_writer.close()
            exit(0)

        video_writer.write_frame(frame)


if __name__ == "__main__":
    run()
