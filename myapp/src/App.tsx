// src/App.tsx
import React, { useState } from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import "./App.css";
import Visualization from "./demo";
import HandSignDetection from "./detection";

export default function App() {
  const [tab, setTab] = useState<"home" | "animation" | "detection">("home");

  return (
    <Router>
      <div className="app-container">
        {tab === "home" && (
          <div className="home-content">
            <h1>Welcome to XX</h1>
            <div className="button-container">
              <Link to="/asl-animation">
                <button
                  className="action-button"
                  onClick={() => setTab("animation")}
                >
                  ASL Animation
                </button>
              </Link>
              <Link to="/hand-sign-detection">
                <button
                  className="action-button"
                  onClick={() => setTab("detection")}
                >
                  Hand Sign Detection
                </button>
              </Link>
            </div>
          </div>
        )}

        <Routes>
          <Route
            path="/asl-animation"
            element={
            <div style={{ overflow: 'hidden' }}>
            <Visualization signingSpeed={1.5} />
            </div>
          }
          />
          <Route path="/hand-sign-detection" element={<HandSignDetection />} />
        </Routes>
      </div>
    </Router>
  );
}
