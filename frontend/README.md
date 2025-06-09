# AI Lie Detector UI

This is the frontend for the AI Lie Detector application. It provides a user interface for interacting with the AI-powered lie detection system.

## Key Technologies

- **React:** A JavaScript library for building user interfaces.
- **Vite:** A fast build tool and development server for modern web projects.
- **Tailwind CSS:** A utility-first CSS framework for rapid UI development.
- **shadcn/ui:** A collection of reusable UI components built with Radix UI and Tailwind CSS.

## Setup and Running

To set up and run the frontend locally, follow these steps:

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   This will typically start the application on `http://localhost:5173`.

## Project Structure

The frontend project is structured as follows:

- **`src/components/`**: Contains all React components.
    - **`App/`**: Houses the main application components, such as:
        - `Header.tsx`: The application header.
        - `ControlPanel.tsx`: Components for managing audio input and analysis.
        - `ResultsDisplay.tsx`: Components for showing the lie detection results.
    - **`ui/`**: Contains reusable UI elements, primarily from the shadcn/ui library.
- **`src/hooks/`**: Includes custom React hooks used for managing state and side effects. This can include hooks for:
    - Audio processing and recording.
    - Handling analysis results from the backend.
    - Session management.
- **`src/assets/`**: Stores static assets like images, custom fonts, etc., that are imported into components.
- **`public/`**: Contains static assets that are served directly by the development server and are copied to the build output. This is suitable for files like `favicon.ico` or `robots.txt`.

## Backend Interaction

The frontend application interacts with a backend service built with Python and FastAPI. This backend is responsible for the core AI lie detection logic, audio processing, and analysis. The frontend sends requests to and receives responses from this backend to provide the user with the analysis results.
