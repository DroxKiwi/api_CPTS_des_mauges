from datetime import datetime
from typing_extensions import Annotated
from fastapi import status, HTTPException
from pydantic import BaseModel
from bdd.cpts import tusers
from datetime import datetime, timedelta, timezone
from typing import Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing_extensions import Annotated

SECRET_KEY = "4bcffe841ab44ddc8d90cf291c3ea98620f6d093788930a8f403c7ff7b127e72"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    token: Union[str, None] = None

"""
class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None
"""
class User(BaseModel):
    user_id:int
    username:str
    accesstoken:str
    password:str
    actif:bool

class UserInDB(User):
    password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    try:
        usr = tusers().readWhere(f"username='{username}'")[0]
        user_dict = {
            "user_id":usr[0].user_id,
            "username":usr[0].username,
            "password":usr[0].password,
            "accesstoken":usr[0].accesstoken,
        }
        return UserInDB(**user_dict)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_user_token(token: str):
    try:
        usr = tusers().readWhere(f"accesstoken='{token}'")
        user_dict = {
            "user_id":usr[0].user_id,
            "username":usr[0].username,
            "password":usr[0].password,
            "accesstoken":usr[0].accesstoken,
            "actif":True
        }
        return UserInDB(**user_dict)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def authenticate_token(token: str):
    try :
        user = get_user_token(token)
        if not user:
            return False
        return user
    except Exception as e:
        print(e)

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token: str = payload.get("sub")
        if token is None:
            raise credentials_exception
        token_data = TokenData(token=token)
    except JWTError:
        raise credentials_exception
    user = get_user_token(token=token_data.token)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if not current_user.actif:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user