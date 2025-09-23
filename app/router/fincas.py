from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.crud.permisos import verify_permissions
from app.router.dependencias import get_current_user
from app.schemas.users import UserOut
from core.database import get_db
from app.schemas.fincas import FincasCreate, FincasOut, FincasOut, FincasUpdate
from app.crud import fincas as crud_fincas


router = APIRouter()
modulo = 3

@router.post("/crear", status_code=status.HTTP_201_CREATED)
def create_fincas(
    finca: FincasCreate, 
    db: Session = Depends(get_db), 
    user_token: UserOut = Depends(get_current_user)
    ):
    try:
        id_rol = user_token.id_rol

            
        if not verify_permissions(db, id_rol, modulo, 'insertar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        

        crud_fincas.create_fincas(db, finca)
        return {"message": "Finca creada correctamente"}
    except HTTPException as http_exc:
        # Deja pasar errores HTTP tal como están
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-id/{id_finca}", response_model=FincasOut)
def get_finca(
    id_finca: int, 
    db: Session = Depends(get_db), 
    user_token: UserOut = Depends(get_current_user)
    ):

    try:
        id_rol = user_token.id_rol 

        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        

        finca = crud_fincas.get_finca_by_id(db, id_finca)
        if not finca:
            raise HTTPException(status_code=404, detail="Finca no encontrada")
        return finca
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    


@router.put("/by-id/{id_finca}")
def update_finca(
    id_finca: int, 
    finca: FincasUpdate, 
    db: Session = Depends(get_db), 
    user_token: UserOut = Depends(get_current_user)
    ):
    try:     
        id_rol = user_token.id_rol 

        if not verify_permissions(db, id_rol, modulo, 'actualizar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        

        success = crud_fincas.update_finca_by_id(db, id_finca, finca)

        if not success:
            raise HTTPException(status_code=404, detail="Finca no encontrada o no se realizaron cambios")
        return {"message": "Finca actualizada correctamente"}
    except HTTPException as http_exc:
        # Deja pasar errores HTTP tal como están
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))