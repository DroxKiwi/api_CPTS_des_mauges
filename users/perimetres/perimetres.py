from typing_extensions import Annotated
from fastapi import APIRouter, Form, Response, status, HTTPException
from SaleskyBdd.SALESKY import tadm_appperimetre, tadm_applist, tadm_approle, tadm_approle_societe, tadm_approle_site, tadm_approle_service, tadm_approle_poste
from pydantic import BaseModel
from typing import Optional, List

perimetres = APIRouter(
    prefix="/perimetres",
    tags=["perimetres"],
    responses={500:{"error":"error"}}
)

class application(BaseModel):
    idAppList:Optional[int]
    appName:Optional[str]
    appMode:Optional[str]

class perimetreByUser(BaseModel):
    idAppPerimetre:Optional[int]
    idAppUser:Optional[int]
    appList:Optional[List[application]]
    
class perimetreByRole(BaseModel):
    name:Optional[str]
    idAppPerimetre:Optional[int]
    idAppRole:Optional[int]
    appList:Optional[List[application]]

class appRole(BaseModel):
    idAppRole:Optional[int]
    idSociete:Optional[int]
    idSite:Optional[int]
    idService:Optional[int]
    idPoste:Optional[int]

class societe(BaseModel):
    name:Optional[str]

class site(BaseModel):
    name:Optional[str]

class service(BaseModel):
    name:Optional[str]

class poste(BaseModel):
    name:Optional[str]

def findNameFromIdAppPerimetre(idAppPerimetre):
    try :
        role = tadm_approle().readId(idAppPerimetre)
        r = appRole(
            idAppRole=role.idAppRole,
            idSociete=role.idSociete,
            idSite=role.idSite,
            idService=role.idService,
            idPoste=role.idPoste
        )
        societeDB = tadm_approle_societe().readId(str(r.idSociete))
        so = societe(
            name=societeDB.nomSociete
        )
        siteDB = tadm_approle_site().readId(str(r.idSite))
        si = site(
            name=siteDB.nomSite
        )
        serviceDB = tadm_approle_service().readId(str(r.idService))
        se = service(
            name=serviceDB.nomService
        )
        posteDB = tadm_approle_poste().readId(str(r.idPoste))
        po = poste(
            name=posteDB.nomPoste
        )
        answer = so.name + ' ' + si.name + ' ' + ' ' + se.name + ' ' + po.name
        print(answer)
        return (answer)
    except Exception as e:
        print(e)
        return None


@perimetres.get('/roles',tags=['perimetres'])
async def get_peri_roles():
    try:
        responselist = []
        periroles = tadm_appperimetre().readWhere('idAppRole is not null')
        for p in periroles:
            applist = []
            for app in p.idAppList.split(','):
                sqlApp:tadm_applist = tadm_applist().readId(app)
                newApp=application(
                    idAppList=app,
                    appName=sqlApp.appNom,
                    appMode=sqlApp.appMode
                )
                applist.append(newApp)
            pr = perimetreByRole(
                name=findNameFromIdAppPerimetre(p.idAppRole),
                idAppPerimetre=p.idAppPerimetre,
                idAppRole=p.idAppRole,
                appList=applist
            )
            responselist.append(pr)
        return responselist
    except Exception as e:
        raise HTTPException(status_code=500,detail="You're a failure, Harry.")

@perimetres.get('/users',tags=['perimetres'])
async def get_peri_users():
    responselist = []
    periusers = tadm_appperimetre().readWhere('idAppUser is not null')
    for p in periusers:
        applist = []
        for app in p.idAppList.split(','):
            sqlApp:tadm_applist = tadm_applist().readId(app)
            newApp=application(
                idAppList=app,
                appName=sqlApp.appNom,
                appMode=sqlApp.appMode
            )
            applist.append(newApp)
        pr = perimetreByUser(
            idAppPerimetre=p.idAppPerimetre,
            idAppUser=p.idAppUser,
            appList=applist
        )
        responselist.append(pr)
    return responselist

@perimetres.post('/roles/new',tags=['perimetres'])
async def post_new_perirole(idAppRole: Annotated[int, Form()], idAppList: Annotated[str, Form()], response: Response):
    try:
        rspStatus = 'fail'
        chkperirole = tadm_appperimetre().readWhere(f"idAppRole={idAppRole}")
        if len(chkperirole)>0:
            rspStatus='ce role possède déjà un périmètre'
            raise Exception
        perirole = tadm_appperimetre()
        perirole.idAppRole = idAppRole
        perirole.idAppList = idAppList
        oCnx = perirole.oCnx
        oCur = oCnx.cursor()
        oCur.execute(perirole.insert())
        oCur.close()
        oCnx.commit()
        oCnx.close()
        response.status_code=status.HTTP_200_OK
        return {'status':'done'}
    except Exception as e:
        print(e)
        response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'status':rspStatus}

@perimetres.post('/users/new',tags=['perimetres'])
async def post_new_periuser(idAppUser: Annotated[int, Form()], idAppList: Annotated[str, Form()], response: Response):
    try:
        rspStatus = 'fail'
        chkperiuser = tadm_appperimetre().readWhere(f"idAppUser={idAppUser}")
        if len(chkperiuser)>0:
            rspStatus='ce user possède déjà un périmètre'
            raise Exception
        periuser = tadm_appperimetre()
        periuser.idAppUser = idAppUser
        periuser.idAppList = idAppList
        oCnx = periuser.oCnx
        oCur = oCnx.cursor()
        oCur.execute(periuser.insert())
        oCur.close()
        oCnx.commit()
        oCnx.close()
        response.status_code=status.HTTP_200_OK
        return {'status':'done'}
    except Exception as e:
        print(e)
        response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'status':rspStatus}
    
@perimetres.post('/update',tags=['perimetres'])
async def post_upd_perirole(idAppPerimetre: Annotated[int, Form()], idAppList: Annotated[str, Form()], response: Response):
    try:
        perirole = tadm_appperimetre().readWhere(f"idAppPerimetre={idAppPerimetre}")[0]
        print(idAppList)
        perirole.idAppList = idAppList
        oCnx = perirole.oCnx
        oCur = oCnx.cursor()
        oCur.execute(perirole.update())
        oCur.close()
        oCnx.commit()
        oCnx.close()
        response.status_code=status.HTTP_200_OK
        return {'status':'done'}
    except Exception as e:
        print(e)
        response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'status':'fail'}
