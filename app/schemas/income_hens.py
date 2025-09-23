from datetime import date
from pydantic import BaseModel
from typing import Optional


class IncomeHensBase(BaseModel):
    id_ingreso: int
    id_galpon: int
    fecha: date
    id_tipo_gallina: int
    cantidad_gallinas: int
    
class IncomeHensCreate(IncomeHensBase):
    pass

class IncomeHensUpdate(BaseModel):
    id_galpon: Optional[int] = None
    fecha: Optional[date] = None
    id_tipo_gallina: Optional[int] = None
    cantidad_gallinas: Optional[int] = None


    
