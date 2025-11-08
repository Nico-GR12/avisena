from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from typing import Optional
import logging

from app.schemas.fincas import FincasCreate, FincasUpdate

logger = logging.getLogger(__name__)


def create_fincas(db: Session, finca: FincasCreate) -> Optional[bool]:
    try:
        query = text("""
            INSERT INTO fincas (
                nombre, longitud, latitud, estado
            ) VALUES (
                :nombre, :longitud, :latitud, :estado
            )
        """)
        db.execute(query, finca.model_dump())
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear finca: {e}")
        raise Exception("Error de base de datos al crear la finca")


def get_finca_by_id(db: Session, id_finca: int):
    try:
        query = text("""SELECT id_finca, nombre, longitud, latitud,
                    estado
                    FROM fincas 
                    WHERE id_finca = :finca_id""")
        result = db.execute(query, {"finca_id": id_finca}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener finca por id: {e}")
        raise Exception("Error de base de datos al obtener la finca")

def update_finca_by_id(db: Session, finca_id: int, finca:FincasUpdate) -> Optional[bool]:
    try:
        # Solo los campos enviados por el cliente
        finca_data = finca.model_dump(exclude_unset=True, exclude_none=True)

        finca_data = {key: value for key, value in finca_data.items() if value != 0}
        
        if not finca_data:
            return False  # nada que actualizar
        
        logger.info(f"Actualizando finca {finca_id} con datos: {finca_data}")

        # Construir dinámicamente la sentencia UPDATE
        set_clauses = ", ".join([f"{key} = :{key}" for key in finca_data.keys()])
        sentencia = text(f"""
            UPDATE fincas 
            SET {set_clauses}
            WHERE id_finca = :id_finca
        """)

        # Agregar el id_usuario
        finca_data["id_finca"] = finca_id

        result = db.execute(sentencia, finca_data)
        db.commit()
        return result.rowcount > 0
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar finca {finca_id}: {e}")
        raise Exception("Error de base de datos al actualizar la finca")
    
