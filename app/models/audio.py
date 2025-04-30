import hashlib
from pydantic import BaseModel

class CreateAudio(BaseModel):    
    description: str    

class Audio(BaseModel):    
    id: str
    description: str    
    file_path: str

def create_id(description: str) -> str:
    hasher = hashlib.md5()
    hasher.update(description.encode())
    return hasher.hexdigest()

def create_file_path(description: str) -> str:    
    return f"audio/{create_id(description)}.txt"