import { useEffect, useState, useRef } from "react";
import { io } from "socket.io-client";
import { Canvas } from "@react-three/fiber";
import Avatar from "./Avatar";

const socket = io("http://localhost:5005"); 

export default function Visualization({ signingSpeed }: { signingSpeed: number }) {
  const [animations, setAnimations] = useState<any[]>([]);
  const [currentWord, setCurrentWord] = useState<string>("");
  const [inputText, setInputText] = useState<string>(""); // Stores user input
  const [lastInputText, setLastInputText] = useState<string>(""); // Stores last sent input

    // recording
    const [isRecording, setIsRecording] = useState(false);
    const [audioPreviewUrl, setAudioPreviewUrl] = useState<string | null>(null); 
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioChunksRef = useRef<Blob[]>([]);

  // Send input to backend when button is clicked
  const handleSendInput = () => {
    if (inputText.trim() !== "") {
      socket.emit("E-REQUEST-ANIMATION", inputText.trim()); // Send user input to backend
      setLastInputText(inputText.trim()); // Store the last input for replay
    }
  };

  // Replay the last sent input
  const handleReplay = () => {
    if (lastInputText.trim() !== "") {
      socket.emit("E-REQUEST-ANIMATION", lastInputText);
    }
  };

  // start recording
  const startRecording = async () => {
    console.log("Starting recording...");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      // clear audioChunksRef
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = event => {
        console.log("ondataavailable event:", event.data, "大小：", event.data.size);
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
  
      mediaRecorder.start(1000);
      setIsRecording(true);
      setAudioPreviewUrl(null);
    } catch (error) {
      console.error("Error accessing microphone:", error);
    }
  };
  
  // stop recording
  const stopRecording = () => {
    console.log("Stopping recording...");
    if (mediaRecorderRef.current) {
      // regiseter onstop event
      mediaRecorderRef.current.onstop = async () => {
        console.log("Recording stopped");
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        console.log("Blob:", audioBlob, "size", audioBlob.size);
        // provide a preview of the audio
        const previewUrl = URL.createObjectURL(audioBlob);
        setAudioPreviewUrl(previewUrl);

        audioChunksRef.current = [];
        const formData = new FormData();
        formData.append("file", audioBlob, "recording.webm");
        try {
          const response = await fetch("http://localhost:5005/transcribe", {
            method: "POST",
            body: formData,
          });
          const data = await response.json();
          if (data.text) {
            socket.emit("E-REQUEST-ANIMATION", data.text);
            setLastInputText(data.text);
          } else {
            console.error("Transcription error:", data.error);
          }
        } catch (error) {
          console.error("Error during transcription:", error);
        }
      };
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  useEffect(() => {
    // Listen for animation data from backend
    const handleAnimation = (data: any) => {
      console.log("Animation Data Received:", data);
      setAnimations(data);
      setCurrentWord(data[0]?.[0] || "");
    };

    socket.on("E-ANIMATION", handleAnimation);

    // Cleanup to prevent memory leaks
    return () => {
      socket.off("E-ANIMATION", handleAnimation);
    };
  }, []);

  const getNextWord = () => {
    if (animations.length > 0) {
      const nextWord = animations.shift();
      setCurrentWord(nextWord[0]);
      return nextWord[1]; // Return animation points
    }
    return null;
  };

  return (
    <div className="relative w-full h-[540px] flex flex-col items-center">
      {/* Input field and buttons */}
      <div className="mb-4 flex space-x-2">
        <input
          type="text"
          placeholder="Enter words..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          className="px-4 py-2 border rounded-md"
        />
        <button
          onClick={handleSendInput}
          className="px-4 py-2 bg-blue-500 text-white rounded-md"
        >
          Send
        </button>
        <button
          onClick={handleReplay}
          className="px-4 py-2 bg-green-500 text-white rounded-md"
          disabled={!lastInputText} // Disable button if no previous input
        >
          Replay
        </button>

        {!isRecording && (
          <button
            onClick={startRecording}
            className="px-4 py-2 bg-purple-500 text-white rounded-md"
          >
            Start Recording
          </button>
        )}
        {isRecording && (
          <button
            onClick={stopRecording}
            className="px-4 py-2 bg-red-500 text-white rounded-md"
          >
            Stop Recording
          </button>
        )}

      </div>

      {audioPreviewUrl && (
        <div className="mb-4">
          <p className="text-white">Audio Preview: </p>
          <audio src={audioPreviewUrl} controls />
        </div>
      )}

      {/* Display current word */}
      <p className="absolute z-10 text-white bottom-10 w-full flex justify-center text-4xl">
        {currentWord}
      </p>

      {/* 3D Avatar Canvas */}
      <Canvas>
        <Avatar signingSpeed={signingSpeed} getNextWord={getNextWord} />
      </Canvas>
    </div>
  );
}
