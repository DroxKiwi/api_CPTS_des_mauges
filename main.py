from dataclasses import dataclass
from datetime import datetime
import hashlib
import os
from time import strftime, strptime
import time
from typing import Optional,List
from fastapi.security import OAuth2PasswordRequestForm
from typing_extensions import Annotated
from fastapi import Body, FastAPI, Request, UploadFile, status, HTTPException, File, Form, Response
from pydantic import BaseModel, RootModel
from admin import admin
from articles import articles
from events import events
from tags import tags
from prods import prods
from patds import patds
from globaldatas import globaldatas
from fastapi.middleware.cors import CORSMiddleware
from google.oauth2 import id_token
from bdd.cpts import tusers
import uuid
from fastapi import FastAPI, APIRouter

from auth import *

main = FastAPI(
    title="API-CPTS-full",
    version="0.0.1",
    contact={
        "name": "Corentin Fredj",
        "email": "corentinfredj.dev@gmail.com",
    },
    #docs_url=None,
    #redoc_url=None,
    #openapi_url=None
)
router = APIRouter()

main.include_router(admin.admin)
main.include_router(articles.articles)
main.include_router(events.events)
main.include_router(tags.tags)
main.include_router(prods.prods)
main.include_router(patds.patds)
main.include_router(globaldatas.globaldatas)

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://www.cptsdesmauges.fr",
    "http://www.cptsdesmauges.fr",  # Pour http, si applicable
    "https://cptsdesmauges.fr",
    "http://cptsdesmauges.fr"
]

main.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class userIdentity(BaseModel):
    user_id:Optional[int]
    username:Optional[str]
    adminofurl:Optional[str]
    accesstoken:Optional[str]
    bearertoken:Optional[Token]
    password:Optional[str]
    actif:Optional[bool]

@main.post("/user/authent",tags=['authent'])
async def authentUser(username: Annotated[str, Form()], password: Annotated[str, Form()], response: Response):      
    try:
        user:tusers = tusers().readWhere(f"username='{username}' and actif=TRUE")[0]
        if verify_password(password,user.password):
            user.accesstoken = str(uuid.uuid4())
            user.oCnx.cursor().execute(user.updateToken())
            user.oCnx.commit()
            user.oCnx.cursor().close()
            responselist = []
            responselist.append({"accesstoken":user.accesstoken})
            return responselist
        else:
            raise Exception()
    except Exception as e:
        #definitely not a user
        print(e)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return [{'authent':'failed'}]
    
@main.post("/user/token",tags=['authent'])
async def checkUserToken(accesstoken: Annotated[str,Form()], response: Response):
    try:
        user:tusers = tusers().readWhere(f"accesstoken='{accesstoken}'")[0]
        responselist = []
        print("bearer token : ")
        bearertoken=login_for_access_token(user.accesstoken)
        print(bearertoken)
        userdata=userIdentity(
            user_id=user.user_id,
            username=user.username,
            adminofurl=user.adminofurl,
            accesstoken=user.accesstoken,
            bearertoken=bearertoken,
            password=None,
            actif=None
        )
        responselist.append(userdata)
        return responselist
    except Exception as e:
        print(e)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return [{'checktoken':'failed'}]
    
@main.post("/token")
async def login_for_access(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    #can't set the Form params as unrequired, so check for default value 'bearer' instead of empty
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.accesstoken}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer", expires_in=ACCESS_TOKEN_EXPIRE_MINUTES)
    
@main.post('/refresh/token')
def login_for_access_token(user_token: Annotated[str, Form()]) -> Token:
    user = authenticate_token(user_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    #refresh the session active time in bdd
    usr:tusers = tusers().readWhere(f"accesstoken='{user_token}'")[0]
    #usr.accessLastDate = datetime.now()
    #usr.oCnx.cursor().execute(usr.update())    
    #usr.oCnx.cursor().close()
    #usr.oCnx.commit()
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.accesstoken}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer", expires_in=ACCESS_TOKEN_EXPIRE_MINUTES)

@main.get('/test')
def test():
    try:
        return "API joignable"
    except Exception as e:
        print(e)

