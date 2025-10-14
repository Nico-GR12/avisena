from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError 
from sqlalchemy import text
from typing import Optional
import logging

from app.schemas.users import UserCreate, UserUpdate
from core.security import get_hashed_password

logger = logging.getLogger(__name__)

def create_user(db: Session, user: UserCreate) -> Optional[bool]:
    try:
        pass_encrypt = get_hashed_password(user.pass_hash)  #se implementa para encriptar la contraseña en la base de datos.
        user.pass_hash = pass_encrypt

        query = text("""
            INSERT INTO usuarios (
                nombre, documento, id_rol,
                email, pass_hash,
                telefono, estado
            ) VALUES (
                :nombre, :documento, :id_rol,
                :email, :pass_hash, 
                :telefono, :estado
            )
        """)
        db.execute(query, user.model_dump())
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al crear usuario: {e}")
        raise Exception("Error de base de datos al crear el usuario")

def get_user_by_email_for_login(db: Session, email: str):
    try:
        query = text("""SELECT id_usuario, nombre, documento, usuarios.id_rol,
                        email, telefono, estado, nombre_rol, pass_hash 
                        FROM usuarios 
                        INNER JOIN roles ON usuarios.id_rol = roles.id_rol
                        WHERE email = :correo""")
        result = db.execute(query, {"correo": email}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener usuario por email: {e}")
        raise Exception("Error de base de datos al obtener el usuario")


def get_all_user_except_admins(db: Session):
    try:
        query = text("""SELECT id_usuario, nombre, documento, usuarios.id_rol,
                        email, telefono, estado, nombre_rol 
                        FROM usuarios 
                        INNER JOIN roles ON usuarios.id_rol = roles.id_rol
                        WHERE usuarios.id_rol NOT IN (1,2)
                """)
        result = db.execute(query).mappings().all()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener los usuarios: {e}")
        raise Exception("Error de base de datos al obtener los usuario")



def get_user_by_email(db: Session, email: str):
    try:
        query = text("""SELECT id_usuario, nombre, documento, usuarios.id_rol,
                        email, telefono, estado, nombre_rol 
                        FROM usuarios 
                        INNER JOIN roles ON usuarios.id_rol = roles.id_rol
                        WHERE email = :correo""")
        result = db.execute(query, {"correo": email}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener usuario por email: {e}")
        raise Exception("Error de base de datos al obtener el usuario")

def update_user_by_id(db: Session, user_id: int, user: UserUpdate) -> Optional[bool]:
    try:
        # Solo los campos enviados por el cliente
        user_data = user.model_dump(exclude_unset=True, exclude_none=True)

        user_data = {key: value for key, value in user_data.items() if value != 0 and value != "" and value != "string"}

        if not user_data:
            return False  # nada que actualizar

        logger.info(f"Actualizando usuario {user_id} con datos: {user_data}")

        # Construir dinámicamente la sentencia UPDATE
        set_clauses = ", ".join([f"{key} = :{key}" for key in user_data.keys()])
        sentencia = text(f"""
            UPDATE usuarios 
            SET {set_clauses}
            WHERE id_usuario = :id_usuario
        """)

        # Agregar el id_usuario
        user_data["id_usuario"] = user_id

        result = db.execute(sentencia, user_data)
        db.commit()

        return result.rowcount > 0
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al actualizar usuario {user_id}: {e}")
        raise Exception("Error de base de datos al actualizar el usuario")
    
def get_user_by_id(db:Session, id:int):
    try:
        query = text(""" SELECT id_usuario, nombre, documento, usuarios.id_rol,
                        email, telefono, estado, nombre_rol
                        FROM usuarios
                        JOIN roles ON usuarios.id_rol = roles.id_rol
                        WHERE id_usuario = :id_usuario

                """)
        result = db.execute(query, {"id_usuario": id}).mappings().first()
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error al obtener usuario por id: {e}")
        raise Exception("Error de base de datos al obtener el usuario")
    

def change_user_status(db: Session, id_usuario: int, nuevo_estado: bool) -> bool:
    try:
        sentencia = text("""
            UPDATE usuarios
            SET estado = :estado
            WHERE id_usuario = :id_usuario
        """)
        result = db.execute(sentencia, {"estado": nuevo_estado, "id_usuario": id_usuario})
        db.commit()

        return result.rowcount > 0

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error al cambiar el estado del usuario {id_usuario}: {e}")
        raise Exception("Error de base de datos al cambiar el estado del usuario")


