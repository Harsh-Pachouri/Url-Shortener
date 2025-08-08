from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt

# --- Password Hashing ---

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# --- JWT Handling ---

SECRET_KEY = "harsh12345"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 240

def create_access_token(username: str):
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 2. Create the payload dictionary with the claims
    payload = {
        "sub": username,       
        "exp": expire,         
        "iat": datetime.now(timezone.utc)  
    }
    
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

'''
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
'''