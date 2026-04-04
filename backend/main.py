import uuid
import secrets
import sqlite3
import os
import tempfile
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from faster_whisper import WhisperModel
import resend

load_dotenv()

CONFIG = {
    "resend_api_key": os.getenv("RESEND_API_KEY", ""),
    "api_base_url": os.getenv("API_BASE_URL", "http://localhost:8000"),
    "from_email": os.getenv("FROM_EMAIL", "dreams@gentlefuture.com"),
    "db_path": os.getenv("DB_PATH", "dreams.db"),
    "whisper_model": os.getenv("WHISPER_MODEL", "tiny"),
}

resend.api_key = CONFIG["resend_api_key"]
whisper_model = WhisperModel(CONFIG["whisper_model"], device="cpu", compute_type="int8")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    conn = sqlite3.connect(CONFIG["db_path"])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            delivery_mode TEXT DEFAULT 'immediate',
            delivery_time TEXT DEFAULT '07:00',
            timezone TEXT DEFAULT 'America/New_York',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS devices (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            token TEXT UNIQUE NOT NULL,
            name TEXT,
            last_seen DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS dreams (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            device_id TEXT NOT NULL,
            transcription TEXT NOT NULL,
            recorded_at DATETIME NOT NULL,
            duration_seconds INTEGER,
            audio_url TEXT,
            email_sent BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (device_id) REFERENCES devices(id)
        );
    """)
    conn.close()


def get_device_from_token(authorization: str | None = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    token = authorization[7:]
    conn = get_db()
    device = conn.execute("SELECT * FROM devices WHERE token = ?", (token,)).fetchone()
    conn.close()
    if not device:
        raise HTTPException(status_code=401, detail="Invalid device token")
    return dict(device)


def format_duration(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds} seconds"
    minutes = seconds // 60
    remaining = seconds % 60
    if remaining == 0:
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    return f"{minutes} minute{'s' if minutes != 1 else ''} {remaining} seconds"


def send_dream_email(user_email: str, transcription: str, recorded_at: datetime, duration_seconds: int):
    time_str = recorded_at.strftime("%-I:%M %p")
    date_str = recorded_at.strftime("%b %-d")
    subject = f"Dream — {date_str}, {time_str}"
    duration_str = format_duration(duration_seconds)
    body = f"{transcription}\n\n---\nRecorded at {time_str} · {duration_str}"
    resend.Emails.send({
        "from": CONFIG["from_email"],
        "to": user_email,
        "subject": subject,
        "text": body,
    })


@app.on_event("startup")
def startup():
    init_db()


class RegisterRequest(BaseModel):
    email: str
    device_name: str | None = None


class SettingsRequest(BaseModel):
    email: str | None = None
    delivery_mode: str | None = None
    delivery_time: str | None = None
    timezone: str | None = None


@app.post("/api/devices/register")
def register_device(body: RegisterRequest):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (body.email,)).fetchone()
    if user:
        user_id = user["id"]
    else:
        user_id = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO users (id, email) VALUES (?, ?)",
            (user_id, body.email),
        )

    device_id = str(uuid.uuid4())
    token = secrets.token_urlsafe(32)
    conn.execute(
        "INSERT INTO devices (id, user_id, token, name) VALUES (?, ?, ?, ?)",
        (device_id, user_id, token, body.device_name),
    )
    conn.commit()
    conn.close()

    resend.Emails.send({
        "from": CONFIG["from_email"],
        "to": body.email,
        "subject": "Your dream device is ready",
        "text": "Your device is set up and ready to capture dreams. Transcriptions will be delivered to this inbox.\n\nHomesick",
    })

    return {"device_token": token, "device_id": device_id}


@app.post("/api/upload")
async def upload_dream(
    file: UploadFile = File(...),
    recorded_at: str | None = Form(None),
    authorization: str | None = Header(None),
):
    device = get_device_from_token(authorization)
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (device["user_id"],)).fetchone()

    content = await file.read()
    file_size = len(content)

    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    try:
        tmp.write(content)
        tmp.close()

        segments, info = whisper_model.transcribe(tmp.name, language="en", beam_size=5)
        transcription = " ".join(segment.text.strip() for segment in segments)

        duration_seconds = int(info.duration)
        recorded_dt = datetime.fromisoformat(recorded_at) if recorded_at else datetime.utcnow()
        dream_id = str(uuid.uuid4())

        conn.execute(
            "INSERT INTO dreams (id, user_id, device_id, transcription, recorded_at, duration_seconds) VALUES (?, ?, ?, ?, ?, ?)",
            (dream_id, device["user_id"], device["id"], transcription, recorded_dt.isoformat(), duration_seconds),
        )

        if user["delivery_mode"] == "immediate":
            send_dream_email(user["email"], transcription, recorded_dt, duration_seconds)
            conn.execute("UPDATE dreams SET email_sent = TRUE WHERE id = ?", (dream_id,))

        conn.commit()
        conn.close()
    finally:
        os.unlink(tmp.name)

    return {"success": True, "transcription_id": dream_id, "transcription": transcription}


@app.get("/api/dreams")
def list_dreams(
    authorization: str | None = Header(None),
    limit: int = Query(50),
    offset: int = Query(0),
):
    device = get_device_from_token(authorization)
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM dreams WHERE user_id = ? ORDER BY recorded_at DESC LIMIT ? OFFSET ?",
        (device["user_id"], limit, offset),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.post("/api/settings")
def update_settings(body: SettingsRequest, authorization: str | None = Header(None)):
    device = get_device_from_token(authorization)
    conn = get_db()
    updates = []
    params = []
    if body.email is not None:
        updates.append("email = ?")
        params.append(body.email)
    if body.delivery_mode is not None:
        updates.append("delivery_mode = ?")
        params.append(body.delivery_mode)
    if body.delivery_time is not None:
        updates.append("delivery_time = ?")
        params.append(body.delivery_time)
    if body.timezone is not None:
        updates.append("timezone = ?")
        params.append(body.timezone)
    if updates:
        params.append(device["user_id"])
        conn.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
    conn.close()
    return {"success": True}
