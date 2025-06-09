# Header Component Documentation

This document provides an overview of the `Header` component located in `frontend/src/components/App/Header.jsx`. This component serves as the main header for the AI Lie Detector application.

---

## Purpose

The `Header` component is responsible for displaying the application's branding, including the title and a descriptive subtitle. It provides a consistent top section for the application interface. In its current implementation, it is primarily a static presentational component.

---

## Key Props Accepted

The `Header` component currently does not accept any specific props. It is a self-contained presentational component.

---

## Static Content Rendered

The component renders the following static content:
*   **Application Title**:
    *   An `<h1>` element displaying "🎙️ NoLyan".
    *   The title has significant styling applied, including a large font size (`text-5xl`), bold weight (`font-bold`), and a gradient text color effect (`bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent`).
    *   It also has a bottom margin (`mb-3`).
*   **Subtitle**:
    *   A `<p>` element displaying "Advanced voice analysis with AI-powered deception detection".
    *   Styled with `text-gray-300` for color and `text-lg` for font size.

---

## Interactive Elements

The current version of the `Header` component does not contain any interactive elements such as navigation links, buttons, or theme switchers. It is purely for display.

---

## UI Components Used

The `Header` component uses standard HTML elements (`div`, `h1`, `p`) for its structure. It does not utilize any custom sub-components from the `@/components/ui` directory or other libraries directly within its own rendering logic. Styling is achieved through Tailwind CSS classes.

---

## Structure and Styling

*   **Outer Container (`div`)**:
    *   Classes: `bg-black/20 backdrop-blur-sm border-b border-white/10`
    *   This creates a semi-transparent black background with a backdrop blur effect, and a subtle bottom border.
*   **Inner Container (`div`)**:
    *   Classes: `max-w-7xl mx-auto px-6 py-6`
    *   This centers the content within a maximum width, providing horizontal and vertical padding.
*   **Text Alignment (`div`)**:
    *   Classes: `text-center`
    *   Centers the `h1` title and `p` subtitle.

---
