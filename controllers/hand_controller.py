"""
Hand gesture controller using MediaPipe Hands
Detects:
✅ Index finger position (for drawing)
✅ Pinch gesture (thumb + index finger) for eraser/tools
"""

import cv2
import mediapipe as mp
import math

class HandController:
    def __init__(self, max_hands=1, detection_confidence=0.7, tracking_confidence=0.7):
        """
        Initialize MediaPipe Hands
        """
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils  # For drawing landmarks
        self.index_finger_pos = None
        self.is_pinch = False
        self.prev_index_finger_pos = None  # For smoothing
        self.smoothing_factor = 0.2

    def process(self, frame):
        if frame is None or frame.size == 0:
            print("[WARNING] Empty frame received in HandController. Skipping.")
            self.index_finger_pos = None
            self.is_pinch = False
            return frame

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]  # only first hand
            self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

            h, w, _ = frame.shape
            index_tip = hand_landmarks.landmark[8]
            new_pos = (int(index_tip.x * w), int(index_tip.y * h))

            # Optional: disable smoothing to test
            # self.index_finger_pos = new_pos

            # Or smoothing only if not pinching
            if not self.is_pinch and self.prev_index_finger_pos:
                x = int(self.prev_index_finger_pos[0] * (1 - self.smoothing_factor) + new_pos[0] * self.smoothing_factor)
                y = int(self.prev_index_finger_pos[1] * (1 - self.smoothing_factor) + new_pos[1] * self.smoothing_factor)
                self.index_finger_pos = (x, y)
            else:
                self.index_finger_pos = new_pos

            self.prev_index_finger_pos = self.index_finger_pos

            thumb_tip = hand_landmarks.landmark[4]
            thumb_pos = (int(thumb_tip.x * w), int(thumb_tip.y * h))

            distance = self._euclidean_distance(self.index_finger_pos, thumb_pos)
            self.is_pinch = distance < 55  # Increased threshold

            # Debug
            # print(f"Pinch distance: {distance:.2f}, Pinch: {self.is_pinch}")

            return frame

        else:
            self.index_finger_pos = None
            self.is_pinch = False
            self.prev_index_finger_pos = None

        return frame

    def get_brush_position(self):
        """
        Return the (x, y) position of index finger tip or None if no hand detected
        """
        return self.index_finger_pos

    def get_pinch_status(self):
        """
        Return True if pinch gesture detected, else False
        """
        return self.is_pinch

    def _euclidean_distance(self, point1, point2):
        """
        Helper function to calculate Euclidean distance between two points
        """
        x1, y1 = point1
        x2, y2 = point2
        return math.hypot(x2 - x1, y2 - y1)
