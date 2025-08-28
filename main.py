import secrets
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import crud
from crud import User, UserCreate, TOKEN, Base, engine
import auth
from auth import SECRET_KEY, ALGORITHM
import jwt



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(crud.get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    current_user = crud.get_user_by_username(db, name=username) 
    if current_user is None:
        raise credentials_exception
    return current_user

def create_random_key(length: int = 5) -> str:
    return secrets.token_urlsafe(length)


@app.get("/")
def root():
    return FileResponse("static/index.html")

@app.post("/register", response_model=User)
def register(
    user: UserCreate, 
    db: Session = Depends(crud.get_db)
):
    if crud.get_user_by_username(db, name = user.username) is not None:
        raise HTTPException(status_code = 400, detail = "Username already taken")
    registered = crud.create_user(db, user)
    return registered

@app.post("/token", response_model = TOKEN)
def login(
    newuser: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(crud.get_db)
):
    registered = crud.get_user_by_username(db, name = newuser.username)
    if registered is not None and auth.verify_password(plain_password = newuser.password, hashed_password = registered.hashed_password):
        return {"access_token": auth.create_access_token(newuser.username), "token_type": "bearer"}
        
    raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
@app.post("/shorten")
def receive_url(
    url: crud.URLBase,
    current_user: crud.User = Depends(get_current_user),
    db: Session = Depends(crud.get_db)
):
    key = create_random_key()
    while crud.get_url_by_key(db, key) is not None:
        key = create_random_key()
    entry = crud.create_db_url(db, url=url.target_url, key=key, ownerid = current_user.id)
    return entry

@app.get("/{key}")
def forward_to_target_url(
    key: str,
    db: Session = Depends(crud.get_db)
):
    url = crud.get_url_by_key(db, key)
    if url:
        # Increment click count
        crud.increment_click_count(db, key)
        return RedirectResponse(url.target_url)
    else:
        raise HTTPException(status_code = 404, detail = "URL not found")
