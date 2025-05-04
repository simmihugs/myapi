from typing import Optional
import os
from sqlalchemy.orm import Session
from app.database import AudioDB

def check_if_audio_exists(description: str, db: Session) -> Optional[AudioDB]:
    db_audio: AudioDB = db.query(AudioDB).filter(AudioDB.description == description).first()
    entry = db_audio if db_audio and os.path.exists(db_audio.file_path) else None
    return entry

