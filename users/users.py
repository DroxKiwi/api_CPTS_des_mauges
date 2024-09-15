import hashlib
import uuid
from fastapi import APIRouter, Form, HTTPException, Response, status, Depends
from SaleskyBdd.SALESKY import tadm_appuser, tadm_appuser_creation, tadm_approle, tadm_appperimetre, tadm_applist, tadm_approle_poste, tadm_approle_service, tadm_approle_site, tadm_approle_societe
from pydantic import BaseModel, Field
from typing import Optional
from typing_extensions import Annotated
from datetime import datetime
from .roles import roles
from .perimetres import perimetres
from .applis import applis
from google.oauth2 import id_token
from google.auth.transport import requests
from auth import User, get_current_active_user, get_password_hash

users = APIRouter(
    prefix="/users",
    tags=["users"]
)

users.include_router(roles.roles)
users.include_router(perimetres.perimetres)
users.include_router(applis.applis)

@users.get("/",tags=['users'])
async def read_root():
    return {"Hello": "Users"}

class user(BaseModel):
    idAppUser:Optional[int]
    username:Optional[str]
    password:Optional[str]
    idRole:Optional[int]
    accessLastDate:Optional[datetime]
    actif:Optional[bool]

class perimetre(BaseModel):
    idAppPerimetre:Optional[int]
    idAppRole:Optional[int]
    idAppUser:Optional[int]
    idAppList:Optional[str]

class app(BaseModel):
    idAppList:Optional[int]
    appNom:Optional[str]
    appMode:Optional[str]
    appDetails:Optional[str]

class firsttime(BaseModel):
    idAppUserCreation:Optional[int]
    username:Optional[str]
    accessToken:Optional[str]
    accessLastDate:Optional[datetime]
    creationDate:Optional[datetime]
    decisionDate:Optional[datetime]
    decisionUserId:Optional[int]
    status:Optional[str]
    commentaire:Optional[str]

@users.get("/all",tags=['users'])
async def get_all(current_user: Annotated[User, Depends(get_current_active_user)]):
    try:
        responseList = []
        sqlData = tadm_appuser().readWhere("1=1")
        for row in sqlData:
            data:tadm_appuser = row
            userdata=user(
                idAppUser=data.idAppUser,
                username=data.username,
                password=data.password,
                idRole=data.idRole,
                accessLastDate=data.accessLastDate,
                actif=data.actif
            )
            responseList.append(userdata)

        return responseList
    except Exception as e:
        raise HTTPException(status_code=500,detail=[])

@users.get("/{userId}",tags=['users'])
async def get_all_by_id(current_user: Annotated[User, Depends(get_current_active_user)],userId:int):
    try:
        sqlData:tadm_appuser = tadm_appuser().readId(userId)
        userdata=user(
            idAppUser=sqlData.idAppUser,
            username=sqlData.username,
            password=sqlData.password,
            idRole=sqlData.idRole,
            accessLastDate=sqlData.accessLastDate,
            actif=sqlData.actif
        )
        return userdata
    except Exception as e:
        raise HTTPException(status_code=500,detail=[])

@users.get("/name/{username}",tags=['users'])
async def get_all_by_name(current_user: Annotated[User, Depends(get_current_active_user)],username:str):
    try:
        responseList = []
        sqlData:tadm_appuser = tadm_appuser().readWhere(f"username='{username}'")
        for row in sqlData:
            data:tadm_appuser = row
        userdata=user(
            idAppUser=data.idAppUser,
            username=data.username,
            password=data.password,
            idRole=data.idRole,
            accessLastDate=data.accessLastDate,
            actif=data.actif
        )
        responseList.append(userdata)

        return responseList
    except Exception as e:
        raise HTTPException(status_code=500,detail=[])

@users.get("/app/all",tags=['users'])
async def get_all_app(current_user: Annotated[User, Depends(get_current_active_user)]):
    try:
        responseList = []
        sqlData = tadm_applist().readWhere("1=1;")
        for row in sqlData:
            data:tadm_applist = row
            appdata=app(
                idAppList=data.idAppList,
                appNom=data.appNom,
                appMode=data.appMode,
                appDetails=data.appDetails
            )
            responseList.append(appdata)

        return responseList
    except Exception as e:
        raise HTTPException(status_code=500,detail="You're a failure, Harry.")

@users.post("/new",tags=['users'])
async def create_user(current_user: Annotated[User, Depends(get_current_active_user)],username: Annotated[str, Form()], password: Annotated[str, Form()], idrole: Annotated[int, Form()], response: Response):
    try:
        us:tadm_appuser = tadm_appuser().readWhere(f"username='{username}'")
        ft:tadm_appuser_creation = tadm_appuser_creation().readWhere(f"username='{username}'")
        if len(us)>0 or len(ft)>0:
            raise IndexError
        user = tadm_appuser()
        user.username = username
        user.password = get_password_hash(password)
        user.idRole = idrole
        user.accessToken = str(uuid.uuid4())
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
    
@users.post("/firsttime/new",tags=['users'])
async def create_user_first_time(googleToken: Annotated[str, Form()], password: Annotated[str, Form()], response: Response):
    try:
        CLIENT_ID='244926750321-vsqrte62jkhkmoinirvdb7147eb98rg4.apps.googleusercontent.com' #CORENTIN
   
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(googleToken, requests.Request(), CLIENT_ID) #TBD

        # If auth request is from a G Suite domain:
        if idinfo['hd'] != 'jetransporte.com':
            raise ValueError('Wrong hosted domain.')
        else:
            us:tadm_appuser = tadm_appuser().readWhere(f"username='{idinfo['email']}'")
            ft:tadm_appuser_creation = tadm_appuser_creation().readWhere(f"username='{idinfo['email']}'")
            if len(us)>0 or len(ft)>0:
                raise IndexError
            user = tadm_appuser_creation()
            user.username = idinfo['email']
            user.password = get_password_hash(password)
            user.accessToken = str(uuid.uuid4())
            user.creationDate = datetime.now()
            user.status = 'new'
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
    
