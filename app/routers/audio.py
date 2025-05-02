from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db, AudioDB
from ..models.audio import Audio, CreateAudio, create_id, create_file_path
from lib.tts import text_to_speech

router = APIRouter(
    prefix="/audio",
    tags=["audio"],
    responses={404: {"description": "Audio not found"}},
)


@router.post("/", response_model=Audio)
async def create_user(audio: CreateAudio, db: Session = Depends(get_db)):
    db_audio = (
        db.query(AudioDB).filter(AudioDB.description == audio.description).first()
    )
    if db_audio:
        return db_audio
    else:
        id = create_id(audio.description)
        file_path = create_file_path(audio.description)

        db_audio = AudioDB(
            id=id,
            description=audio.description,
            file_path=file_path,
        )
        db.add(db_audio)
        db.commit()
        db.refresh(db_audio)

        response = text_to_speech(text=audio.description, output_path=file_path)
        print(response)

        return db_audio


@router.get("/{description}", response_model=Audio)
async def query_audio(audio_description: str, db: Session = Depends(get_db)):
    db_audio = (
        db.query(AudioDB).filter(AudioDB.description == audio_description).first()
    )
    if db_audio is None:
        create_user(CreateAudio(description=audio_description), db)
    else:
        return db_audio


@router.delete("/{description}", response_model=Audio)
async def delete_audio(audio_description: str, db: Session = Depends(get_db)):
    db_audio = (
        db.query(AudioDB).filter(AudioDB.description == audio_description).first()
    )
    if db_audio is None:
        return None
    else:
        db.delete(db_audio)
        db.commit()
        return db_audio
