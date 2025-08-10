from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
import auth
import os
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/url_shortener_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

#url -------------------------------------------------------------------------------------
class URL(Base):
    __tablename__= "urls"
    id = Column(Integer, primary_key=True)
    target_url = Column(String)
    short_key = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("USER", back_populates="urls")

class URLBase(BaseModel):
    target_url: str

class URLInfo(URLBase):
    id: int
    short_key: str
    owner_id: int
    
    class Config:
        from_attributes = True

#user-------------------------------------------------------------------------------------
class USER(Base):
    __tablename__= "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique = True, index = True)
    hashed_password = Column(String)
    urls = relationship("URL", back_populates="owner")
    
class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str
    
    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#token -------------------------------------------------------------------------------
class TOKEN(BaseModel):
    access_token: str
    token_type: str

def create_db_url(
    db : Session,
    url: str, 
    key: str,
    ownerid: int,
):
    entry = URL(target_url=url, short_key=key, owner_id = ownerid)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def get_url_by_key(
    db : Session,
    key: str
):
    url = db.query(URL).filter(URL.short_key==key).first()
    return url

def create_user(
    db: Session, 
    user:UserCreate
):
    hashed_pass = auth.get_password_hash(password=user.password)
    db_user = USER(username=user.username, hashed_password=hashed_pass)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, name: str):
    user = db.query(USER).filter(USER.username == name).first()
    return user
