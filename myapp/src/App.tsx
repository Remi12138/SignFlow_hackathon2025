import { useState } from "react";
import Visualization from "./demo";
import HandSignDetection from "./detection";  // Import the HTML page logic

export default function App() {
  const [tab, setTab] = useState<"animation" | "detection">("animation");

  return (
    <div className="app-container">
      {/* Navigation Tabs */}
      <div className="tab-menu">
        <button className={`tab ${tab === "animation" ? "active" : ""}`} onClick={() => setTab("animation")}>
          ASL Animation
        </button>
        <button className={`tab ${tab === "detection" ? "active" : ""}`} onClick={() => setTab("detection")}>
          Hand Sign Detection
        </button>
      </div>

      {/* Render the correct tab */}
      {tab === "animation" ? <Visualization signingSpeed={1.5} /> : <HandSignDetection />}
    </div>
  );
}
