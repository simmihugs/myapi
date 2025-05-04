import asyncio
from collections import deque
from fastapi import FastAPI
from sqlalchemy.orm import Session
from app.models.audio import create_file_path, create_id
from app.utils import check_if_audio_exists
from app.database import AudioDB
from lib.tts import text_to_speech

audio_queue = asyncio.Queue()
processing_status = {}
WORK = True


async def audio_worker(app: FastAPI, session_factory):
    print(f"worker processing status = {processing_status}")
    while WORK:
        text, request_id = await audio_queue.get()
        print(f'request id: {request_id}')
        processing_status[request_id] = {"status": "processing"}
        db: Session = session_factory()   
        # db: Session = app.state.db_session()
        try:
            if check_if_audio_exists(text, db):
                print("audio already exists")
                processing_status[request_id] = {
                    "status": "completed",
                    "message": "Audio already exists",
                }
            else:
                file_path = create_file_path(text)
                audio_file_path = text_to_speech(text=text, output_path=file_path)
                if audio_file_path:
                    print("audio created")
                    # db: Session = app.state.db_session()
                    db_audio = AudioDB(
                        id=create_id(text), description=text, file_path=file_path
                    )
                    db.add(db_audio)
                    db.commit()
                    db.refresh(db_audio)
                    processing_status[request_id] = {
                        "status": "completed",
                        "file_path": file_path,
                    }
                else:
                    print("audio creation failed")
                    processing_status[request_id] = {
                        "status": "failed",
                        "error": "TTS could not create audio",
                    }
        except Exception as exp:
            db.rollback()
            processing_status[request_id] = {"status": "failed", "error": str(exp)}
        finally:
            db.close()
            audio_queue.task_done()
