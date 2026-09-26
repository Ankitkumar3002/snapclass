# SnapClass

SnapClass is an AI-powered classroom attendance system built with Python and Streamlit. It helps teachers manage subjects, share class join links, track attendance, and perform attendance verification using facial recognition and voice recognition. Students can register, enroll in classes, and view their attendance records from a single app-based interface.

This repository is a complete end-to-end prototype that combines a modern web UI with database-backed persistence and ML-based recognition pipelines.

## What this project does

SnapClass combines three core flows:

- Teacher portal for creating classes, managing course enrollment, and taking attendance
- Student portal for face-based login, profile registration, subject enrollment, and attendance records
- AI attendance recognition using face embeddings and voice embeddings

The application uses Supabase as its backend data store and stores student profiles, subject memberships, and attendance logs there.

## Key features

- Teacher authentication and registration
- Subject creation with subject codes and sections
- QR code sharing for subject join links
- Student registration with face embedding capture
- Optional voice profile registration
- Face recognition-based attendance capture
- Voice recognition-based attendance capture
- Attendance history dashboard for teachers and students
- Student enrollment via class join code
- Subject-level attendance summaries

## Architecture overview

This repository is organized around a Streamlit app and a separate Python source package:

```text
.
├── app.py                         # Application entry point
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore rules
├── src/
│   ├── components/               # Reusable UI components and dialogs
│   │   ├── dialog_add_photo.py
│   │   ├── dialog_attendance_results.py
│   │   ├── dialog_auto_enroll.py
│   │   ├── dialog_create_subject.py
│   │   ├── dialog_enroll.py
│   │   ├── dialog_share_subject.py
│   │   ├── dialog_voice_attendance.py
│   │   ├── footer.py
│   │   ├── header.py
│   │   └── subject_card.py
│   ├── database/
│   │   ├── config.py             # Supabase client setup
│   │   └── db.py                 # Database helper functions
│   ├── pipelines/
│   │   ├── face_pipeline.py      # Face detection and recognition logic
│   │   └── voice_pipeline.py     # Voice embedding and matching logic
│   ├── screens/
│   │   ├── home_screen.py        # Landing screen
│   │   ├── student_screen.py     # Student UI flow
│   │   └── teacher_screen.py     # Teacher dashboard and admin flow
│   └── ui/
│       └── base_layout.py        # Shared styling and layout helpers
└── README.md
```

## Tech stack

### Frontend / app layer
- Python 3
- Streamlit
- Custom HTML/CSS styling via `st.markdown` and layout helpers

### Backend / storage
- Supabase
- PostgreSQL-backed tables managed through Supabase client APIs

### AI / ML
- dlib
- face_recognition_models
- scikit-learn
- librosa
- resemblyzer
- NumPy
- Pillow

### Utility libraries
- pandas
- segno (QR code generation)
- bcrypt (password hashing)
- numpy

## How the system works

### 1. Teacher flow
Teachers can:
- sign up with a username and password
- log in to the teacher dashboard
- create subjects with a subject code, name, and section
- share a class code or generated QR to students
- upload classroom photos for AI-based attendance capture
- view attendance records grouped by date and subject

The teacher dashboard is implemented in `src/screens/teacher_screen.py` and uses helper functions such as:
- `create_teacher()`
- `teacher_login()`
- `get_teacher_subjects()`
- `get_attendance_for_teacher()`

### 2. Student flow
Students can:
- register using their face photo and optional voice sample
- log in using face recognition
- enroll in subjects by entering the teacher-provided subject code
- view enrolled classes and attendance status
- leave a subject if needed

The student flow is implemented in `src/screens/student_screen.py` and interacts with database functions such as:
- `create_student()`
- `get_all_students()`
- `get_student_subjects()`
- `get_student_attendance()`
- `unenroll_student_to_subject()`

### 3. Face recognition attendance
The face recognition pipeline is handled by `src/pipelines/face_pipeline.py`.

It does the following:
- loads dlib face detection and recognition models
- extracts face embeddings for each detected face in a classroom image
- trains an SVM classifier from stored student face embeddings
- predicts the matching student ID
- compares the prediction against stored embeddings using distance metrics
- marks a student as present if the similarity threshold passes

The core function is `predict_attendance(class_image_np)`, which returns detected student IDs and class-related metadata.

### 4. Voice recognition attendance
The voice pipeline is defined in `src/pipelines/voice_pipeline.py`.

It uses:
- `VoiceEncoder` from resemblyzer
- `librosa` to load and process audio
- cosine-like similarity between stored and newly extracted voice embeddings

The system identifies likely speakers by comparing embeddings against enrolled students that already have a voice profile.

### 5. Database operations
The `src/database/db.py` module acts as the project’s main data access layer.

It manages:
- teacher creation and login
- student creation and lookup
- subject creation
- subject enrollment and unenrollment
- attendance log insertion
- attendance queries for teacher and student dashboards