@users.post("/firsttime/accept",tags=['users'])
async def accept_user_firsttime(current_user: Annotated[User, Depends(get_current_active_user)],username: Annotated[str, Form()], idRole: Annotated[int, Form()], idUserDecision: Annotated[str, Form()], response: Response):
    try:        
        usercrea:tadm_appuser_creation = tadm_appuser_creation().readWhere(f"username='{username}'")[0]
        usercrea.decisionUserId = idUserDecision
        usercrea.decisionDate = datetime.now()
        usercrea.status = 'valide'
        user = tadm_appuser()
        user.username = username
        user.password = usercrea.password
        user.idRole = idRole
        user.accessToken = usercrea.accessToken
        user.actif = 1
        oCnx = user.oCnx
        cur = oCnx.cursor()
        cur.execute(usercrea.update())
        cur.execute(user.insert())
        oCnx.commit()
        cur.close()
        oCnx.close()
        return {'result':'success'} 
    except Exception as e:
        print(e)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'result':'failed'}
    
#unicite des usernames

@users.post("/firsttime/decline",tags=['users'])
async def decline_user_firsttime(current_user: Annotated[User, Depends(get_current_active_user)],username: Annotated[str, Form()], idUserDecision: Annotated[int, Form()], commentaire: Annotated[str, Form()], response: Response):
    try:
        user:tadm_appuser_creation = tadm_appuser_creation().readWhere(f"username='{username}'")[0]
        user.decisionUserId=idUserDecision
        user.decisionDate=datetime.now()
        user.status='refus'
        user.commentaire=commentaire
        oCnx = user.oCnx
        cur = oCnx.cursor()
        cur.execute(user.update())
        oCnx.commit()
        cur.close()
        oCnx.close()
        return {'result':'success'} 
    except Exception as e:
        print(e)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'result':'failed'}    

#get all user in progress
@users.get("/firsttime/all",tags=['users'])
async def get_all_firsttime(current_user: Annotated[User, Depends(get_current_active_user)],response: Response):
    try:
        responselist = []
        user:tadm_appuser_creation = tadm_appuser_creation().readWhere(f"1=1")
        for us in user:
            u:tadm_appuser_creation = us
            ft = firsttime(
                idAppUserCreation=u.idAppUserCreation,
                username=u.username,
                accessToken=u.accessToken,
                accessLastDate=u.accessLastDate,
                creationDate=u.creationDate,
                decisionDate=u.decisionDate,
                decisionUserId=u.decisionUserId,
                status=u.status,
                commentaire=u.commentaire
            )
            responselist.append(ft)
        return responselist
    except Exception as e:
        print(e)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'result':'failed'}    


@users.post("/update",tags=['users'])
async def update_user(current_user: Annotated[User, Depends(get_current_active_user)],username: Annotated[str, Form()], idrole: Annotated[int, Form()], actif: Annotated[bool, Form()], response: Response):
    try:
        user:tadm_appuser = tadm_appuser().readWhere(f"username='{username}'")[0]
        user.idRole = idrole
        user.actif = actif
        print(user)
        oCnx = user.oCnx
        cur = oCnx.cursor()
        cur.execute(user.update())
        oCnx.commit()
        cur.close()
        response.status_code = status.HTTP_200_OK
        return {'result':'done'}
    except Exception as e:
        print(e)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'result':'failed'}
    
@users.post("/reinitPassword", tags=['users'])
async def reinit_password(current_user: Annotated[User, Depends(get_current_active_user)],username: Annotated[str, Form()], response: Response):
    try:
        user:tadm_appuser = tadm_appuser().readWhere(f"username='{username}'")[0]
        user.password = hashpass("toto")
        oCnx = user.oCnx
        cur = oCnx.cursor()
        cur.execute(user.update())
        oCnx.commit()
        cur.close()
        response.status_code = status.HTTP_200_OK
        return {'result':'done'}
    except:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'result':'failed'}
    
@users.post("/updatePassord", tags=['users'])
async def reinit_password(current_user: Annotated[User, Depends(get_current_active_user)],username: Annotated[str, Form()], password: Annotated[str, Form()], response: Response):
    try:
        user:tadm_appuser = tadm_appuser().readWhere(f"username='{username}'")[0]
        user.password = hashpass(password)
        oCnx = user.oCnx
        cur = oCnx.cursor()
        cur.execute(user.update())
        oCnx.commit()
        cur.close()
        response.status_code = status.HTTP_200_OK
        return {'result':'done'}
    except:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'result':'failed'}

@users.post("/delete",tags=['users'])
async def delete_user(current_user: Annotated[User, Depends(get_current_active_user)],username: Annotated[str, Form()], response: Response):
    try:
        user:tadm_appuser = tadm_appuser().readWhere(f"username='{username}'")[0]
        user.actif = 0
        oCnx = user.oCnx
        cur = oCnx.cursor()
        cur.execute(user.update())
        cur.close()
        response.status_code = status.HTTP_200_OK
        return {'result':'done'}
    except:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'result':'failed'}

def hashpass(password:str):
    hash_object = hashlib.sha256()
    hash_object.update(password.encode())
    hash_password = hash_object.hexdigest()
    return hash_password
