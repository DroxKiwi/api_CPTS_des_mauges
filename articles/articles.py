
from datetime import datetime
import uuid
from fastapi import APIRouter, Form, HTTPException, Response, status, Depends
from pydantic import BaseModel, Field
from typing import Optional
import pymysql
from typing_extensions import Annotated
from bdd.cpts import tarticles
from auth import User, get_current_active_user, get_password_hash, Token

articles = APIRouter(
    prefix="/articles",
    tags=["articles"]
)

class article(BaseModel):
    article_id:Optional[int]
    name:Optional[str]
    img:Optional[str]
    tagid:Optional[int]
    actif:Optional[bool]

@articles.get("/all", tags=['articles'])
async def get_articles(current_user: Annotated[User, Depends(get_current_active_user)]):
    try:
        data:tarticles = tarticles().readWhere(f"1 = 1")
        response = []
        for res in data:
            r = article(
                article_id=res.article_id,
                name=res.name,
                img=res.img,
                tagid=res.tagid,
                actif=res.actif
            )
            response.append(r)
        return response
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500,detail=[])

@articles.get("/byid/{article_id}", tags=['articles'])
async def get_articles(current_user: Annotated[User, Depends(get_current_active_user)], article_id:int):
    try:
        data:tarticles = tarticles().readId(str(article_id))
        r = article(
            article_id=data.article_id,
            name=data.name,
            img=data.img,
            tagid=data.tagid,
            actif=data.actif
        )
        return r
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500,detail=[])
    
@articles.post("/new", tags=['articles'])
async def create_article(current_user: Annotated[User, Depends(get_current_active_user)], name: str= Form(), img: str= Form(), tagid: int= Form(), actif: bool= Form()):
    try:
        newArticle = tarticles()
        newArticle.name = name
        newArticle.img = img
        newArticle.tagid = tagid
        newArticle.actif = actif
        oCnx = newArticle.oCnx
        curs = oCnx.cursor()
        curs.execute(newArticle.insert())
        oCnx.commit()
        curs.close()
        return {'result':'done'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=["Une erreur est survenue"])
    
@articles.post("/delete", tags=['articles'])
async def delete_article(current_user: Annotated[User, Depends(get_current_active_user)], article_id: int= Form()):
    try:
        print(article_id)
        articleToDelete:tarticles = tarticles().readId(str(article_id))
        oCnx = articleToDelete.oCnx
        curs = oCnx.cursor()
        curs.execute(articleToDelete.delete())
        oCnx.commit()
        curs.close()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=["Une erreur est survenue"])