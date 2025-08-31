# 🌱 Voice Carbon Footprint Tracker - EarthPrint

A web application that lets you upload or record a voice note describing your daily activities, transcribes your speech, extracts activities, and estimates your carbon footprint.

## 🚀 Features

- **Voice note upload:** Speak your activities, the app does the rest!
- **Automatic transcription:** Uses OpenAI Whisper for accurate speech-to-text.
- **Activity extraction:** NLP with spaCy to identify daily actions.
- **Carbon footprint estimation:** Calculates CO₂ emissions for your activities.
- **Modern React frontend:** Simple, clean, and responsive interface.

## 🖥️ Setup Guide For Windows (Mac Commands Included)

### 1. Prerequisites

- **Python 3.12** (Download from [python.org](https://www.python.org/downloads/))
- **Node.js (v18 or higher)** (Download from [nodejs.org](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/download/win))
- **ffmpeg**  
  - Download the latest static build from [gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)
  - Extract the ZIP, copy the `bin` folder path (e.g., `C:\ffmpeg\bin`), and add it to your Windows PATH:
    - Search “Environment Variables” in Start Menu → Edit the system environment variables → Environment Variables → Under "System variables", find `Path`, click Edit, then New, and paste the `bin` path.

### 2. Clone the Repository

```sh
git clone https://github.com/manyakalra05/earthprint.git
cd earthprint
```

### 3. Backend Setup (FastAPI + Whisper)

#### A. Create and Activate a Virtual Environment

```sh
cd backend
python -m venv venv 
venv\Scripts\activate   // source venv/bin/activate  (for mac)
```

#### B. Install Python Dependencies

```sh
pip install --upgrade pip
pip install -r requirements.txt
// download ffmpeg now as stated above,  for mac users if you have homebrew installed run -> brew install ffmpeg
python -m spacy download en_core_web_sm
```

> **If you see numpy or torch errors, run:**  
> `pip install "numpy<2.0"`

#### C. Run the Backend Server

```sh
uvicorn main:app --reload
```

- The backend will be available at [http://localhost:8000](http://localhost:8000)
- You can test endpoints at [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Frontend Setup (React)

```sh
cd ../frontend
npm install
npm start
```

- The frontend will be available at [http://localhost:3000](http://localhost:3000)

### 5. Using the App

- Open [http://localhost:3000](http://localhost:3000) in your browser.
- Upload or record a voice note describing your activities (e.g., "I drove 2 kilometers on petrol").
- The app will transcribe your speech, extract activities, and estimate your carbon footprint.

## 🛠️ Troubleshooting & FAQ

- **ffmpeg not found:**  
  Make sure you added the ffmpeg `bin` folder to your Windows PATH, then restart your terminal or computer.

- **Module not found:**  
  Ensure you activated your virtual environment and installed all requirements.

- **NumPy version error:**  
  Run `pip install "numpy<2.0"`

- **CORS errors:**  
  Make sure the backend is running and CORS is enabled in `main.py`.

- **Large files or slow processing:**  
  Try with a smaller audio file first.

- **Submodule or folder errors in Git:**  
  Do not commit `venv/` or `node_modules/` folders.  
  If you see arrows on folders in GitHub, remove any nested `.git` folders and re-add as normal folders.

## 📝 .gitignore Recommendations

- In `backend/.gitignore`:
  ```
  venv/
  __pycache__/
  *.pyc
  ```

- In `frontend/.gitignore`:
  ```
  node_modules/
  build/
  ```

## 🌍 Deploying Online

- Deploy the backend (FastAPI) to a cloud VM or service (see deployment instructions).
- Deploy the frontend (React) to Vercel, Netlify, or similar.
- Update the API URL in your frontend code to point to your deployed backend.

## 🤝 Contributing

Pull requests are welcome! Please open an issue first to discuss what you would like to change.

## 📄 License

[MIT](LICENSE)

## 🙏 Credits

- [OpenAI Whisper](https://github.com/openai/whisper)
- [spaCy](https://spacy.io/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [FFmpeg](https://ffmpeg.org/)

**Enjoy tracking your carbon footprint by voice!
You can copy-paste this README into your project and adjust as needed!**

<!-- Update 2024-11-05T14:31:28+05:30 -->
<!-- Update 2024-11-05T07:24:28+05:30 -->
<!-- Update 2024-11-06T15:38:44+05:30 -->
<!-- Update 2024-11-11T13:32:03+05:30 -->
<!-- Update 2024-11-16T08:33:10+05:30 -->
<!-- Update 2024-11-16T10:44:10+05:30 -->
<!-- Update 2024-11-16T15:17:10+05:30 -->
<!-- Update 2024-11-25T08:41:17+05:30 -->
<!-- Update 2024-11-26T17:21:18+05:30 -->
<!-- Update 2024-12-28T09:34:24+05:30 -->
<!-- Update 2025-01-08T06:18:27+05:30 -->
<!-- Update 2025-01-10T06:58:28+05:30 -->
<!-- Update 2025-02-04T08:10:32+05:30 -->
<!-- Update 2025-02-04T16:29:32+05:30 -->
<!-- Update 2025-02-17T12:07:34+05:30 -->
<!-- Update 2025-02-19T10:50:35+05:30 -->
<!-- Update 2025-03-25T11:54:39+05:30 -->
<!-- Update 2025-04-19T06:39:46+05:30 -->
<!-- Update 2025-04-21T06:40:48+05:30 -->
<!-- Update 2025-04-22T08:32:49+05:30 -->
<!-- Update 2025-05-07T18:33:51+05:30 -->
<!-- Update 2025-05-10T05:38:52+05:30 -->
<!-- Update 2025-05-27T17:37:56+05:30 -->
<!-- Update 2025-05-27T18:13:56+05:30 -->
<!-- Update 2025-06-04T15:34:57+05:30 -->
<!-- Update 2025-06-20T05:45:00+05:30 -->
<!-- Update 2025-06-25T10:58:02+05:30 -->
<!-- Update 2025-06-28T06:25:02+05:30 -->
<!-- Update 2025-08-31T09:14:11+05:30 -->