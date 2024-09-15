from fastapi import APIRouter, Form, Response, status, Depends
from SaleskyBdd.SALESKY import tadm_approle, tadm_approle_poste, tadm_approle_service, tadm_approle_site, tadm_approle_societe
from pydantic import BaseModel
from typing import Optional
from typing_extensions import Annotated
from auth import User, get_current_active_user

roles = APIRouter(
    prefix="/roles",
    tags=["roles"],
    responses={500:{"error":"error"}}
)

class role(BaseModel):
    idAppRole:Optional[int]
    idSociete:Optional[int]
    idSite:Optional[int]
    idService:Optional[int]
    idPoste:Optional[int]

class roleDetail(BaseModel):
    idAppRole:Optional[int]
    socsitserpos:Optional[str]    

class societe(BaseModel):
    idAppRoleSociete:Optional[int]
    codeSociete:Optional[str]
    nomSociete:Optional[str]

class site(BaseModel):
    idAppRoleSite:Optional[int]
    idAppRoleSociete:Optional[int]
    nomSite:Optional[str]
    villeSite:Optional[str]

class service(BaseModel):
    idAppRoleService:Optional[int]
    nomService:Optional[str]

class poste(BaseModel):
    idAppRolePoste:Optional[int]
    idAppRoleService:Optional[int]
    nomPoste:Optional[str]

@roles.get("/all",tags=['roles'])
async def get_all_role(current_user: Annotated[User, Depends(get_current_active_user)]):
    responseList = []
    sqlData = tadm_approle().readWhere("1=1;")
    for row in sqlData:
        data:tadm_approle = row
        roledata=role(
            idAppRole=data.idAppRole,
            idSociete=data.idSociete,
            idSite=data.idSite,
            idService=data.idService,
            idPoste=data.idPoste
        )
        responseList.append(roledata)

    return responseList


@roles.get("/societes",tags=['roles'])
async def get_societes(current_user: Annotated[User, Depends(get_current_active_user)]):
    try:
        responseList = []
        soc = tadm_approle_societe().readWhere("1=1")
        for s in soc:
            oSoc = societe(
                idAppRoleSociete=s.idApproleSociete,
                codeSociete=s.codeSociete,
                nomSociete=s.nomSociete
            )
            responseList.append(oSoc)
        return responseList
    except Exception as e:
        print(e)
        return "error while fetching societes"

@roles.get("/sites/{societeid}",tags=['roles'])
async def get_sites(current_user: Annotated[User, Depends(get_current_active_user)], societeid:int):
    try:
        responseList = []
        sit = tadm_approle_site().readWhere(f"idAppRoleSociete={societeid}")
        for s in sit:
            oSit = site(
                idAppRoleSite=s.idAppRoleSite,
                idAppRoleSociete=s.idAppRoleSociete,
                nomSite=s.nomSite,
                villeSite=s.villeSite
            )
            responseList.append(oSit)
        return responseList
    except Exception as e:
        print(e)
        return "error while fetching societes"

@roles.get("/services",tags=['roles'])
async def get_services(current_user: Annotated[User, Depends(get_current_active_user)]):
    try:
        responseList = []
        ser = tadm_approle_service().readWhere("1=1")
        for s in ser:
            oSer = service(
                idAppRoleService=s.idAppRoleService,
                nomService=s.nomService                
            )
            responseList.append(oSer)
        return responseList
    except Exception as e:
        print(e)
        return "error while fetching services"

@roles.get("/postes/{serviceid}",tags=['roles'])
async def get_postes(current_user: Annotated[User, Depends(get_current_active_user)], serviceid:int):
    try:
        responseList = []
        pos = tadm_approle_poste().readWhere(f"idAppRoleService={serviceid}")
        for p in pos:
            oPos = poste(
                idAppRolePoste=p.idAppRolePoste,
                idAppRoleService=p.idAppRoleService,
                nomPoste=p.nomPoste
            )
            responseList.append(oPos)
        return responseList
    except Exception as e:
        print(e)
        return "error while fetching postes"
    
@roles.post("/societes/new",tags=['roles'])
async def post_societes(current_user: Annotated[User, Depends(get_current_active_user)], codeSociete: Annotated[str, Form()], nomSociete: Annotated[str, Form()], response: Response):
    try:
        newSoc = tadm_approle_societe()
        newSoc.codeSociete = codeSociete
        newSoc.nomSociete = nomSociete
        newSoc.actif = 1
        oCnx = newSoc.oCnx
        oCur = oCnx.cursor()
        oCur.execute(newSoc.insert())
        oCnx.commit()
        oCur.close()
        oCnx.close()
        response.status_code=status.HTTP_200_OK
        return {'status':'done'}
    except Exception as e:
        print(e)
        response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'status':'fail'}
    
