/**
 * @file frontend/src/main.jsx
 * @description This is the main entry point for the React application.
 * It initializes the React root and renders the top-level App component.
 */
import { StrictMode } from 'react'; // React's StrictMode for highlighting potential problems in an application.
import { createRoot } from 'react-dom/client'; // Method for the new React 18 root API.
import './index.css'; // Global styles for the application.
import App from './App.jsx'; // The main App component.

// Get the root DOM element where the React app will be mounted.
const rootElement = document.getElementById('root');

// Create a React root for the main application container.
// This enables React 18's concurrent features.
const root = createRoot(rootElement);

// Render the application.
// StrictMode is a wrapper component that checks for potential problems in the app during development.
// It does not render any visible UI and only runs in development mode.
root.render(
  <StrictMode>
    <App /> {/* The root component of the application. */}
  </StrictMode>,
);
