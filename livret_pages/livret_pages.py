
from datetime import datetime
import uuid
from fastapi import APIRouter, Form, HTTPException, Response, status, Depends
from pydantic import BaseModel, Field
from typing import Optional
import pymysql
from typing_extensions import Annotated
from bdd.cpts import tlivret_pages
from auth import User, get_current_active_user, get_password_hash, Token

livretpages = APIRouter(
    prefix="/livretpages",
    tags=["livretpages"]
)

defaultImg = "data:image/png;base64,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"

class livretpage(BaseModel):
    livret_pages_id:Optional[int]
    numero_page:Optional[int]
    img:Optional[str]

@livretpages.get("/all", tags=['livretpages'])
async def get_livretpages():
    try:
        data:tlivret_pages = tlivret_pages().readWhere(f"1 = 1 order by numero_page asc")
        response = []
        for res in data:
            r = livretpage(
                livret_pages_id = res.livret_pages_id,
                numero_page = res.numero_page,
                img = res.img
            )
            response.append(r)
        return response
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500,detail=[])
    
@livretpages.get("/byid/{livret_pages_id}", tags=['livretpages'])
async def get_articles(livret_pages_id:int):
    try:
        data:tlivret_pages = tlivret_pages().readId(livret_pages_id)
        r = livretpage(
            livret_pages_id = data.livret_pages_id,
            numero_page = data.numero_page,
            img = data.img
        )
        return r
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500,detail=[])

@livretpages.post("/new", tags=['livretpages'])
async def create_event(current_user: Annotated[User, Depends(get_current_active_user)]):
    try:
        newLivretPage = tlivret_pages()
        alllp = tlivret_pages().readWhere("1 = 1")
        ind = 0
        for l in alllp:
            ind += 1
        ind += 1
        newLivretPage.numero_page = ind
        newLivretPage.img = defaultImg
        newLivretPage.actif = True
        oCnx = newLivretPage.oCnx
        curs = oCnx.cursor()
        curs.execute(newLivretPage.insert())
        oCnx.commit()
        curs.close()
        return {'result':'done'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=["Une erreur est survenue"])

@livretpages.post("/remove", tags=['livretpages'])
async def remove_article(current_user: Annotated[User, Depends(get_current_active_user)], livret_pages_id: int = Form()):
    try:
        livretpageToDelete:tlivret_pages = tlivret_pages().readId(str(livret_pages_id))
        oCnx = livretpageToDelete.oCnx
        curs = oCnx.cursor()
        curs.execute(livretpageToDelete.delete())
        oCnx.commit()
        curs.close()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=["Une erreur est survenue"])

@livretpages.post("/update", tags=['livretpages'])
async def update_livretpages(current_user: Annotated[User, Depends(get_current_active_user)], livret_pages_id: int= Form(), numero_page: int= Form(), img: str= Form()):
    try:
        livretpageToUpdate:tlivret_pages = tlivret_pages().readId(str(livret_pages_id))
        livretpageToUpdate.numero_page = numero_page
        livretpageToUpdate.img = img
        oCnx = livretpageToUpdate.oCnx
        curs = oCnx.cursor()
        curs.execute(livretpageToUpdate.update())
        oCnx.commit()
        curs.close()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=["Une erreur est survenue"])