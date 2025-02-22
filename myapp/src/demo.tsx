import { useEffect, useState } from "react";
import { io } from "socket.io-client";
import { Canvas } from "@react-three/fiber";
import Avatar from "./Avatar";

const socket = io("http://localhost:5005"); 

export default function Visualization({ signingSpeed }: { signingSpeed: number }) {
  const [animations, setAnimations] = useState<any[]>([]);
  const [currentWord, setCurrentWord] = useState<string>("");

  useEffect(() => {
    // Emit event when component loads
    socket.emit("E-REQUEST-ANIMATION", "beautiful attention");
  
    // Listen for animation data
    const handleAnimation = (data: any) => {
      console.log("Animation Data Received:", data);
      setAnimations(data);
      setCurrentWord(data[0]?.[0] || "");
    };
  
    socket.on("E-ANIMATION", handleAnimation);
  
    // Return a cleanup function (Fixes TypeScript Error)
    return () => {
      socket.off("E-ANIMATION", handleAnimation); // Cleanup to prevent memory leaks
    };
  }, []);
  

    // useEffect(() => {
    //   const handleAnimation = (data: any) => {
    //     setAnimations(data);
    //     animationIndex.current = 0;
    //     setCurrentWord(data[0]?.[0] || "");
    //   };
    
    //   socket.on("E-ANIMATION", handleAnimation);
    
    //   return () => {
    //     socket.off("E-ANIMATION", handleAnimation); // Cleanup function
    //   };
    // }, []);
  

  const getNextWord = () => {
    if (animations.length > 0) {
      const nextWord = animations.shift();
      setCurrentWord(nextWord[0]);
      return nextWord[1]; // Return animation points
    }
    return null;
  };

  return (
    <div className="relative w-full h-[540px]">
      <p className="absolute z-10 text-white bottom-10 w-full flex justify-center text-4xl">
        {currentWord}
      </p>
      <Canvas>
        <Avatar signingSpeed={signingSpeed} getNextWord={getNextWord} />
      </Canvas>
    </div>
  );
}
