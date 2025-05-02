from typing import List
import os
from fastapi import APIRouter, Depends, HTTPException, Response
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
async def create_audio(audio: CreateAudio, db: Session = Depends(get_db)):
    db_audio = (
        db.query(AudioDB).filter(AudioDB.description == audio.description).first()
    )

    if db_audio:
        file_path = db_audio.file_path
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Audio file not found on disk")
        return Response(content=open(file_path, "rb").read(), media_type="audio/wav")

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

        audio_file_path = text_to_speech(text=audio.description, output_path=file_path)
        if audio_file_path is None:
            db.delete(db_audio)
            db.commit()
            raise HTTPException(status_code=500, detail="Failed to generate audio")

        return Response(
            content=open(audio_file_path, "rb").read(), media_type="audio/wav"
        )


@router.get("/{description}", response_model=Audio)
async def query_audio(audio_description: str, db: Session = Depends(get_db)):
    db_audio = (
        db.query(AudioDB).filter(AudioDB.description == audio_description).first()
    )
    if db_audio is None:
        create_audio(CreateAudio(description=audio_description), db)
    else:
        file_path = db_audio.file_path
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Audio file not found on disk")
        return Response(
            content=open(db_audio.file_path, "rb").read(), media_type="audio/wav"
        )


@router.get("/library", response_model=List[Audio])
async def get_all(db: Session = Depends(get_db)):
    #return db.query(AudioDB).all()
    return db_audio = (
           db.query(AudioDB).filter(AudioDB.description == "Okay, here's the modified code that returns the audio file via the API, handling both existing and newly generated audio. f").first()
       )


@router.delete("/{description}", response_model=Audio)
async def delete_audio(audio_description: str, db: Session = Depends(get_db)):
    id = create_id(audio_description)
    file_path = create_file_path(audio_description)
    db_audio = db.query(AudioDB).filter(AudioDB.id == id).first()
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"{e}")
    if db_audio is None:
        return None
    else:
        db.delete(db_audio)
        db.commit()
        return db_audio
