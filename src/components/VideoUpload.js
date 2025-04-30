

import React, { useState, useEffect } from "react";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";



function VideoUpload() {
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [previewURL, setPreviewURL] = useState(null);
  const [processedURL, setProcessedURL] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [storedVideos, setStoredVideos] = useState([]);




  useEffect(() => {
    const fetchStoredVideos = async () => {
      try {
        const response = await axios.get("http://localhost:5000/videos");
        setStoredVideos(response.data);
      } catch (err) {
        console.error("Error fetching stored videos:", err);
      }
    };
    fetchStoredVideos();
  }, []);


//Handling
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith("video/")) {
      setSelectedVideo(file);
      setPreviewURL(URL.createObjectURL(file));
      setProcessedURL(null);
      setError("");
    } else {
      setError("Please upload a valid video file.");
      setSelectedVideo(null);
      setPreviewURL(null);
      setProcessedURL(null);
    }
  };


  //upload to backend sathi
  const uploadVideo = async () => {
    if (!selectedVideo) {
      setError("Please select a video to upload.");
      return;
    }

    const formData = new FormData();
    formData.append("video", selectedVideo);

    setLoading(true);
    setError("");

    
//mongo stored
    try {
      const response = await axios.post(
        "http://localhost:5000/predict",
        formData
      );
      



      // Get the video from MongoDB using the returned ID
      const videoURL = `http://localhost:5000/video/${response.data.video_id}`;
      setProcessedURL(videoURL);
      
      // Refresh the stored videos list
      const videosResponse = await axios.get("http://localhost:5000/videos");
      setStoredVideos(videosResponse.data);
    } catch (err) {
      console.error("Upload failed:", err);
      setError("Video processing failed. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };




  return (
    <div className="container-fluid vh-100 p-0">

     <div className="row m-0 py-3 bg-dark text-white">
        <div className="col text-center">
          <h1 className="m-0">Bullet Detection System</h1>
        </div>
      </div>

      <div className="row h-100 m-0">

        <div className="col-md-6 h-100 p-4 bg-light">
          <div className="h-100 d-flex flex-column">
            <h3 className="text-center mb-4">Original Video</h3>
            
            <div className="mb-3">
              <input
                type="file"
                accept="video/*"
                onChange={handleFileChange}
                className="form-control"
                disabled={loading}
              />
            </div>

            {previewURL ? (
              <div className="flex-grow-1 d-flex flex-column">
                <h5 className="mb-2">Preview:</h5>
                <video 
                  controls 
                  className="w-100 h-100 bg-dark"
                  style={{ maxHeight: "70vh" }}
                >
                  <source src={previewURL} type={selectedVideo?.type} />
                  Your browser does not support the video tag.
                </video>
              </div>
            ) : (
              <div className="flex-grow-1 d-flex align-items-center justify-content-center bg-secondary bg-opacity-10 rounded">
                <p className="text-muted">No video selected</p>
              </div>
            )}
          </div>
        </div>




        <div className="col-md-6 h-100 p-4">
          <div className="h-100 d-flex flex-column">
            <div className="d-flex justify-content-between align-items-center mb-4">
              <h3 className="m-0">Processed Output</h3>
              <button
                className="btn btn-primary"
                onClick={uploadVideo}
                disabled={loading || !selectedVideo}
              >
                {loading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" />
                    Processing...
                  </>
                ) : (
                  "Detect Bullets"
                )}
              </button>
            </div>

            {error && <div className="alert alert-danger">{error}</div>}

            {processedURL ? (
              <div className="flex-grow-1 d-flex flex-column">
                <h5 className="mb-2">Results:</h5>
                <video 
                  controls 
                  className="w-100 h-100 bg-dark"
                  style={{ maxHeight: "70vh" }}
                >
                  <source src={processedURL} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              </div>
            ) : (
              <div className="flex-grow-1 d-flex flex-column align-items-center justify-content-center bg-secondary bg-opacity-10 rounded">
                <div className="text-center">
                  <i className="bi bi-arrow-right-circle fs-1 text-muted mb-3"></i>
                  <p className="text-muted">
                    {selectedVideo 
                      ? "Click 'Detect Bullets' to process the video" 
                      : "Upload a video to see processed results"}
                  </p>
                </div>
              </div>
            )}


            

            {/* Stored Videos List */}
            <div className="mt-4">
              <h5>Previously Processed Videos:</h5>
              <div className="list-group">
                {storedVideos.map((video) => (
                  <a 
                    key={video.id}
                    href={`http://localhost:5000/video/${video.id}`}
                    className="list-group-item list-group-item-action"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {video.filename} - {new Date(video.upload_date).toLocaleString()}
                  </a>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default VideoUpload;

