The database config is initialized in `src/database/config.py` using Supabase credentials loaded from:
- `st.secrets`
- environment variables `SUPABASE_URL` and `SUPABASE_KEY`

## Entry point

The main app is launched through:

```bash
streamlit run app.py
```

`app.py` checks the session state and routes the user to either:
- `home_screen()`
- `teacher_screen()`
- `student_screen()`

It also checks for a URL `join-code` query parameter for automatic student enrollment flows.

## Setup and installation

### Prerequisites

- Python 3.9+
- pip
- A Supabase project with tables configured for the app
- Access to a working camera and microphone during runtime

### Clone the repository

```bash
git clone https://github.com/Ankitkumar3002/snapclass.git
cd snapclass
```

### Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
# or .venv\Scripts\activate  # Windows
```

### Install dependencies

```bash
pip install -r requirements.txt
```

Important note: this repo includes heavy ML dependencies such as `dlib-bin` and `face_recognition_models`. Installation may require system libraries depending on the OS. On Linux, you may need packages such as:

```bash
sudo apt-get update
sudo apt-get install -y build-essential cmake libgl1 libglib2.0-0
```

If you are on a constrained or Windows environment, you may need to troubleshoot these dependencies separately before running the app.

## Configuration

### Supabase setup

The app expects a valid Supabase project and connection credentials.

Add environment variables:

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"
```

Or configure Streamlit secrets in `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"
```

This is read in `src/database/config.py`.

## Expected database schema

The code references tables with names such as:

- `teachers`
- `students`
- `subjects`
- `subject_students`
- `attendance_logs`

The application assumes these tables exist in Supabase and that rows contain the fields used by the code, including:

### `teachers`
- `teacher_id` (usually auto-generated)
- `username`
- `password`
- `name`

### `students`
- `student_id` (usually auto-generated)
- `name`
- `face_embedding`
- `voice_embedding`

### `subjects`
- `subject_id`
- `subject_code`
- `name`
- `section`
- `teacher_id`

### `subject_students`
- `student_id`
- `subject_id`

### `attendance_logs`
- `student_id`
- `subject_id`
- `timestamp`
- `is_present`

## Running the app

From the project root:

```bash
streamlit run app.py
```

Then open the URL shown by Streamlit in the terminal (typically `http://localhost:8501`).

## Typical user flow

### Teacher workflow
1. Register teacher account
2. Create one or more subjects
3. Share subject code / QR link
4. Use AI attendance tools from the teacher dashboard
5. Review attendance summaries for each class

### Student workflow
1. Register profile using face photo and optional voice sample
2. Login with face recognition
3. Enter teacher-provided subject code
4. Access subject cards and attendance records

## Notable code paths

These are the most important files to read when understanding the app:

- `app.py` — root app flow and page routing
- `src/screens/home_screen.py` — landing page and portal chooser
- `src/screens/teacher_screen.py` — teacher dashboard logic and attendance actions
- `src/screens/student_screen.py` — student registration/login and dashboard
- `src/database/db.py` — persistence operations and data access layer
- `src/pipelines/face_pipeline.py` — facial recognition attendance logic
- `src/pipelines/voice_pipeline.py` — voice recognition attendance logic
- `src/components/dialog_share_subject.py` — QR code and share-link generator

## Current limitations and caveats

This is a prototype and has several practical limitations that are visible from the code:

- It depends heavily on large ML libraries and may be difficult to install on some systems
- No automated test suite is included in the repository
- Use of face and voice recognition is subject to camera/audio quality, lighting, and environment noise
- Attendance matching uses fixed thresholds and may require tuning for a real classroom environment
- Database connectivity is required for any meaningful runtime usage
- There is no explicit API layer or deployment package beyond the Streamlit app

## Project status

This repository appears to be a functional prototype for an AI-powered classroom attendance app. It is well structured around a Streamlit UI and ML-based attendance recognition, and it demonstrates a realistic end-to-end workflow for teacher and student interactions.

## License

No license file was present in the repository at the time of review, so this project is currently unlicensed unless a license is added later.

## Summary

SnapClass is a compact but capable classroom attendance system that blends:
- Streamlit UI
- Supabase backend storage
- face recognition
- voice recognition
- subject and attendance management

It is best understood as a focused prototype for AI-assisted attendance tracking in education environments.

## Future improvement ideas

If this project is expanded, the following would add the most value:

- Add a proper test suite for database logic and pipelines
- Add a real schema migration system for Supabase
- Add stronger error handling and logging
- Add a teacher/student role authorization layer
- Add attendance export to CSV or PDF
- Add better classification metrics and confidence reporting
- Add model retraining and profile updates for students
- Add support for multi-class / multi-room attendance
- Add proper deployment configuration for production hosting

---

This README reflects the code structure and functional behavior present in the repository at the time of review.
