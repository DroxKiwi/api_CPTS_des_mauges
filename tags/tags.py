
from datetime import datetime
import uuid
from fastapi import APIRouter, Form, HTTPException, Response, status, Depends
from pydantic import BaseModel, Field
from typing import Optional
import pymysql
from typing_extensions import Annotated
from bdd.cpts import ttags
from auth import User, get_current_active_user, get_password_hash, Token

tags = APIRouter(
    prefix="/tags",
    tags=["tags"]
)

class tag(BaseModel):
    tag_id:Optional[int]
    name:Optional[str]
    color:Optional[str]
    actif:Optional[bool]

@tags.get("/all", tags=['tags'])
async def get_articles(current_user: Annotated[User, Depends(get_current_active_user)]):
    try:
        data:ttags = ttags().readWhere(f"1 = 1")
        response = []
        for res in data:
            r = tag(
                tag_id=res.tag_id,
                name=res.name,
                color=res.color,
                actif=res.actif
            )
            response.append(r)
        return response
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500,detail=[])

@tags.get("/byid/{tag_id}", tags=['tags'])
async def get_articles(current_user: Annotated[User, Depends(get_current_active_user)], tag_id:int):
    try:
        data:ttags = ttags().readId(tag_id)
        r = tag(
            tag_id=data.tag_id,
            name=data.name,
            color=data.color,
            actif=data.actif
        )
        return r
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500,detail=[])
    
@tags.post("/new", tags=['tags'])
async def create_article(current_user: Annotated[User, Depends(get_current_active_user)], name: str= Form(), color: str= Form(), actif: bool= Form()):
    try:
        newTag = ttags()
        newTag.name = name
        newTag.color = color
        newTag.actif = actif
        oCnx = newTag.oCnx
        curs = oCnx.cursor()
        curs.execute(newTag.insert())
        oCnx.commit()
        curs.close()
        return {'result':'done'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=["Une erreur est survenue"])
    
    
@tags.post("/update", tags=['tags'])
async def create_article(current_user: Annotated[User, Depends(get_current_active_user)], tag_id: int= Form(), name: str= Form(), color: str= Form(), actif: bool= Form()):
    try:
        tagToUpdate:ttags = ttags().readId(tag_id)
        tagToUpdate.name = name
        tagToUpdate.color = str(color)
        tagToUpdate.actif = actif
        oCnx = tagToUpdate.oCnx
        curs = oCnx.cursor()
        curs.execute(tagToUpdate.update())
        oCnx.commit()
        curs.close()
        return {'result':'done'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=["Une erreur est survenue"])