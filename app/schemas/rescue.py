# from datetime import date
# from pydantic import BaseModel, Field
# from typing import Optional



# class RescueBase(BaseModel):
#     id_salvamento: int
#     id_galpon: int
#     fecha: date
#     id_tipo_gallina: int
#     cantidad_gallina: int

# class RescueCreate(RescueBase):
#     pass

# class RescueUpdate(BaseModel):
#     id_galpon: Optional[int] = None
#     fecha: Optional[date] = None
#     id_tipo_gallina: Optional[int] = None
#     cantidad_gallina: Optional[int] = None

# class RescueOut(RescueBase):
#     id_rescate: int
#     nombre_galpon: str
#     nombre_tipo_gallina: str