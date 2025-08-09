import numpy as np
import cv2

class Canvas:
    def __init__(self, height=720, width=1280, bg_color=(255, 255, 255)):
        """
        Initialize the canvas with a white background by default.
        """
        self.height = height
        self.width = width
        self.bg_color = bg_color
        # Create a blank canvas filled with bg_color (white)
        self.canvas = np.full((self.height, self.width, 3), self.bg_color, dtype=np.uint8)

    def reset(self):
        """
        Clear the canvas by resetting it to the background color.
        """
        self.canvas[:] = self.bg_color

    def get_canvas(self):
        """
        Return the current canvas image.
        """
        return self.canvas

    def draw_line(self, start_point, end_point, color, thickness=15):
        """
        Draw a line on the canvas from start_point to end_point with specified color and thickness.
        """
        cv2.line(self.canvas, start_point, end_point, color, thickness)
        
    def draw_circle(self, center, radius=5, color=(0, 0, 0)):
        """
        Draw a circle on the canvas.
        """
        cv2.circle(self.canvas, center, radius, color, cv2.FILLED)