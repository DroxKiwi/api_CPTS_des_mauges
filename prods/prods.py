
from datetime import datetime
from fastapi import APIRouter, Form, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from typing_extensions import Annotated
from bdd.cpts import tprod
from auth import User, get_current_active_user

prods = APIRouter(
    prefix="/prods",
    tags=["prods"]
)

class prod(BaseModel):
    prod_id:Optional[int]
    prof_ids:Optional[str]
    name:Optional[str]
    img:Optional[str]
    actif:Optional[bool]

@prods.get("/all", tags=['prods'])
async def get_events(current_user: Annotated[User, Depends(get_current_active_user)]):
    try:
        data:tprod = tprod().readWhere(f"1 = 1")
        response = []
        for res in data:
            p = prod(
                prod_id=res.prod_id,
                prof_ids=res.prof_ids,
                name=res.name,
                img=res.img,
                actif=res.actif,
            )
            response.append(p)
        return response
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500,detail=[])


@prods.post("/new", tags=['prods'])
async def create_event(current_user: Annotated[User, Depends(get_current_active_user)]):
    try:
        newProd = tprod()
        newProd.prof_ids = ''
        newProd.name = f"Nouveau dossier"
        newProd.img = "null"
        newProd.actif = True
        oCnx = newProd.oCnx
        curs = oCnx.cursor()
        curs.execute(newProd.insert())
        oCnx.commit()
        curs.close()
        return {'result':'done'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=["Une erreur est survenue"])
    
@prods.post("/remove", tags=['prods'])
async def remove_event(current_user: Annotated[User, Depends(get_current_active_user)], prod_id: int = Form()):
    try:
        prodToDelete:tprod = tprod().readId(str(prod_id))
        oCnx = prodToDelete.oCnx
        curs = oCnx.cursor()
        curs.execute(prodToDelete.delete())
        oCnx.commit()
        curs.close()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=["Une erreur est survenue"])