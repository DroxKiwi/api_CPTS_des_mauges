
from datetime import datetime
import uuid
from fastapi import APIRouter, Form, HTTPException, Response, status, Depends
from pydantic import BaseModel, Field
from typing import Optional
import pymysql
from typing_extensions import Annotated
from bdd.cpts import tevents, ttags
from auth import User, get_current_active_user, get_password_hash, Token

events = APIRouter(
    prefix="/events",
    tags=["events"]
)

class event(BaseModel):
    event_id:Optional[int]
    name:Optional[str]
    subtitle:Optional[str]
    description:Optional[str]
    img:Optional[str]
    tagid:Optional[int]
    startdate:Optional[datetime]
    enddate:Optional[datetime]
    tectimeinsert:Optional[datetime]
    actif:Optional[bool]

@events.get("/all", tags=['events'])
async def get_events(current_user: Annotated[User, Depends(get_current_active_user)]):
    try:
        data:tevents = tevents().readWhere(f"1 = 1")
        response = []
        for res in data:
            r = event(
                event_id=res.event_id,
                name=res.name,
                subtitle=res.subtitle,
                description=res.description,
                img=res.img,
                tagid=res.tagid,
                startdate=res.startdate,
                enddate=res.enddate,
                tectimeinsert=res.tectimeinsert,
                actif=res.actif
            )
            response.append(r)
        return response
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500,detail=[])

@events.get("/byid/{event_id}", tags=['events'])
async def get_events(current_user: Annotated[User, Depends(get_current_active_user)], event_id:int):
    try:
        data:tevents = tevents().readId(str(event_id))
        r = event(
            event_id=data.event_id,
            name=data.name,
            subtitle=data.subtitle,
            description=data.description,
            img=data.img,
            tagid=data.tagid,
            startdate=data.startdate,
            enddate=data.enddate,
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

@events.post("/new", tags=['events'])
async def create_event(current_user: Annotated[User, Depends(get_current_active_user)]):
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

        allevents = tevents().readWhere("1 = 1")
        ind = 0
        for a in allevents:
            ind += 1
        ind += 1
        newEvent = tevents()
        newEvent.name = f"Nom du nouvel event {ind}"
        newEvent.subtitle = "Sous-titre du nouvel event"
        newEvent.description = "Description du nouvel event"
        newEvent.img = "null"
        newEvent.tagid = allTags[-1].tag_id
        newEvent.startdate = actualDate
        newEvent.enddate = actualDate
        newEvent.tectimeinsert = actualDate
        newEvent.actif = True
        oCnx = newEvent.oCnx
        curs = oCnx.cursor()
        curs.execute(newEvent.insert())
        oCnx.commit()
        curs.close()
        return {'result':'done'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=["Une erreur est survenue"])
    
@events.post("/remove", tags=['events'])
async def remove_event(current_user: Annotated[User, Depends(get_current_active_user)], event_id: int = Form()):
    try:
        eventToDelete:tevents = tevents().readId(str(event_id))
        oCnx = eventToDelete.oCnx
        curs = oCnx.cursor()
        curs.execute(eventToDelete.delete())
        oCnx.commit()
        curs.close()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=["Une erreur est survenue"])

@events.post("/update", tags=['events'])
async def update_event(current_user: Annotated[User, Depends(get_current_active_user)], event_id: int= Form(), name: str= Form(), subtitle: str= Form(), description: str= Form(), img: str= Form(), tagid: int= Form(), startdate: str= Form(), enddate: str= Form(), actif: bool= Form()):
    try:
        eventToUpdate:tevents = tevents().readId(str(event_id))
        eventToUpdate.name = name
        eventToUpdate.subtitle = subtitle
        eventToUpdate.description = description
        eventToUpdate.img = img
        eventToUpdate.tagid = tagid
        eventToUpdate.startdate = startdate
        eventToUpdate.enddate = enddate
        eventToUpdate.actif = actif
        oCnx = eventToUpdate.oCnx
        curs = oCnx.cursor()
        curs.execute(eventToUpdate.update())
        oCnx.commit()
        curs.close()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=["Une erreur est survenue"])