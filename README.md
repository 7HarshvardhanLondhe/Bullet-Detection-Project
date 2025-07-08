# 🔫 Bullet Detection Project

This project detects bullets in a video using a YOLO model and Kalman filtering. The system is built with a ReactJS frontend and a Python Flask backend. MongoDB is used for storing logs or detection data.

## 🧠 Project Features

- 🎯 Bullet detection in uploaded video using YOLOv5
- 📈 Tracking with Kalman Filter
- 📂 Upload and preview video via React frontend
- 📬 Backend API using Flask
- 💾 Optional MongoDB integration for storing detection results
- 📁 Organized output (video with bounding boxes + JSON tracking data)

---

## 🚀 Tech Stack

| Layer        | Tech                          |
|--------------|-------------------------------|
| Frontend     | ReactJS, Bootstrap            |
| Backend      | Flask (Python)                |
| Machine Learning | YOLOv5, OpenCV, Kalman Filter |
| Database     | MongoDB (optional)            |

---

## 📁 Folder Structure

project_bullet/
├── backend/
│ ├── app.py # Flask backend
│ ├── yolo_model/ # YOLO model weights and config
│ ├── output/
│ │ ├── temp_output.mp4 # Processed video
│ │ └── tracking_data.json # JSON output from tracking
│ └── ...
├── frontend/
│ ├── public/
│ ├── src/
│ │ ├── components/
│ │ └── App.js
│ └── ...
├── Bullet_Detection_Project.docx
├── README.md
└── package.json (React dependencies)

yaml
Copy code

---

## 🔧 Setup Instructions

### 1. 📦 Backend Setup (Flask + YOLO)

``bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
python app.py
Make sure YOLO weights (e.g., yolov5s.pt) are present in yolo_model/.

2. 💻 Frontend Setup (React)
``bash
Copy code
cd frontend
npm install
npm start
This runs the React app at http://localhost:3000

🧪 Usage
Open the React app in browser.

Upload a video file.

Click Detect.

The backend processes it and returns:

Processed video with detected bullets.

JSON tracking data.

🗃️ MongoDB 
You can configure MongoDB connection inside the Flask backend (app.py) to log detections or user sessions.
