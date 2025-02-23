import { useRef, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export default function HandSignDetection({ setTab }: { setTab: (tab: "home") => void }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [prediction, setPrediction] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const navigate = useNavigate();

  useEffect(() => {
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (error) {
        console.error("Error accessing webcam:", error);
      }
    };

    startCamera();

    return stopCamera; // Stops camera when leaving the page
  }, []);

  const stopCamera = () => {
    if (videoRef.current?.srcObject) {
      (videoRef.current.srcObject as MediaStream)
        .getTracks()
        .forEach((track) => track.stop());
      videoRef.current.srcObject = null;
    }
  };

  const handleReturnHome = () => {
    stopCamera(); // Stop the camera
    setTab("home"); // Update tab state
    navigate("/"); // Navigate home
  };

  const captureImage = async () => {
    if (!canvasRef.current || !videoRef.current) return;

    const context = canvasRef.current.getContext("2d");
    if (!context) return;

    // Define crop area (red frame box)
    const x = 220;
    const y = 160;
    const width = 200;
    const height = 200;

    // Draw the cropped area from the video feed onto the canvas
    context.drawImage(videoRef.current, x, y, width, height, 0, 0, width, height);

    // Convert the cropped area to a Base64 string
    const imageData = canvasRef.current.toDataURL("image/jpeg");

    try {
      setLoading(true);
      const response = await fetch("http://localhost:8088/predict", {
        method: "POST",
        body: JSON.stringify({ image: imageData }),
        headers: { "Content-Type": "application/json" },
      });

      if (!response.ok) throw new Error("Failed to fetch prediction");

      const data = await response.json();
      setPrediction(data.prediction);
    } catch (error) {
      console.error("Error predicting sign:", error);
      setPrediction("Error predicting sign:" + error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center space-y-4">
      <h1 className="text-2xl font-bold">ASL Hand Sign Detection</h1>

      {/* Video Container */}
      <div className="relative w-[960px] h-[540px]">
        <video
          ref={videoRef}
          width="960"
          height="540"
          autoPlay
          className="absolute top-0 left-0 w-full h-full border border-gray-400"
        />

        {/* Red Frame */}
        <div
          className="absolute border-4 border-red-500"
          style={{
            top: "140px",
            left: "220px",
            width: "200px",
            height: "200px",
            zIndex: 10,
            position: "absolute",
            border: "4px solid red",
          }}
        ></div>
      </div>

      {/* Hidden Canvas */}
      <canvas ref={canvasRef} width="200" height="200" style={{ display: "none" }}></canvas>

      {/* Buttons */}
      <div className="flex space-x-4">
        <button
          onClick={captureImage}
          className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
          disabled={loading}
        >
          {loading ? "Predicting..." : "Predict Sign"}
        </button>

        {/* Return to Home Button */}
        <button
          onClick={handleReturnHome}
          className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600"
        >
          Return to Home
        </button>
      </div>
      
      {/* Prediction Result */}
      <p className="text-xl font-semibold">
        Prediction: <span className="text-blue-600">{prediction || "Waiting for input..."}</span>
      </p>
    </div>
  );
}
