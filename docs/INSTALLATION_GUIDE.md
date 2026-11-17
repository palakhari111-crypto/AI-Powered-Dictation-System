# Step-by-step installation (Windows)

1. Install Python 3.10+ from python.org. During setup, enable **Add Python to PATH**.
2. Extract the project ZIP to a simple folder, for example `C:\Projects\ai_dictation_system`.
3. Open that folder in VS Code (File > Open Folder).
4. Open Terminal > New Terminal. Confirm terminal path is the project root.
5. Run `py --version`.
6. Create the environment: `py -m venv .venv`.
7. Activate it: `.\.venv\Scripts\Activate.ps1`.
8. If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again.
9. Install dependencies: `python -m pip install --upgrade pip` then `pip install -r requirements.txt`.
10. Copy `.env.example` to `.env`. Replace SECRET_KEY with a long random string. Keep DATABASE_URL as SQLite.
11. Terminal 1: `uvicorn backend.app.main:app --reload`.
12. Visit `http://127.0.0.1:8000/health`, then `http://127.0.0.1:8000/docs`.
13. Terminal 2: activate the same environment and run `streamlit run frontend/app.py`.
14. Visit `http://localhost:8501`.
15. Register a teacher, create a classroom, register a student, join with the classroom code, publish a dictation and submit a handwritten page.

## SQLite database file
The app creates `storage/dictation.db` automatically. It is a single local file. You do not install or start a separate database server.

## Optional Tesseract OCR
Install the Tesseract OCR application separately and add its installation folder to PATH. Then restart VS Code/terminal. The Python dependency is already in requirements.txt. Tesseract is primarily a printed-text OCR baseline; handwriting accuracy may be poor. Use manual review or integrate a dedicated HTR model before claiming reliable handwriting grading.
