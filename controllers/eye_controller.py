"""
Eye gesture controller using MediaPipe Face Mesh
Detects:
✅ Double Blink 👁👁
✅ Left Wink 😉
✅ Right Wink 😉
"""

import cv2
import mediapipe as mp
import time
import math

class EyeController:
    def __init__(self, detection_confidence=0.7, tracking_confidence=0.7):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )

        # Gesture states
        self.double_blink_detected = False
        self.left_wink_detected = False
        self.right_wink_detected = False

        # Blink timing
        self.last_blink_time = 0
        self.blink_interval = 0.5  # seconds for double blink

    def process(self, frame):
        """
        Process frame to detect eye gestures
        """
        if frame is None or frame.size == 0:
            print("[WARNING] Empty frame received in EyeController. Skipping.")
            self._reset_gestures()
            return frame

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        h, w, _ = frame.shape
        self._reset_gestures()

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark

            def landmark_to_pixel(lm_id):
                lm = landmarks[lm_id]
                return int(lm.x * w), int(lm.y * h)

            try:
                # 🎯 Eye landmarks
                left_eye_top = landmark_to_pixel(159)
                left_eye_bottom = landmark_to_pixel(145)
                right_eye_top = landmark_to_pixel(386)
                right_eye_bottom = landmark_to_pixel(374)

                # 📏 Eye aspect ratios
                left_eye_ratio = self._euclidean_distance(left_eye_top, left_eye_bottom)
                right_eye_ratio = self._euclidean_distance(right_eye_top, right_eye_bottom)

                # 🪜 Dynamic threshold (based on face height)
                face_height = self._euclidean_distance(landmark_to_pixel(10), landmark_to_pixel(152))
                eye_threshold = face_height * 0.018  # 1.8% of face height

                # 👁 Blink & Wink Detection
                left_eye_closed = left_eye_ratio < eye_threshold
                right_eye_closed = right_eye_ratio < eye_threshold

                current_time = time.time()

                # 👁👁 Double Blink
                if left_eye_closed and right_eye_closed:
                    if (current_time - self.last_blink_time) < self.blink_interval:
                        self.double_blink_detected = True
                        print("[INFO] Double Blink Detected")
                    self.last_blink_time = current_time

                # 😉 Left Wink
                elif left_eye_closed and not right_eye_closed:
                    self.left_wink_detected = True
                    print("[INFO] Left Wink Detected")

                # 😉 Right Wink
                elif right_eye_closed and not left_eye_closed:
                    self.right_wink_detected = True
                    print("[INFO] Right Wink Detected")

                # 🔵 Debug landmarks (optional)
                # cv2.circle(frame, left_eye_top, 4, (255, 0, 0), cv2.FILLED)
                # cv2.circle(frame, left_eye_bottom, 4, (255, 0, 0), cv2.FILLED)
                # cv2.circle(frame, right_eye_top, 4, (0, 0, 255), cv2.FILLED)
                # cv2.circle(frame, right_eye_bottom, 4, (0, 0, 255), cv2.FILLED)

            except Exception as e:
                print(f"[ERROR] Eye landmark processing failed: {e}")
                self._reset_gestures()

        return frame

    def get_double_blink(self):
        """Returns True if double blink detected"""
        return self.double_blink_detected

    def get_left_wink(self):
        """Returns True if left wink detected"""
        return self.left_wink_detected

    def get_right_wink(self):
        """Returns True if right wink detected"""
        return self.right_wink_detected

    def _euclidean_distance(self, point1, point2):
        """
        Calculate distance between two (x, y) points
        """
        x1, y1 = point1
        x2, y2 = point2
        return math.hypot(x2 - x1, y2 - y1)

    def _reset_gestures(self):
        """Reset gesture states"""
        self.double_blink_detected = False
        self.left_wink_detected = False
        self.right_wink_detected = False
