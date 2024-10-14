
from datetime import datetime
import uuid
from fastapi import APIRouter, Form, HTTPException, Response, status, Depends
from pydantic import BaseModel, Field
from typing import Optional
import pymysql
from typing_extensions import Annotated
from bdd.cpts import tusers
from auth import User, get_current_active_user, get_password_hash, Token

admin = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

class userIdentity(BaseModel):
    user_id:Optional[int]
    username:Optional[str]
    accesstoken:Optional[str]
    bearertoken:Optional[Token]
    password:Optional[str]
    actif:Optional[bool]

@admin.get("/getadmin", tags=['admin'])
async def get_admin(current_user: Annotated[User, Depends(get_current_active_user)]):
    try:
        data:tusers = tusers().readWhere(f"1 = 1")
        response = []
        for res in data:
            r = userIdentity(
                user_id=res.user_id,
                username=res.username,
                accesstoken=res.accesstoken,
                bearertoken=res.bearertoken,
                password=res.password,
                actif=res.actif
            )
            response.append(r)
        return response
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500,detail=[])
    
@admin.post("/new",tags=['admin'])
async def create_user(current_user: Annotated[User, Depends(get_current_active_user)],username: Annotated[str, Form()], password: Annotated[str, Form()], idrole: Annotated[int, Form()], response: Response):
    try:
        us:tusers = tusers().readWhere(f"username='{username}'")
        if len(us)>0:
            raise IndexError
        user = tusers()
        user.username = username
        user.password = get_password_hash(password)
        user.idRole = idrole
        user.accesstoken = str(uuid.uuid4())
        user.actif = 1
        oCnx = user.oCnx
        cur = oCnx.cursor()
        cur.execute(user.insert())
        oCnx.commit()
        cur.close()
        oCnx.close()    
        response.status_code = status.HTTP_200_OK
        return {'result':'done'}
    except IndexError as ie:
        print(ie)
        response.status_code = status.HTTP_418_IM_A_TEAPOT
        return {'result':'user exists'}
    except Exception as e:
        print(e)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'result':'failed'}