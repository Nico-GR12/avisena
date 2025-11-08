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
                nombre, id_rol,
                email, telefono,
                documento, pass_hash, estado
            ) VALUES (
                :nombre, :id_rol,
                :email, :telefono, 
                :documento, :pass_hash, :estado
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
        query = text("""SELECT usuarios.id_usuario, usuarios.nombre, usuarios.id_rol,
                        usuarios.email, usuarios.telefono,
                        usuarios.documento, usuarios.pass_hash, usuarios.estado, roles.nombre_rol
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
        query = text("""SELECT usuarios.id_usuario, usuarios.nombre, usuarios.id_rol,
                        usuarios.email, usuarios.telefono,
                        usuarios.documento, usuarios.pass_hash, usuarios.estado, roles.nombre_rol 
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
        query = text("""SELECT usuarios.id_usuario, usuarios.nombre, usuarios.id_rol,
                        usuarios.email, usuarios.telefono,
                        usuarios.documento, usuarios.pass_hash, usuarios.estado, roles.nombre_rol
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
        query = text(""" SELECT usuarios.id_usuario, usuarios.nombre, usuarios.id_rol,
                        usuarios.email, usuarios.telefono,
                        usuarios.documento, usuarios.pass_hash, usuarios.estado, roles.nombre_rol
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
    

# OFFSET :skip Salta un numero de filas (por ejemplo, los usuarios ya mostrados).
# FETCH NEXT :Limit ROWS ONLY obtiene solo las filas de esa pagina 
# Usamos parametros :skip y :limit para evitar inyeccion sqlñ

def get_all_user_except_admins_pag(db: Session, skip: int = 0, limit: int = 10):
    """
    Obtiene los usuarios  (excepto administradores) con paginacion.
    Tambien realiza una segunda consulta para contar total de usuarios.
    Compatible con PostgreSQL, MySQL y SQLite
    """
    try:
        # 1. Contar total de usuarios excepto admins
        count_query = text("""
            SELECT COUNT(id_usuario) AS total
            FROM usuarios
            WHERE id_rol NOT IN (1,2)
            """)
        total_result = db.execute(count_query).scalar()
    
        # 2. Consultar usuarios paginados
        data_query = text("""
            SELECT id_usuario, nombre, documento, usuarios.id_rol,
                    email, telefono, estado, nombre_rol
            FROM usuarios
            JOIN roles ON usuarios.id_rol = roles.id_rol
            WHERE usuarios.id_rol NOT IN (1,2)
            ORDER BY id_usuario
            LIMIT :limit OFFSET :skip
        """)

        result = db.execute(data_query, {"skip": skip, "limit": limit}).mappings().all()

        # 3. Retornar resultados
        return {
            "total": total_result or 0,
            "users": [dict(row) for row in result]
        }
    
    except SQLAlchemyError as e:
        logger.error(f"error al obtener los usuarios: {e}", exc_info=True)
        raise Exception("Error de base de datos al obtener los usuarios")
        


