import React from 'react';
import './App.css';
import Visualization from "./demo";

function App() {
  return (
    <div className="App">
      <header className="ASL">
        <Visualization signingSpeed={10} />
      </header>
    </div>
  );
}

export default App;
