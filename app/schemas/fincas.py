from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class FincaBase(BaseModel):
    nombre_finca: str = Field(min_length=3, max_length=100)
    longitud: float
    latitud: float
    id_usuario: int
    estado_finca: bool

class FincasCreate(FincaBase):
    pass

class FincasUpdate(BaseModel):
    nombre_finca: Optional[str] = None  
    longitud: Optional[float] = None
    latitud: Optional[float] = None
    estado_finca: Optional[bool] = None

class FincasOut(FincaBase):
    id_finca: int  