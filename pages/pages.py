
from datetime import datetime
import uuid
from fastapi import APIRouter, Form, HTTPException, Response, status, Depends
from pydantic import BaseModel, Field
from typing import Optional
import pymysql
from typing_extensions import Annotated
from bdd.cpts import tpages
from auth import User, get_current_active_user, get_password_hash, Token

pages = APIRouter(
    prefix="/pages",
    tags=["pages"]
)


class page(BaseModel):
    pagesid:Optional[int]
    name:Optional[str]
    url:Optional[str]

@pages.get("/all", tags=['pages'])
async def get_articles(current_user: Annotated[User, Depends(get_current_active_user)]):
    try:
        data:tpages = tpages().readWhere(f"1 = 1")
        response = []
        for res in data:
            r = page(
                pagesid=res.pages_id,
                name=res.name,
                url=res.url
            )
            response.append(r)
        return response
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500,detail=[])
    
@pages.post("/new", tags=['pages'])
async def create_article(current_user: Annotated[User, Depends(get_current_active_user)], name: str= Form(), url: str= Form()):
    try:
        newPage = tpages()
        newPage.name = name
        newPage.url = url
        oCnx = newPage.oCnx
        curs = oCnx.cursor()
        curs.execute(newPage.insert())
        oCnx.commit()
        curs.close()
        return {'result':'done'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=["Une erreur est survenue"])