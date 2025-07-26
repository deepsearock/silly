#!/usr/bin/env python3
"""
rtsp_blink_power_mac.py

RTSP → FaceMesh blink detection → Power level overlay → Sound alert via `afplay` on Mac.
"""

import cv2
import mediapipe as mp
import numpy as np
import subprocess
import sys

# Constants
BLINK_THRESHOLD      = 0.20    # Eye aspect ratio under this means “closed”
BLINK_CONSEC_FRAMES  = 2       # Frames eye must stay below threshold
POWER_PER_BLINK      = 100     # Power added per blink
POWER_ALERT          = 9000    # Trigger sound when exceeded
ALERT_SOUND_PATH     = "alert.mp3"  # Place an MP3 here, or use system sound

# MediaPipe setup
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=5,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

# Indices for FaceMesh eyes
LEFT_EYE  = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362,385,387,263,373,380]

def eye_aspect_ratio(landmarks, eye_idxs, w, h):
    pts = [(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in eye_idxs]
    A = np.linalg.norm(np.array(pts[1]) - np.array(pts[5]))
    B = np.linalg.norm(np.array(pts[2]) - np.array(pts[4]))
    C = np.linalg.norm(np.array(pts[0]) - np.array(pts[3]))
    return (A + B) / (2.0 * C)

def play_alert_mac():
    # Nonblocking fire-and-forget
    subprocess.Popen(["afplay", ALERT_SOUND_PATH], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main(rtsp_url: str):
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        print(f"❌ Couldn't open stream {rtsp_url}")
        sys.exit(1)

    blink_counters = {}
    blinked        = {}
    power_levels   = {}

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️  Stream ended or failed.")
            break

        h, w, _ = frame.shape
        rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        if results.multi_face_landmarks:
            for idx, face in enumerate(results.multi_face_landmarks):
                # Compute average EAR
                left_ear  = eye_aspect_ratio(face.landmark, LEFT_EYE, w, h)
                right_ear = eye_aspect_ratio(face.landmark, RIGHT_EYE, w, h)
                ear = (left_ear + right_ear) / 2.0

                # Initialize
                blink_counters.setdefault(idx, 0)
                blinked.setdefault(idx, False)
                power_levels.setdefault(idx, 0)

                if ear < BLINK_THRESHOLD:
                    blink_counters[idx] += 1
                else:
                    if blink_counters[idx] >= BLINK_CONSEC_FRAMES and not blinked[idx]:
                        power_levels[idx] += POWER_PER_BLINK
                        blinked[idx] = True
                        if power_levels[idx] > POWER_ALERT:
                            play_alert_mac()
                    blink_counters[idx] = 0
                    blinked[idx]        = False

                # Draw box & power text
                xs = [lm.x for lm in face.landmark]
                ys = [lm.y for lm in face.landmark]
                x1, y1 = int(min(xs)*w), int(min(ys)*h)
                x2, y2 = int(max(xs)*w), int(max(ys)*h)

                cv2.rectangle(frame, (x1,y1), (x2,y2), (255,0,0), 2)
                cv2.putText(frame, f"⚡{power_levels[idx]}",
                            (x1, max(y1-10,0)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2, cv2.LINE_AA)

        cv2.imshow("Blink → Power Levels (Mac)", frame)
        if cv2.waitKey(1) & 0xFF in (27, ord('q')):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python rtsp_blink_power_mac.py rtsp://<stream_url>")
        sys.exit(1)
    main(sys.argv[1])
