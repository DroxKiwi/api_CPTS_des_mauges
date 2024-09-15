from typing_extensions import Annotated
from fastapi import APIRouter, Form, HTTPException, Response, status
from SaleskyBdd.SALESKY import tadm_applist, tadm_appperimetre
from pydantic import BaseModel
from typing import Optional, List

applis = APIRouter(
    prefix="/applis",
    tags=["applis"],
    responses={500:{"error":"error"}}
)

class application(BaseModel):
    idAppList:Optional[int]
    appName:Optional[str]
    appMode:Optional[str]
    appDetails:Optional[str]

@applis.get("/all",tags=["applis"])
async def get_apps():
    try:
        responseList=[]                
        sqlApp:tadm_applist = tadm_applist().readWhere("1=1")
        for app in sqlApp:
            a:tadm_applist = app
            newApp=application(
                idAppList=a.idAppList,
                appName=a.appNom,
                appMode=a.appMode,
                appDetails=a.appDetails
            )
            responseList.append(newApp)
        return responseList
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500,detail="You're a failure, Harry.")
    
@applis.get("/all/perimetre/{idperi}",tags=["applis"])
async def get_apps_by_peri(idperi:int):
    try:
        responseList=[]
        peri:tadm_appperimetre = tadm_appperimetre().readId(idperi)
        for app in peri.idAppList.split(','):
            sqlApp:tadm_applist = tadm_applist().readId(app)
            newApp=application(
                idAppList=app,
                appName=sqlApp.appNom,
                appMode=sqlApp.appMode,
                appDetails=sqlApp.appDetails
            )
            responseList.append(newApp)
        return responseList
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500,detail="You're a failure, Harry.")
    
@applis.get("/{idappli}",tags=["applis"])
async def get_app(idapp:int):
    try:
        responseList = []
        sqlapp:tadm_applist = tadm_applist().readId(idapp)
        app = application(
            idAppList=sqlapp.idAppList,
            appName=sqlapp.appNom,
            appMode=sqlapp.appMode,
            appDetails=sqlapp.appDetails
        )
        responseList.append(app)
        return responseList
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500,detail="You're a failure, Harry.")
    
@applis.post("/new",tags=["applis"])
async def new_app(appname: Annotated[str, Form()], appmode: Annotated[str, Form()], appdetails: Annotated[str, Form()], response: Response):
    try:
        newapp = tadm_applist()
        newapp.appNom=appname
        newapp.appMode=appmode
        newapp.appDetails=appdetails
        oCnx = newapp.oCnx
        cur = oCnx.cursor()    
        cur.execute(newapp.insert())
        oCnx.commit()
        cur.close()
        oCnx.close() 
        response.status_code = status.HTTP_200_OK
        return {'result':'done'}
    except Exception as e:
        print(e)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'result':'failed'}