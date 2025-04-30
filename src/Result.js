import React from "react";

function Result({ videoUrl, bullets }) {
  return (
    <div>
      <h2>Detected Bullets</h2>
      <video src={videoUrl} controls width="800" />
      <ul>
        {bullets.map((b, index) => (
          <li key={index}>
            Bullet ID: {b.id}, Speed: {b.speed} km/h, Direction: {b.direction}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Result;
