"""
Face gesture controller using MediaPipe Face Mesh
Detects:
✅ Mouth Open 😮
✅ Eyebrow Raise 😀 (with auto calibration)
"""

import cv2
import mediapipe as mp
import math

class FaceController:
    def __init__(self, detection_confidence=0.7, tracking_confidence=0.7):
        """
        Initialize MediaPipe Face Mesh and variables
        """
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )
        self.mouth_open = False
        self.eyebrow_raised = False

        # Calibration variables
        self.calibrated = False
        self.neutral_eyebrow_distances = []
        self.neutral_eyebrow_distance = None
        self.calibration_frames = 60  # ~2 seconds at 30fps
        self.current_frame = 0

    def process(self, frame):
        """
        Process frame to detect gestures
        """
        if frame is None or frame.size == 0:
            print("[WARNING] Empty frame received in FaceController. Skipping.")
            self.mouth_open = False
            self.eyebrow_raised = False
            return frame

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        # Reset gesture flags
        self.mouth_open = False
        self.eyebrow_raised = False

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            h, w, _ = frame.shape

            def landmark_to_pixel(lm_id):
                lm = landmarks[lm_id]
                return int(lm.x * w), int(lm.y * h)

            try:
                # 🎯 Key landmarks
                upper_lip = landmark_to_pixel(13)
                lower_lip = landmark_to_pixel(14)
                left_eyebrow_top = landmark_to_pixel(65)
                left_eye_top = landmark_to_pixel(159)
                right_eyebrow_top = landmark_to_pixel(295)
                right_eye_top = landmark_to_pixel(386)

                # 📏 Distances
                mouth_distance = self._euclidean_distance(upper_lip, lower_lip)
                left_eyebrow_dist = self._euclidean_distance(left_eyebrow_top, left_eye_top)
                right_eyebrow_dist = self._euclidean_distance(right_eyebrow_top, right_eye_top)
                avg_eyebrow_dist = (left_eyebrow_dist + right_eyebrow_dist) / 2

                face_height = self._euclidean_distance(
                    landmark_to_pixel(10),  # forehead
                    landmark_to_pixel(152)  # chin
                )

                # 🛠️ Calibration Phase
                if not self.calibrated:
                    self.neutral_eyebrow_distances.append(avg_eyebrow_dist)
                    self.current_frame += 1
                    cv2.putText(frame, f"Calibrating... {self.current_frame}/{self.calibration_frames}",
                                (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

                    if self.current_frame >= self.calibration_frames:
                        self.neutral_eyebrow_distance = sum(self.neutral_eyebrow_distances) / len(self.neutral_eyebrow_distances)
                        self.calibrated = True
                        print(f"[INFO] Calibration done. Neutral eyebrow distance: {self.neutral_eyebrow_distance:.2f}")
                else:
                    # 🎯 Detect Eyebrow Raise
                    raise_threshold = self.neutral_eyebrow_distance + (face_height * 0.02)
                    if avg_eyebrow_dist > raise_threshold:
                        self.eyebrow_raised = True

                    # 😮 Detect Mouth Open
                    mouth_threshold = face_height * 0.035
                    if mouth_distance > mouth_threshold:
                        self.mouth_open = True

                # 🔵 Debug landmarks (optional)
                # cv2.circle(frame, upper_lip, 5, (0, 255, 0), cv2.FILLED)
                # cv2.circle(frame, lower_lip, 5, (0, 255, 0), cv2.FILLED)
                # cv2.circle(frame, left_eyebrow_top, 5, (255, 0, 0), cv2.FILLED)
                # cv2.circle(frame, right_eyebrow_top, 5, (0, 0, 255), cv2.FILLED)

            except Exception as e:
                print(f"[ERROR] Landmark processing failed: {e}")
                self.mouth_open = False
                self.eyebrow_raised = False

        else:
            # No face detected → reset flags
            self.mouth_open = False
            self.eyebrow_raised = False

        return frame

    def get_mouth_status(self):
        """
        True if mouth is open
        """
        return self.mouth_open

    def get_eyebrow_status(self):
        """
        True if eyebrows are raised
        """
        return self.eyebrow_raised

    def _euclidean_distance(self, point1, point2):
        """
        Distance between two (x, y) points
        """
        x1, y1 = point1
        x2, y2 = point2
        return math.hypot(x2 - x1, y2 - y1)
