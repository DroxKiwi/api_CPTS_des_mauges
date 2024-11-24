
from datetime import datetime
import uuid
from fastapi import APIRouter, Form, HTTPException, Response, status, Depends
from pydantic import BaseModel, Field
from typing import Optional
import pymysql
from typing_extensions import Annotated
from bdd.cpts import tarticles, ttags
from auth import User, get_current_active_user, get_password_hash, Token

articles = APIRouter(
    prefix="/articles",
    tags=["articles"]
)

class article(BaseModel):
    article_id:Optional[int]
    name:Optional[str]
    subtitle:Optional[str]
    description:Optional[str]
    img:Optional[str]
    tagid:Optional[int]
    tectimeinsert:Optional[datetime]
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
                subtitle=res.subtitle,
                description=res.description,
                img=res.img,
                tagid=res.tagid,
                tectimeinsert=res.tectimeinsert,
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
            subtitle=data.subtitle,
            description=data.description,
            img=data.img,
            tagid=data.tagid,
            tectimeinsert=data.tectimeinsert,
            actif=data.actif
        )
        return r
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500,detail=[])
    

class tag(BaseModel):
    tag_id:Optional[int]
    name:Optional[str]
    color:Optional[str]
    actif:Optional[bool]

@articles.post("/new", tags=['articles'])
async def create_article(current_user: Annotated[User, Depends(get_current_active_user)]):
    try:

        now = datetime.now()
        actualDate = now.strftime("%Y-%m-%d %H:%M:%S")
        data:ttags = ttags().readWhere(f"1 = 1")
        allTags = []
        for res in data:
            r = tag(
                tag_id=res.tag_id,
                name=res.name,
                color=res.color,
                actif=res.actif
            )
            allTags.append(r)

        allArticles = tarticles().readWhere("1 = 1")
        ind = 0
        for a in allArticles:
            ind += 1
        ind += 1
        newArticle = tarticles()
        newArticle.name = f"Nom du nouvel article {ind}"
        newArticle.subtitle = "Sous-titre du nouvel article"
        newArticle.description = "Description du nouvel article"
        newArticle.img = "null"
        newArticle.tagid = allTags[-1].tag_id
        newArticle.tectimeinsert = actualDate
        newArticle.actif = True
        oCnx = newArticle.oCnx
        curs = oCnx.cursor()
        curs.execute(newArticle.insert())
        oCnx.commit()
        curs.close()
        return {'result':'done'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=["Une erreur est survenue"])
    
@articles.post("/remove", tags=['articles'])
async def remove_article(current_user: Annotated[User, Depends(get_current_active_user)], article_id: int = Form()):
    try:
        articleToDelete:tarticles = tarticles().readId(str(article_id))
        oCnx = articleToDelete.oCnx
        curs = oCnx.cursor()
        curs.execute(articleToDelete.delete())
        oCnx.commit()
        curs.close()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=["Une erreur est survenue"])

@articles.post("/update", tags=['articles'])
async def update_article(current_user: Annotated[User, Depends(get_current_active_user)], article_id: int= Form(), name: str= Form(), subtitle: str= Form(), description: str= Form(), img: str= Form(), tagid: int= Form(), actif: bool= Form()):
    try:
        articleToUpdate:tarticles = tarticles().readId(str(article_id))
        articleToUpdate.name = name
        articleToUpdate.subtitle = subtitle
        articleToUpdate.description = description
        articleToUpdate.img = img
        articleToUpdate.tagid = tagid
        articleToUpdate.actif = actif
        oCnx = articleToUpdate.oCnx
        curs = oCnx.cursor()
        curs.execute(articleToUpdate.update())
        oCnx.commit()
        curs.close()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=["Une erreur est survenue"])