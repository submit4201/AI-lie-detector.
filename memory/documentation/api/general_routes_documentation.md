# API Documentation: General Routes (`general_routes.py`)

This document provides an overview of the general API routes defined in `backend/api/general_routes.py`. These routes are typically used for health checks, basic API information, and testing purposes.

**General Purpose**: To offer utility endpoints for monitoring the API's status and for aiding in development and testing, such as providing mock data.

---

## Endpoint: `/`

*   **HTTP Method**: GET
*   **URL Path**: `/`
*   **Tags**: `General`
*   **Summary**: API Root/Health Check
*   **Description**: A basic endpoint to confirm that the API is running and responsive.
*   **Request Parameters/Body**: None.
*   **Response**:
    *   **Success (200 OK)**:
        ```json
        {
          "message": "AI Lie Detector API is running"
        }
        ```
*   **Services/Configuration Used**: None.

---

## Endpoint: `/health`

*   **HTTP Method**: GET
*   **URL Path**: `/health`
*   **Tags**: `General`
*   **Summary**: Detailed Health Check
*   **Description**: Provides a more comprehensive health status of the API, including system information, status of key services, and checks for essential environment variables.
*   **Request Parameters/Body**: None.
*   **Response**:
    *   **Success (200 OK)**: A JSON object detailing the health status.
        ```json
        {
          "status": "healthy", // or "degraded", "unhealthy"
          "timestamp": "YYYY-MM-DDTHH:MM:SS.ffffff",
          "uptime": 12345.67, // Process uptime in seconds
          "service": "AI Lie Detector API",
          "version": "1.0.0", // Static version in this implementation
          "environment": "development", // or "production", etc.
          "services": {
            "gemini_service": "available", // or "error: <message>"
            "audio_service": "available",
            "session_service": "available",
            "streaming_service": "available"
          },
          "environment_variables": {
            "gemini_api_key": "configured", // or "missing"
            "cors_origins": "configured" // or "default"
          },
          "warnings": [] // List of warning messages if status is "degraded"
        }
        ```
    *   **Error (If the health check itself fails critically)**:
        ```json
        {
          "status": "unhealthy",
          "timestamp": "YYYY-MM-DDTHH:MM:SS.ffffff",
          "error": "<error message>",
          "service": "AI Lie Detector API"
        }
        ```
*   **Key Operations**:
    *   Retrieves current time and approximate process uptime.
    *   Gets environment type from `os.getenv("ENVIRONMENT", "development")`.
    *   **Service Availability Check**: Attempts to import key functions/classes from various services (`gemini_service`, `audio_service`, `session_service`, `streaming_service`). If an import fails, it's marked as an error for that service.
    *   **Environment Variable Check**: Checks for the presence of `GEMINI_API_KEY` and `CORS_ORIGINS`.
    *   **Overall Health Determination**: Sets status to "degraded" if there are service import errors or if `GEMINI_API_KEY` is missing, and includes relevant warnings.
*   **Error Handling**: A top-level `try-except` block catches any exceptions during the health check process and returns an "unhealthy" status with the error message.

---

## Endpoint: `/test-structured-output`

*   **HTTP Method**: GET
*   **URL Path**: `/test-structured-output`
*   **Tags**: `Testing`
*   **Summary**: Test Structured Output
*   **Description**: Provides a complete, mock `AnalyzeResponse` object. This endpoint is specifically for frontend development and testing to ensure that the frontend application can correctly parse and display all fields of a typical successful analysis response.
*   **Request Parameters/Body**: None.
*   **Response**:
    *   **Success (200 OK)**: `AnalyzeResponse` (Pydantic model). The response contains a detailed, pre-defined mock data structure that mirrors a full analysis result, including transcript, audio quality, emotion analysis, linguistic analysis, risk assessment, session insights, etc.
*   **Services/Configuration Used**:
    *   Uses the `AnalyzeResponse` Pydantic model from `backend.models`.
    *   The data returned is hardcoded within the route handler.
*   **Key Operations**:
    *   Constructs a dictionary (`mock_response`) containing sample data for all fields expected in an `AnalyzeResponse`.
    *   Returns this dictionary validated and serialized through the `AnalyzeResponse` model.

---
