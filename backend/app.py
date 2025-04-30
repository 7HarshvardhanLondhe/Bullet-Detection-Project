
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from gridfs import GridFS
from bson.objectid import ObjectId
import subprocess
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)


app.config["MONGO_URI"] = "mongodb://localhost:27017/bullet_detection"
mongo = PyMongo(app)
fs = GridFS(mongo.db)


UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.route('/predict', methods=['POST'])
def predict():
    if 'video' not in request.files:
        return jsonify({'error': 'No video uploaded'}), 400

    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    

    # Save uploaded video 
    filename = secure_filename(str(uuid.uuid4()) + ".mp4")
    video_path = os.path.join(UPLOAD_FOLDER, filename)
    video_file.save(video_path)


    try:
        subprocess.run(['python', 'predictions.py', video_path], check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Prediction failed', 'details': str(e)}), 500


    #for storing in G
    final_output_path = os.path.join(OUTPUT_FOLDER, 'final_output.mp4')
    if not os.path.exists(final_output_path):
        return jsonify({'error': 'Output video not found'}), 500

    with open(final_output_path, 'rb') as processed_video:
        video_id = fs.put(processed_video, filename=filename, metadata={
            'original_filename': video_file.filename,
            'content_type': 'video/mp4'
        })



    os.remove(video_path)
    os.remove(final_output_path)

    return jsonify({
        'video_id': str(video_id),
        'message': 'Video processed and stored successfully'
    })


@app.route('/video/<video_id>', methods=['GET'])
def get_video(video_id):
    try:
        video = fs.get(ObjectId(video_id))
        return send_file(video, mimetype='video/mp4')
    except:
        return jsonify({'error': 'Video not found'}), 404
    

@app.route('/videos', methods=['GET'])
def list_videos():
    videos = []
    for file in fs.find():
        videos.append({
            'id': str(file._id),
            'filename': file.filename,
            'upload_date': file.upload_date,
            'length': file.length
        })
    return jsonify(videos)


if __name__ == '__main__':
    app.run(debug=True, port=5000)

























