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
