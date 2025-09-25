from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from typing import Optional
import logging

from app.schemas.rescue import RescueCreate, RescueUpdate

logger = logging.getLogger(__name__)

def create_rescue(db: Session, rescue: RescueCreate) -> Optional[bool]:
    try:
        query = text("""
            INSERT INTO salvamento (
                id_galpon, fecha, id_tipo_gallina, cantidad_gallinas
            ) VALUES (
                :id_galpon, :fecha, :id_tipo_gallina, :cantidad_gallinas
            )
        """)
        db.execute(query, rescue.model_dump())
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear salvamento: {e}")
        raise Exception("Error de base de datos al crear la salvamento")


def get_rescue_by_id(db: Session, id_salvamento: int):
    try:
        query = text("""SELECT id_galpon, fecha, id_tipo_gallina, cantidad_gallinas, nombre_galpon, nombre_tipo_gallina
                        FROM salvamento
                        JOIN galpones ON salvamento.id_galpon = galpones.id_galpon
                        JOIN tipo_gallinas ON salvamento.id_tipo_gallina = tipo_gallinas.id_tipo_gallina
                        WHERE id_salvamento = :salvamento_id
                    """)
        result = db.execute(query, {"salvamento_id": id_salvamento}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener salvamento por id: {e}")
        raise Exception("Error de base de datos al obtener la salvamento")


def update_rescue_by_id(db: Session, id_salvamento: int, rescue:RescueUpdate) -> Optional[bool]:
    try:
        # Solo los campos enviados por el cliente
        rescue_data = rescue.model_dump(exclude_unset=True, exclude_none=True)

        rescue_data = {key: value for key, value in rescue_data.items() if value != 0}
        
        if not rescue_data:
            return False  # nada que actualizar
        
        logger.info(f"Actualizando finca {id_salvamento} con datos: {rescue_data}")

        # Construir dinámicamente la sentencia UPDATE
        set_clauses = ", ".join([f"{key} = :{key}" for key in rescue_data.keys()])
        sentencia = text(f"""
            UPDATE salvamento 
            SET {set_clauses}
            WHERE id_salvamento = :id_salvamento
        """)

        # Agregar el id_usuario
        rescue_data["id_salvamento"] = id_salvamento

        result = db.execute(sentencia, rescue_data)
        db.commit()
        return result.rowcount > 0
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar salvamento {id_salvamento}: {e}")
        raise Exception("Error de base de datos al actualizar la salvamento")
    
