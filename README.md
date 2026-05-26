# Anti-Proxy Attendance System (APCAS)

> An AI-powered, camera-based attendance system that uses real-time face detection and recognition to automatically mark student attendance — eliminating proxy attendance entirely.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Running the Application](#running-the-application)
- [Roles & Portals](#roles--portals)
- [AI Pipeline](#ai-pipeline)
- [Team & Contributions](#team--contributions)

---

## Overview

The **Anti-Proxy Attendance System (APCAS)** is a full-stack, AI-driven solution designed for academic institutions to automate and secure the student attendance process. Using a live classroom camera (streamed via Iriun Webcam), the system captures frames at scheduled class periods, detects student faces using a YOLOv8-based face detector, and matches them against stored FaceNet embeddings to determine presence.

Results are written directly to a MySQL database and are immediately accessible through role-based web dashboards for students, faculty, and administrators.

---

## Features

1. **AI Face Recognition:** Uses YOLOv8 for face detection and FaceNet (via `keras-facenet`) for deep 512-D embeddings.
2. **Offline Mode:** Captures images via smartphone or USB camera, which can later be uploaded and processed by the desktop client.
3. **Desktop Interface:** A fast, responsive, and beautiful desktop GUI built with `CustomTkinter`.
4. **Three-Tier Portals:** Distinct dashboards for Students, Faculty, and Admins.
5. **Real-time Camera Checking:** Checks camera health and system status to maintain an audit trail.

---

## Getting Started

### Prerequisites

- Python 3.10+
- MySQL Server (Ensure database is created via `database/schema.sql`)
- NVIDIA GPU with CUDA recommended for fast embedding generation (but runs fine on CPU)

### Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create the `Attandance` database in MySQL and import `database/schema.sql`.
4. Create a `db_config.py` file in the project root with your MySQL credentials (see below).
5. Run the desktop application:
   ```bash
   python app.py
   ```

### Database Configuration (`db_config.py`)
Create a file named `db_config.py` in the project root with the following contents:
```python
import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_password",
    "database": "Attandance"
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)
```

---
- ✏️ **Manual Override** — Admin can edit timetables, attendance records, and manage faculty


---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py (Scheduler)                   │
│   Period schedule → Iriun Webcam stream → Attendance session │
└───────────────┬─────────────────────────────────────────────┘
                │
        ┌───────▼────────┐
        │ face_detector  │  YOLOv8n-face → bounding boxes
        └───────┬────────┘
                │ face crops
        ┌───────▼────────┐
        │ embedding_model│  FaceNet → 512-D embedding vectors
        └───────┬────────┘
                │ embeddings
        ┌───────▼────────┐
        │  similarity.py │  Cosine similarity → student match
        └───────┬────────┘
                │ matched student IDs
        ┌───────▼────────────────────┐
        │   attendance_service.py    │  Business logic → MySQL
        └───────┬────────────────────┘
                │
        ┌───────▼────────┐
        │     app.py     │  Flask web server + REST APIs
        └───────┬────────┘
                │
        ┌───────▼─────────────────────────────────────────────┐
        │               frontend/                              │
        │   login → student/faculty/admin dashboards          │
        └─────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer         | Technology                              |
|---------------|-----------------------------------------|
| Backend       | Python 3, Flask                         |
| AI / ML       | FaceNet (`keras-facenet`), YOLOv8 (`ultralytics`), MTCNN |
| Deep Learning | PyTorch, TensorFlow, torchvision        |
| Computer Vision | OpenCV (`opencv-python`), NumPy       |
| Database      | MySQL (`mysql-connector-python`)        |
| Frontend      | CustomTkinter                           |
| Camera        | Iriun Webcam                            |

---

## Project Structure

```
Anti-Proxy-Attendance-System/
│
├── db_config.py                 # Central database configuration
├── gui_app.py                   # CustomTkinter GUI & client logic
├── app.py                       # Application entry point (GUI + Local API backend)
├── main.py                      # Core scheduler & capture pipeline
├── attendance_service.py        # Attendance business logic (MySQL)
├── migrate_embeddings.py        # Migrate embeddings → MySQL
├── resolve_conflicts.py         # Data/merge conflict resolution helper
├── requirements.txt             # Python dependencies
│
├── models/
│   ├── embedding_model.py       # FaceNet 512-D embedding extraction
│   ├── similarity.py            # Cosine similarity scoring
│   └── generate_embeddings.py  # Batch embedding generation & storage
│
├── detection/
│   └── face_detector.py         # YOLOv8-based face localization
│
├── preprocessing/
│   ├── align.py                 # Face alignment (MTCNN)
│   ├── augment_data.py          # Data augmentation for enrollment images
│   ├── capture_image.py         # Raw image capture utilities
│   ├── dataset_cleaner.py       # Dataset quality control
│   └── preprocessing_images.py # Resize, normalize, batch preparation
│
├── database/
│   └── schema.sql               # Full MySQL schema + seed data
│
├── saved_models/
│   └── yolov8n-face.pt          # YOLOv8 face detection model weights
```

---

## Database Schema

The system uses a MySQL database named `Attandance` with the following core tables:

| Table              | Description                                              |
|--------------------|----------------------------------------------------------|
| `students`         | Student records: roll number, name, department, face encoding |
| `faculty`          | Faculty profiles and credentials                         |
| `admin`            | Administrator accounts                                   |
| `courses`          | Course catalog with faculty mapping and period counts    |
| `timetable`        | Per-class, per-day, per-period slot definitions          |
| `attendance`       | Per-student daily attendance: `hour1`–`hour6` columns    |
| `camera_health_log`| Camera status per period per day for audit trail         |

---

## Roles & Portals

### 🎓 Student

- View personal attendance dashboard with subject-wise breakdown
- See class timetable
- Review per-day attendance history

### 👨‍🏫 Faculty

- View assigned courses and timetable
- See class-level attendance for each period
- Upload offline class photos for manual attendance processing
- Export attendance as CSV
- Flag periods as upload days

### 🛡️ Admin

- Full system overview and status monitoring
- Add/manage faculty accounts
- Edit timetable entries
- View and edit attendance records for any class/student
- Monitor camera health log
- Access live camera feed

---

## AI Pipeline

```
Raw Video Frame
      │
      ▼
[YOLOv8n-face]  ─── face bounding boxes ──▶ face crops (ROI)
      │
      ▼
[MTCNN Align]   ─── aligned 160×160 face image
      │
      ▼
[FaceNet]       ─── 512-D embedding vector
      │
      ▼
[Cosine Similarity] ─── compared against stored student embeddings
      │
      ▼
[Attendance Service] ─── updates MySQL per student per period
```

**Key parameters:**
- Face detection confidence threshold: `0.5` (YOLOv8)
- Embedding size: `512` dimensions (FaceNet / `keras-facenet`)
- Input face size: `160 × 160` px (RGB)

---

## Team & Contributions

| # | Member | Role |
|---|--------|------|
| 1 | **Vasudev V** | System Architecture & AI Model |
| 2 | **Susan Saji** | Database Design & Management |
| 3 | **Sulfa Saji** | Frontend Development & Backend Integration |
| 4 | **Meera Krishna S** | Dataset Collection, Preprocessing & Documentation |

---

### 1. Vasudev V — System Architecture & AI Model

Designed the overall system architecture, defining how all components interact end-to-end. Developed and integrated the AI pipeline including model selection, training configuration, and runtime inference.

**Key files:**
- `run_gui.py` — The Desktop Application entry point.
- `gui_app.py` — The unified CustomTkinter desktop interface and client logic.
- `app.py` — The local API backend, serving data and processing requests from the desktop UI.
- `main.py` — End-to-end capture pipeline: period scheduling, Iriun Webcam I/O, attendance sessions, face matching loop, GPU cleanup.

> **Note:** The `old/` directory contains the legacy web-based frontend and server code for reference.

### `models/`
Contains the AI logic for extracting embeddings and comparing faces.rom image data with database persistence
- `detection/face_detector.py` — YOLOv8-based face localization feeding crops into the embedding pipeline

---

### 2. Susan Saji — Database Design & Management

Designed and managed the MySQL database structure, defining the schema for all entities. Handled all attendance data storage, retrieval, and business logic on top of the database layer.

**Key files:**
- `database/schema.sql` — Full MySQL schema: students, faculty, admin, courses, timetable, attendance (hour1–hour6), camera health log, and seed data
- `attendance_service.py` — Attendance business logic: ensuring rows, period updates, class-level marking from detections, camera health logging, upload eligibility, and CREATE TABLE safeguards
- `app.py` *(database layer)* — SQL throughout Flask routes: connections, timetable resolution, attendance CRUD, faculty mapping, system status queries

---

### 3. Sulfa Saji — Frontend Development & Backend Integration

Designed the user interface for all three portals and implemented all frontend features. Also built and wired backend Flask routes, JSON APIs, and session/auth logic for smooth end-to-end communication.

**Key files:**
- `app.py` — Flask application: routes, session/auth, JSON APIs (attendance, faculty periods, admin actions, live MJPEG feed helpers), offline photo processing, live embeddings
- `frontend/style.css` — Global layout, components, and visual styling
- `frontend/login.html` — Sign-in UI with role selection
- `frontend/navigation.js` — Client-side navigation helpers
- `frontend/studentdashboard.html/.js` — Student dashboard with charts
- `frontend/student_timetable.html`, `student.html`, `studentattendance.html` — Student timetable and attendance views
- `frontend/facultydashboard.html`, `facultytimetable.html`, `faculty.html` — Faculty workspace screens
- `frontend/admindashboard.html`, `addfaculty.html`, `adminclassview.html`, `edittimetable.html`, `systemstatus.html`, `live.html` — Admin management screens
- `frontend/viewattendance.html`, `capture.html` — Attendance viewing and capture UI

---

### 4. Meera Krishna S — Dataset, Preprocessing & Documentation

Collected and prepared the face image datasets required for training and enrollment. Performed system testing and created all project documentation.

**Key files:**
- `preprocessing/align.py` — Face alignment via MTCNN for high-quality embedding crops
- `preprocessing/augment_data.py` — Data augmentation for robust enrollment images
- `preprocessing/capture_image.py` — Utilities for capturing and organizing raw face images
- `preprocessing/dataset_cleaner.py` — Dataset quality control and noise removal
- `preprocessing/preprocessing_images.py` — Resize, normalize, and batch-prepare images for the ML pipeline
- `migrate_embeddings.py` — Migrates stored embeddings (`.npz`) into MySQL for runtime use
- `resolve_conflicts.py` — Helper for resolving data/merge conflicts in project assets
- `requirements.txt` — Python dependency list for environment reproduction
- `project explanation.txt` — In-depth project documentation: architecture, flows, and configuration

---

## License

This project was developed as an academic mini-project. All rights reserved by the contributors.
