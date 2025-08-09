import cv2
import numpy as np
import time
import os
from drawing.canvas import Canvas
from controllers.hand_controller import HandController
from controllers.face_controller import FaceController
from controllers.eye_controller import EyeController

# 🔕 Silence MediaPipe logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'




def main():
    # 🎥 Initialize webcam
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    # ✋ Initialize controllers
    hand = HandController()
    face = FaceController()
    eye = EyeController()

    # 📝 Initialize white canvas
    canvas_obj = Canvas()

    # 🎨 Colors and brush size
    color_list = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
    color_index = 0
    current_color = color_list[color_index]
    brush_size = 15

    # ↩ Undo/Redo stacks
    stroke_history = []
    redo_stack = []

    prev_index_pos = None
    prev_eraser_pos = None
    current_stroke = []
    last_color_change_time = 0

    print("[INFO] Virtual Painter Started! Press 'Q' to quit.")

    while True:
        success, frame = cap.read()
        if not success or frame is None or frame.size == 0:
            print("[WARNING] Empty frame received. Retrying...")
            time.sleep(0.1)
            continue

        frame = cv2.flip(frame, 1)
        current_canvas = canvas_obj.get_canvas()

        try:
            # Process inputs
            frame = hand.process(frame)
            frame = face.process(frame)
            frame = eye.process(frame)

            index_pos = hand.get_brush_position()
            pinch = hand.get_pinch_status()

            if index_pos and pinch and not face.get_mouth_status():
                # Draw on webcam feed directly:
                cv2.circle(frame, index_pos, 10, current_color, cv2.FILLED)
                if prev_index_pos:
                    # Draw smooth line on webcam feed:
                    cv2.line(frame, prev_index_pos, index_pos, current_color, brush_size)

                    # Draw smooth line on your Canvas object:
                    canvas_obj.draw_line(prev_index_pos, index_pos, current_color, brush_size)

                    current_stroke.append(index_pos)

                prev_index_pos = index_pos
                prev_eraser_pos = None
            else:
                if current_stroke:
                    stroke_history.append({
                        'points': current_stroke.copy(),
                        'color': current_color
                    })
                    current_stroke = []
                prev_index_pos = None


            if face.get_mouth_status():
                cv2.putText(frame, "Eraser Mode 🧽", (50, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

                if index_pos:
                    # Erase circle on webcam feed
                    cv2.circle(frame, index_pos, 50, canvas_obj.bg_color, cv2.FILLED)

                    if prev_eraser_pos:
                        # Erase line on webcam feed
                        cv2.line(frame, prev_eraser_pos, index_pos, canvas_obj.bg_color, 50)

                        # Erase line on white canvas
                        canvas_obj.draw_line(prev_eraser_pos, index_pos, canvas_obj.bg_color, 50)

                    prev_eraser_pos = index_pos

                # Important: reset brush position to avoid conflicts
                    prev_index_pos = None    
            else:
                prev_eraser_pos = None


            # 🎨 Eyebrow Raise → Change Color
            if face.get_eyebrow_status() and not eye.get_double_blink():
                if time.time() - last_color_change_time > 1.0:  # 1 second debounce
                    color_index = (color_index + 1) % len(color_list)
                    current_color = color_list[color_index]
                    print(f"[INFO] Color changed to: {current_color}")
                    last_color_change_time = time.time()
                    cv2.putText(frame, f"Color Changed 🎨", (50, 150),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, current_color, 3)


            # 💾 Double Blink → Save & Clear
            # 🔥 Save artwork to resources/saved_artworks
            if eye.get_double_blink():
                save_dir = "resources/saved_artworks"
                os.makedirs(save_dir, exist_ok=True)  # ✅ Create folder if not exists

                filename = f"artwork_{int(time.time())}.png"
                file_path = os.path.join(save_dir, filename)

                cv2.imwrite(file_path, current_canvas)
                print(f"[INFO] Artwork saved as {file_path}")

                canvas_obj.reset()
                stroke_history.clear()
                redo_stack.clear()
                cv2.putText(frame, "Canvas Saved 💾", (50, 200),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 3)

            # 😉 Left Wink → Undo
            if eye.get_left_wink():
                print("[DEBUG] Left wink detected")  # 🔥 Debug print
                if stroke_history:
                    redo_stack.append(stroke_history.pop())
                    canvas_obj.reset()
                    for stroke in stroke_history:
                        pts, col = stroke['points'], stroke['color']
                        for i in range(1, len(pts)):
                            canvas_obj.draw_line(pts[i - 1], pts[i], col, brush_size)
                    print("[INFO] Undo Last Stroke")
                else:
                    print("[DEBUG] Nothing to undo (stroke_history empty)")

                # 😉 Right Wink → Redo
                if eye.get_right_wink():
                    print("[DEBUG] Right wink detected")  # 🔥 Debug print
                    if redo_stack:
                        stroke = redo_stack.pop()
                        stroke_history.append(stroke)
                        pts, col = stroke['points'], stroke['color']
                        for i in range(1, len(pts)):
                            canvas_obj.draw_line(pts[i - 1], pts[i], col, brush_size)
                        print("[INFO] Redo Stroke")
                    else:
                        print("[DEBUG] Nothing to redo (redo_stack empty)")


            # 🪞 Show webcam feed with overlay
            cv2.namedWindow("Webcam Feed", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Webcam Feed", 640, 720)
            cv2.moveWindow("Webcam Feed", 0, 0)
            cv2.imshow("Webcam Feed", frame)

            # 📝 Show clean whiteboard
            cv2.namedWindow("Drawing Canvas", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Drawing Canvas", 640, 720)
            cv2.moveWindow("Drawing Canvas", 650, 0)
            cv2.imshow("Drawing Canvas", current_canvas)

        except Exception as e:
            print(f"[ERROR] Processing failed: {e}")

        # 🛑 Quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[INFO] Exiting Virtual Painter...")
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
