"""
Face authentication module for Jarvis.
Uses OpenCV for webcam capture and face_recognition for comparison.

Reference photo: engine/data/owner.jpg
Run capture_face.py first to create the reference photo.
"""

import os
import time

FACE_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OWNER_PHOTO_PATH = os.path.join(FACE_DATA_DIR, "owner.jpg")

# How many frames to try for recognition
MAX_ATTEMPTS = 60          # ~5 seconds at 12fps
RECOGNITION_TOLERANCE = 0.5  # lower = stricter (0.4–0.6 is good)


def _load_face_recognition():
    """Import face_recognition lazily (it's slow to import)."""
    try:
        import face_recognition
        return face_recognition
    except ImportError:
        print("[FaceAuth] face_recognition library not installed.")
        return None


def has_reference_photo() -> bool:
    """Check if the owner reference photo exists."""
    return os.path.isfile(OWNER_PHOTO_PATH)


def authenticate(on_progress=None) -> bool:
    """
    Open webcam, try to match owner's face.
    
    Args:
        on_progress: optional callback(str) for status updates
    
    Returns:
        True if face matched, False otherwise.
    """
    fr = _load_face_recognition()
    if fr is None:
        # If library not available, skip auth
        if on_progress:
            on_progress("Face recognition unavailable, skipping...")
        return True

    if not has_reference_photo():
        if on_progress:
            on_progress("No reference photo found. Run capture_face.py first.")
        return True   # Fail open if no photo exists yet

    try:
        import cv2
    except ImportError:
        if on_progress:
            on_progress("OpenCV not available, skipping face auth...")
        return True

    # Load reference encoding
    try:
        owner_image = fr.load_image_file(OWNER_PHOTO_PATH)
        owner_encodings = fr.face_encodings(owner_image)
        if not owner_encodings:
            if on_progress:
                on_progress("No face found in reference photo.")
            return True
        owner_encoding = owner_encodings[0]
    except Exception as e:
        print(f"[FaceAuth] Error loading reference photo: {e}")
        return True

    # Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        if on_progress:
            on_progress("Webcam not accessible. Skipping authentication.")
        return True

    if on_progress:
        on_progress("Scanning face...")

    matched = False
    attempts = 0

    try:
        while attempts < MAX_ATTEMPTS:
            ret, frame = cap.read()
            if not ret:
                break

            # Resize for speed
            small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

            face_locations = fr.face_locations(rgb, model="hog")
            if face_locations:
                face_encodings = fr.face_encodings(rgb, face_locations)
                for encoding in face_encodings:
                    results = fr.compare_faces([owner_encoding], encoding, tolerance=RECOGNITION_TOLERANCE)
                    if results[0]:
                        matched = True
                        break

            if matched:
                break

            attempts += 1
            time.sleep(0.1)
    finally:
        cap.release()

    return matched


def capture_and_save(save_path: str = OWNER_PHOTO_PATH) -> bool:
    """
    Capture a photo from the webcam and save as reference.
    Returns True on success.
    """
    try:
        import cv2
    except ImportError:
        print("[FaceAuth] OpenCV not installed.")
        return False

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[FaceAuth] Cannot open webcam.")
        return False

    print("Webcam opened. Look at the camera...")
    time.sleep(1.5)   # let camera warm up

    ret, frame = cap.read()
    cap.release()

    if ret:
        cv2.imwrite(save_path, frame)
        print(f"[FaceAuth] Photo saved to: {save_path}")
        return True
    else:
        print("[FaceAuth] Failed to capture frame.")
        return False
