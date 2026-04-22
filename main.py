#April 22, 2026
#
#Ross Jervin Lorenz B. Ruiz
#2023305556
#BS Data Science DS3A
#
#DS323 Cloud Computing
#Activity 5: Fanbase API (Marvel Cinematic Universe)

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List

# Database Configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./mcu_fanbase.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model
class CharacterDB(Base):
    __tablename__ = "characters"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    alias = Column(String)
    actor = Column(String)
    first_appearance = Column(String)

# Creating the database tables
Base.metadata.create_all(bind=engine)

# Pydantic Schema
class CharacterSchema(BaseModel):
    name: str
    alias: str
    actor: str
    first_appearance: str

    class Config:
        from_attributes = True

app = FastAPI(title="MCU Infinity Saga Fanbase API")

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Adding sample data
@app.on_event("startup")
def startup_populate_db():
    db = SessionLocal()
    # Check if we already have data
    if db.query(CharacterDB).count() == 0:
        sample_chars = [
            CharacterDB(name="Tony Stark", alias="Iron Man", actor="Robert Downey Jr.", first_appearance="Iron Man (2008)"),
            CharacterDB(name="Steve Rogers", alias="Captain America", actor="Chris Evans", first_appearance="Captain America: The First Avenger (2011)"),
            CharacterDB(name="Thor Odinson", alias="Thor", actor="Chris Hemsworth", first_appearance="Thor (2011)"),
            CharacterDB(name="Natasha Romanoff", alias="Black Widow", actor="Scarlett Johansson", first_appearance="Iron Man 2 (2010)"),
            CharacterDB(name="Clint Barton", alias="Hawkeye", actor="Jeremy Renner", first_appearance="Thor (2011)"),
            # Recast entries for the Hulk.
            CharacterDB(name="Bruce Banner", alias="Hulk", actor="Edward Norton", first_appearance="The Incredible Hulk (2008)"),
            CharacterDB(name="Bruce Banner", alias="Hulk", actor="Mark Ruffalo", first_appearance="The Avengers (2012)"),
            # Recast entries for War Machine.
            CharacterDB(name="James 'Rhodey' Rhodes", alias="War Machine", actor="Terrence Howard", first_appearance="Iron Man (2008)"),
            CharacterDB(name="James 'Rhodey' Rhodes", alias="War Machine", actor="Don Cheadle", first_appearance="Iron Man 2 (2010)"),
            CharacterDB(name="Virginia 'Pepper' Potts", alias="Rescue", actor="Gwyneth Paltrow", first_appearance="Iron Man (2008)"),
            CharacterDB(name="Nicholas Fury", alias="Nick", actor="Samuel L. Jackson", first_appearance="Iron Man (2008)"),
            CharacterDB(name="Jane Foster", alias="Lady Thor", actor="Natalie Portman", first_appearance="Thor (2011)"),
            CharacterDB(name="Loki Laufeyson", alias="Loki", actor="Tom Hiddleston", first_appearance="Thor (2011)"),
            CharacterDB(name="Peter Parker", alias="Spider-Man", actor="Tom Holland", first_appearance="Captain America: Civil War (2016)")
        ]
        db.add_all(sample_chars)
        db.commit()
    db.close()

# API Endpoints 

@app.get("/")
def home():
    return {"message": "Welcome to the Marvel Cinematic Universe (MCU) Infinity Saga API! Head to /docs for the interactive UI."}

# 1. Get All Characters
@app.get("/characters", response_model=List[CharacterSchema])
def get_all_characters(db: Session = Depends(get_db)):
    return db.query(CharacterDB).all()

# 2. Get a Specific Character by ID
@app.get("/characters/{char_id}", response_model=CharacterSchema)
def get_character(char_id: int, db: Session = Depends(get_db)):
    char = db.query(CharacterDB).filter(CharacterDB.id == char_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="Avenger not found in records")
    return char

# 3. Get Actors
@app.get("/actors")
def get_actors(db: Session = Depends(get_db)):
    characters = db.query(CharacterDB).all()
    # Using a set to ensure unique actor names
    unique_actors = list(set([c.actor for c in characters]))
    return {"actors": sorted(unique_actors)}

# Bonus: Add a new character via POST
@app.post("/characters", response_model=CharacterSchema)
def add_character(char: CharacterSchema, db: Session = Depends(get_db)):
    new_char = CharacterDB(**char.dict())
    db.add(new_char)
    db.commit()
    db.refresh(new_char)
    return new_char
