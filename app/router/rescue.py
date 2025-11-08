from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.crud.permisos import verify_permissions
from app.router.dependencias import get_current_user
from app.schemas.rescue import RescueCreate, RescueOut, RescueUpdate
from core.database import get_db
from app.schemas.users import UserOut
from app.crud import rescue as crud_rescue

router = APIRouter()
modulo = 5

@router.post("/crear", status_code=status.HTTP_201_CREATED)
def create_rescue(
    rescue: RescueCreate, 
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        #El rol de quien usa el endpoint
        id_rol = user_token.id_rol


        if not verify_permissions(db, id_rol, modulo, 'insertar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")

        crud_rescue.create_rescue(db, rescue)
        return {"message": "Salvamento creado correctamente"}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/by-id/{id_salvamento}", response_model=RescueOut)
def get_rescue(
    id_salvamento: int, 
    db: Session = Depends(get_db), 
    user_token: UserOut = Depends(get_current_user)
    ):

    try:
        id_rol = user_token.id_rol 

        if not verify_permissions(db, id_rol, modulo, 'seleccionar'):
            raise HTTPException(status_code=401, detail="Usuario no autorizado")
        

        rescue = crud_rescue.get_rescue_by_id(db, id_salvamento)
        if not rescue:
            raise HTTPException(status_code=404, detail="Salvamento no encontrada")
        return rescue
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    
    

@router.put("/by-id/{id_salvamento}")
def update_user(
    id_salvamento: int, 
    rescue: RescueUpdate, 
    db: Session = Depends(get_db),
    user_token: UserOut = Depends(get_current_user)
):
    try:
        success = crud_rescue.update_rescue_by_id(db, id_salvamento, rescue)
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo actualizar el salvamento")
        return {"message": "salvamento actualizado correctamente"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

