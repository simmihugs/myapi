from lib.worker import processing_status
from typing import List
import os
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from ..database import get_db, AudioDB, try_to_delete_audio_file
from ..models.audio import Audio, CreateAudio, create_id, create_file_path
from lib.worker import audio_queue
from lib.tts import text_to_speech
import asyncio
from ..utils import check_if_audio_exists

router = APIRouter(
    prefix="/audio",
    tags=["audio"],
    responses={404: {"description": "Audio not found"}},
)


@router.post("/", response_model=Audio)
async def query_audio(audio: CreateAudio, db: Session = Depends(get_db)):
    if option := check_if_audio_exists(audio.description, db):
        return Response(
            content=open(option.file_path, "rb").read(), media_type="audio/wav"
        )
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


@router.post("/create", response_model=Audio)
async def create_audio(audio: CreateAudio, db: Session = Depends(get_db)):
    if db_audio := check_if_audio_exists(audio.description, db):
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

        audio_file_path = text_to_speech(text=audio.description, output_path=file_path)
        if audio_file_path is None:
            db.delete(db_audio)
            db.commit()
            raise HTTPException(status_code=500, detail="Failed to generate audio")

        return db_audio


@router.post("/add_to_queue", response_model=dict)
async def add_to_queue(audio: CreateAudio, db: Session = Depends(get_db)):
    if db_audio := check_if_audio_exists(audio.description, db):
        return db_audio
    else:
        request_id = create_id(audio.description + str(asyncio.get_running_loop().time())) 
        await audio_queue.put((audio.description, request_id))
        return {
            "message":
            f"Audio request added to queue with ID: {request_id}", "request_id": request_id
        }


@router.get("/all", response_model=List[Audio])
async def all(db: Session = Depends(get_db)):
    return db.query(AudioDB).all()


@router.get("/{id}", response_model=Audio)
async def get_audio(id: str, db: Session = Depends(get_db)):
    db_audio = db.query(AudioDB).filter(AudioDB.id == id).first()
    if db_audio:
        file_path = db_audio.file_path
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Audio file not found on disk")
        return Response(content=open(file_path, "rb").read(), media_type="audio/wav")
    else:
        raise HTTPException(status_code=404, detail="No entry found in database")



@router.delete("/{id}", response_model=Audio)
async def delete_audio(id: str, db: Session = Depends(get_db)):
    db_audio = db.query(AudioDB).filter(AudioDB.id == id).first()
    try_to_delete_audio_file(db_audio)
    if db_audio is None:
        return None
    else:
        db.delete(db_audio)
        db.commit()
        return db_audio


@router.delete("/")
async def delete_all_audio(db: Session = Depends(get_db)):
    try:
        for entry in db.query(AudioDB).all():
            try_to_delete_audio_file(entry)
        db.query(AudioDB).delete()
        db.commit()

        return {"message": "All audio entries have been deleted."}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete all audio entries: {e}",
        )

