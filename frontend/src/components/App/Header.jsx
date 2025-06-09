import React from 'react';

/**
 * @component Header
 * @description A stateless functional component that renders the main header section for the application.
 * It displays the application title and a brief tagline.
 * This component does not receive any props.
 *
 * @returns {JSX.Element} The Header component UI.
 */
const Header = () => {
  return (
    // Outer container for the header with a semi-transparent background, backdrop blur, and bottom border.
    <div className="bg-black/20 backdrop-blur-sm border-b border-white/10">
      {/* Inner container to manage content width and padding. */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        {/* Centered text content. */}
        <div className="text-center">
          {/* Main application title with gradient text styling. */}
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent mb-3">
            🎙️ AI Lie Detector
          </h1>
          {/* Application tagline providing a brief description. */}
          <p className="text-gray-300 text-lg">Advanced voice analysis with AI-powered deception detection</p>
        </div>
      </div>
    </div>
  );
};

export default Header;
