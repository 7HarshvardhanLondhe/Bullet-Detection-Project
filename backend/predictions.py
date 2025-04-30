

import cv2
import numpy as np
import json
import sys
import os
import subprocess
from ultralytics import YOLO

# Optional fallback FFmpeg resolver
try:
    import imageio_ffmpeg as ffmpeg_helper
    ffmpeg_path = ffmpeg_helper.get_ffmpeg_exe()
except ImportError:
    ffmpeg_path = "ffmpeg"  # Must be in system PATH

# Load YOLO model
model = YOLO("best.pt")  # Replace with your model path

kalman_filters = {}
trajectories = {}
previous_positions = {}
disappeared_frames = {}

fps = 300
disappearance_threshold = 20

def create_kalman():
    kf = cv2.KalmanFilter(4, 2)
    kf.transitionMatrix = np.array([[1, 0, 1, 0],
                                    [0, 1, 0, 1],
                                    [0, 0, 1, 0],
                                    [0, 0, 0, 1]], np.float32)
    kf.measurementMatrix = np.array([[1, 0, 0, 0],
                                     [0, 1, 0, 0]], np.float32)
    kf.processNoiseCov = np.eye(4, dtype=np.float32) * 0.001
    kf.measurementNoiseCov = np.eye(2, dtype=np.float32) * 0.5
    kf.errorCovPost = np.eye(4, dtype=np.float32) * 1
    return kf

def assign_id(detections):
    bullet_ids = []
    detected_bullet_ids = set()

    for box in detections:
        x1, y1, x2, y2 = map(int, box)
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        assigned_id = None
        min_distance = 50

        for bullet_id, kf in kalman_filters.items():
            prev_x, prev_y = kf.statePre[0][0], kf.statePre[1][0]
            distance = np.sqrt((cx - prev_x) ** 2 + (cy - prev_y) ** 2)
            if distance < min_distance:
                assigned_id = bullet_id
                break

        if assigned_id is None:
            assigned_id = len(kalman_filters) + 1
            kalman_filters[assigned_id] = create_kalman()
            kalman_filters[assigned_id].statePre = np.array([[cx], [cy], [0], [0]], np.float32)
            trajectories[assigned_id] = []
            previous_positions[assigned_id] = (None, None)
            disappeared_frames[assigned_id] = 0

        bullet_ids.append((assigned_id, cx, cy, x1, y1, x2, y2))
        detected_bullet_ids.add(assigned_id)

    return bullet_ids, detected_bullet_ids

def process_video(video_path):
    cap = cv2.VideoCapture(video_path)

    os.makedirs("output", exist_ok=True)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    in_fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    temp_output = "output/temp_output.mp4"
    out = cv2.VideoWriter(temp_output, fourcc, in_fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)

        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            bullet_data, detected_bullet_ids = assign_id(boxes)

            for bullet_id, cx, cy, x1, y1, x2, y2 in bullet_data:
                kf = kalman_filters[bullet_id]
                measured = np.array([[np.float32(cx)], [np.float32(cy)]])
                kf.correct(measured)
                predicted = kf.predict()
                px, py = int(predicted[0]), int(predicted[1])

                trajectories[bullet_id].append((px, py))

                prev_x, prev_y = previous_positions[bullet_id]
                if prev_x is not None and prev_y is not None:
                    distance = np.sqrt((px - prev_x) ** 2 + (py - prev_y) ** 2)
                    speed = distance * fps
                    speed_kmh = speed * 0.02

                    angle = np.arctan2(py - prev_y, px - prev_x) * (180 / np.pi)
                    if -45 <= angle < 45:
                        direction = "Right"
                    elif 45 <= angle < 135:
                        direction = "Up"
                    elif -135 <= angle < -45:
                        direction = "Down"
                    else:
                        direction = "Left"

                    cv2.putText(frame, f"Speed: {speed_kmh:.2f} km/h", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    cv2.putText(frame, f"Direction: {direction}", (x1, y1 - 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                previous_positions[bullet_id] = (px, py)
                disappeared_frames[bullet_id] = 0

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.circle(frame, (px, py), 4, (0, 0, 255), -1)

            for bullet_id in list(disappeared_frames.keys()):
                if bullet_id not in detected_bullet_ids:
                    disappeared_frames[bullet_id] += 1
                    if disappeared_frames[bullet_id] > disappearance_threshold:
                        kalman_filters.pop(bullet_id, None)
                        trajectories.pop(bullet_id, None)
                        previous_positions.pop(bullet_id, None)
                        disappeared_frames.pop(bullet_id, None)

        out.write(frame)

    cap.release()
    out.release()

    # Encode using FFmpeg
    final_output = "output/final_output.mp4"
    try:
        subprocess.run([
            ffmpeg_path, "-y", "-i", temp_output,
            "-vcodec", "libx264", "-acodec", "aac",
            final_output
        ], check=True)
    except FileNotFoundError:
        print("⚠️ FFmpeg not found. Please install it or use 'pip install imageio-ffmpeg'.")

    # Save tracking info
    tracking_data = {
        "previous_positions": {key: list(val) if val else None for key, val in previous_positions.items()},
        "disappeared_frames": disappeared_frames
    }

    with open("output/tracking_data.json", "w") as f:
        json.dump(tracking_data, f, indent=4)

    print("✅ Processing complete. Video saved to", final_output)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python predictions.py <video_path>")
    else:
        process_video(sys.argv[1])



