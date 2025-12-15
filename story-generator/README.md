# AI Story Generator

A full-stack application to generate Instagram/WhatsApp stories using Google Gemini.

## Project Structure
- `backend/`: FastAPI server that wraps the `stories.py` logic.
- `frontend/`: React + Vite application for the user interface.

## Prerequisites
- Python 3.11+
- Node.js & npm
- Google API Key (stored in `.env` in the root `ai-engineering` folder)

## How to Run

### 1. Start the Backend
Navigate to the `ai-engineering` root:
```bash
python3 story-generator/backend/main.py
```
The backend will run on `http://localhost:8000`.

### 2. Start the Frontend
Navigate to the frontend directory:
```bash
cd story-generator/frontend
npm run dev
```
The frontend will run on `http://localhost:5173`.

## Features
- **Dark Mode UI**: Premium dark aesthetic.
- **Customizable**: Choose topic, number of slides (1-5), and visual style.
- **AI-Powered**: Uses Gemini 2.0 Flash for content and Gemini 3 Pro for images.
