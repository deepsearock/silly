#!/usr/bin/env python3
"""
rtsp_blink_power_opencv.py

RTSP → OpenCV Haar cascades blink detection → Power overlay → Sound alert via afplay.
"""

import cv2
import numpy as np
import subprocess
import sys
import time

# Constants
BLINK_CONSEC_FRAMES  = 2       # Frames eyes must stay undetected to count a blink
POWER_PER_BLINK      = 100     # Power added per blink
POWER_ALERT          = 9000    # Trigger sound when exceeded
ALERT_SOUND_PATH     = "alert.mp3"  # Your MP3 or use system sound

# Load Haar cascades (make sure these XML files are in the script directory)
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
eye_cascade  = cv2.CascadeClassifier("haarcascade_eye.xml")

def play_alert():
    # Asynchronous macOS playback
    subprocess.Popen(["afplay", ALERT_SOUND_PATH],
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)

def main(rtsp_url: str):
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        print(f"❌ Cannot open stream {rtsp_url}")
        sys.exit(1)

    # Track blink state per face rectangle
    blink_counters = {}   # face_id -> consecutive non-eye frames
    blinked        = {}   # face_id -> blink already counted this closure
    power_levels   = {}   # face_id -> power

    next_face_id = 0      # assign incremental IDs

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️  Stream ended.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        # If faces move around, we just reassign incremental IDs each frame
        # (for demo). In a real app you’d track faces via centroids.
        blink_counters.clear()
        blinked.clear()
        power_levels.setdefault(next_face_id, 0)

        for (x, y, w, h) in faces:
            face_id = next_face_id
            next_face_id += 1

            roi_gray  = gray[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray)

            # Initialize if needed
            blink_counters.setdefault(face_id, 0)
            blinked.setdefault(face_id, False)
            power_levels.setdefault(face_id, 0)

            if len(eyes) == 0:
                blink_counters[face_id] += 1
            else:
                if blink_counters[face_id] >= BLINK_CONSEC_FRAMES and not blinked[face_id]:
                    power_levels[face_id] += POWER_PER_BLINK
                    blinked[face_id] = True
                    if power_levels[face_id] > POWER_ALERT:
                        play_alert()
                blink_counters[face_id] = 0
                blinked[face_id] = False

            # Draw face box
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            # Overlay power
            text = f"⚡{power_levels[face_id]}"
            cv2.putText(frame, text, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

        cv2.imshow("Blink→Power (OpenCV)", frame)
        if cv2.waitKey(1) & 0xFF in (27, ord('q')):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python rtsp_blink_power_opencv.py rtsp://<stream_url>")
        sys.exit(1)
    main(sys.argv[1])