@roles.post("/sites/new",tags=['roles'])
async def post_sites(current_user: Annotated[User, Depends(get_current_active_user)], idAppRoleSociete: Annotated[int, Form()], nomSite: Annotated[str, Form()], villeSite: Annotated[str, Form()], response: Response):
    try:
        newSit = tadm_approle_site()
        newSit.idAppRoleSociete = idAppRoleSociete
        newSit.nomSite = nomSite
        newSit.villeSite = villeSite
        newSit.actif = 1
        oCnx = newSit.oCnx
        oCur = oCnx.cursor()
        oCur.execute(newSit.insert())
        oCnx.commit()
        oCur.close()
        oCnx.close()
        response.status_code=status.HTTP_200_OK
        return {'status':'done'}
    except Exception as e:
        print(e)
        response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'status':'fail'}
    
@roles.post("/services/new",tags=['roles'])
async def post_services(current_user: Annotated[User, Depends(get_current_active_user)], nomService: Annotated[str, Form()], response: Response):
    try:
        newSer = tadm_approle_service()
        newSer.nomService = nomService
        newSer.actif = 1
        oCnx = newSer.oCnx
        oCur = oCnx.cursor()
        oCur.execute(newSer.insert())
        oCnx.commit()
        oCur.close()
        oCnx.close()
        response.status_code=status.HTTP_200_OK
        return {'status':'done'}
    except Exception as e:
        print(e)
        response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'status':'fail'}
    
@roles.post("/postes/new",tags=['roles'])
async def post_postes(current_user: Annotated[User, Depends(get_current_active_user)], idAppRoleService: Annotated[int, Form()], nomPoste: Annotated[str, Form()], response: Response):
    try:
        newPos = tadm_approle_poste()
        newPos.idAppRoleService = idAppRoleService
        newPos.nomPoste = nomPoste
        newPos.actif = 1
        oCnx = newPos.oCnx
        oCur = oCnx.cursor()
        oCur.execute(newPos.insert())
        oCnx.commit()
        oCur.close()
        oCnx.close()
        response.status_code=status.HTTP_200_OK
        return {'status':'done'}
    except Exception as e:
        print(e)
        response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'status':'fail'}
    
@roles.post("/new",tags=['roles'])
async def post_roles(current_user: Annotated[User, Depends(get_current_active_user)], idAppRoleSociete: Annotated[int, Form()],idAppRoleSite: Annotated[int, Form()],idAppRoleService: Annotated[int, Form()],idAppRolePoste: Annotated[int, Form()], response: Response):
    try:
        newRol = tadm_approle()
        newRol.idSociete = idAppRoleSociete
        newRol.idSite = idAppRoleSite
        newRol.idService = idAppRoleService
        newRol.idPoste = idAppRolePoste
        oCnx = newRol.oCnx
        oCur = oCnx.cursor()
        oCur.execute(newRol.insert())
        oCnx.commit()
        oCur.close()
        oCnx.close()
        response.status_code=status.HTTP_200_OK
        return {'status':'done'}
    except Exception as e:
        print(e)
        response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'status':'fail'}
    
@roles.get("/search",tags=['roles'])
async def search_roles(current_user: Annotated[User, Depends(get_current_active_user)]):
    try:
        response = []
        allroles = tadm_approle().readWhere('1=1')
        for role in allroles:
            r:tadm_approle = role
            soc = tadm_approle_societe().readId(str(r.idSociete))
            #print(soc.nomSociete)
            sit = tadm_approle_site().readId(str(r.idSite))
            #print(r.idSite)
            ser = tadm_approle_service().readId(str(r.idService))
            #print(ser.nomService)
            pos = tadm_approle_poste().readId(str(r.idPoste))
            #print(pos.nomPoste)
            cleanLib = soc.nomSociete+" "+sit.nomSite+" "+ser.nomService+" "+pos.nomPoste
            print(cleanLib)
            rd = roleDetail(
                idAppRole=r.idAppRole,
                socsitserpos=cleanLib
            )
            response.append(rd)
        return response
    except Exception as e:
        print(e)
        return []