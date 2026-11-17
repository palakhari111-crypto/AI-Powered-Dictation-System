# AI-Powered Dictation System

A modular academic MVP for classroom dictation and handwritten-answer evaluation, built with **Streamlit**, **FastAPI**, **SQLAlchemy**, and **SQLite**.

## Features

- Teacher and student registration/login with hashed passwords and JWT authentication
- Classroom creation and join codes; students can join multiple classrooms
- Text-based dictation creation and publishing
- Optional text-to-speech audio generation with gTTS
- Student answer-image uploads
- OCR adapter with optional Tesseract integration
- Deterministic text comparison with mistake categories and scoring metrics
- Student reports, teacher classroom views, and weak-word aggregation
- Local SQLite database and file storage

## Technology stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend/API | FastAPI |
| Database | SQLite + SQLAlchemy |
| Authentication | JWT + password hashing |
| OCR baseline | Tesseract (optional) |
| Text-to-speech | gTTS (optional) |

## Quick start (Windows)

1. Download and extract the project archive from this repository.
2. Open a terminal in the extracted `ai_dictation_system` folder.
3. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Copy `.env.example` to `.env` and replace `SECRET_KEY` with a long random value.
6. Start the API in terminal 1:

   ```powershell
   uvicorn backend.app.main:app --reload
   ```

7. Start the Streamlit frontend in terminal 2:

   ```powershell
   streamlit run frontend/app.py
   ```

8. Open the frontend at http://localhost:8501. The API documentation is available at http://127.0.0.1:8000/docs.

See [the installation guide](docs/INSTALLATION_GUIDE.md) in the extracted project for detailed setup instructions.

## Important limitations

This repository contains an academic MVP, not a production-ready deployment. Tesseract is a general OCR baseline and may perform poorly on handwriting. Low-confidence results should be manually reviewed. A dedicated handwriting-text-recognition (HTR) model should be integrated before relying on automated handwriting grading.

Teacher source-image OCR, multi-page processing, advanced analytics, PDF/Excel exports, and adaptive practice are not represented as completed features.

## Security and data

- Never commit your real `.env`, credentials, student records, uploaded answer images, audio files, or local SQLite database.
- Configure a strong secret key before running the application.
- Add HTTPS, rate limiting, backups, audit logging, and data-retention controls before any real deployment.

## Project archive

The complete source package is provided in [`ai_dictation_system_sqlite.zip`](ai_dictation_system_sqlite.zip). It includes the backend, frontend, tests, documentation, and sample environment configuration.
