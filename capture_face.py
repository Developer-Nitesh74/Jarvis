"""
Jarvis Face Setup — run this ONCE to capture your face photo.

Usage:
    py -3.12 capture_face.py

This will:
1. Open your webcam
2. Show a live preview
3. When you press SPACE or after 3 seconds, save your photo to engine/data/owner.jpg
"""

import cv2
import os
import time

SAVE_PATH = os.path.join(os.path.dirname(__file__), "engine", "data", "owner.jpg")

def capture():
    os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Cannot open webcam. Please check your camera connection.")
        return False

    print("=" * 50)
    print("  JARVIS FACE SETUP")
    print("=" * 50)
    print(f"  Camera opened successfully.")
    print(f"  Look directly at the camera.")
    print(f"  Press SPACE to capture, or wait 5 seconds.")
    print(f"  Press Q to quit without saving.")
    print("=" * 50)

    start_time = time.time()
    captured = False
    countdown = 5

    while True:
        ret, frame = cap.read()
        if not ret:
            print("ERROR: Failed to read from webcam.")
            break

        elapsed = time.time() - start_time
        remaining = max(0, countdown - int(elapsed))

        # Draw overlay
        display = frame.copy()
        h, w = display.shape[:2]

        # Countdown circle guide
        cv2.circle(display, (w // 2, h // 2), 130, (0, 170, 255), 2)

        # Countdown text
        cv2.putText(display, f"Auto-capture in: {remaining}s",
                    (w // 2 - 160, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 170, 255), 2)
        cv2.putText(display, "SPACE = Capture now | Q = Quit",
                    (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        cv2.imshow("Jarvis Face Setup — Look at the camera", display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord(' ') or elapsed >= countdown:
            # Save the clean frame (not the annotated one)
            cv2.imwrite(SAVE_PATH, frame)
            print(f"\n✓ Face photo saved to: {SAVE_PATH}")
            print("  You can now run: py -3.12 main.py")
            captured = True
            break
        elif key == ord('q'):
            print("\nSetup cancelled.")
            break

    cap.release()
    cv2.destroyAllWindows()
    return captured


if __name__ == "__main__":
    success = capture()
    if success:
        print("\n✓ Face authentication is set up!")
        print("  Run 'py -3.12 main.py' to start Jarvis.")
    else:
        print("\n✗ Face setup incomplete.")
        print("  You can still run Jarvis — face auth will be skipped.")
    input("\nPress Enter to exit...")
