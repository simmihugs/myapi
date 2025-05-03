import os
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# DATABASE_URL = "sqlite:///./audio.db"

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./audio.db")

print(f"DATABASE_URL being used: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)

Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class AudioDB(Base):
    __tablename__ = "audio"

    id = Column(String, primary_key=True, index=True)
    description = Column(String, unique=True, index=True)
    file_path = Column(String, unique=True, index=True)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
