from typing import List, Optional
from pydantic import BaseModel, Field


class Punto(BaseModel):
    id: str
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    orden: Optional[int] = None
    nombre: Optional[str] = ""


class Base(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    nombre: str = "Base"


class Bloqueo(BaseModel):
    id: Optional[str] = "Bloqueo"
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    reporte: Optional[str] = "Calle bloqueada"

c
class ParamsAG(BaseModel):
    poblacion: int = Field(150, ge=2)
    generaciones: int = Field(500, ge=1)
    mutacion: float = Field(0.02, ge=0.0, le=1.0)
    cruce: float = Field(0.9, ge=0.0, le=1.0)
    elite: int = Field(20, ge=1)
    tipo_mutacion: str = Field("swap", pattern="^(swap|inversion)$")
    patience: int = Field(0, ge=0)
    mejora_minima: float = Field(1.0, ge=0.0)
    semilla: Optional[int] = None
    log_cada: int = Field(50, ge=1)


class OptimizarRequest(BaseModel):
    puntos: List[Punto] = Field(..., min_length=1)
    base_inicio: Optional[Base] = None
    base_fin: Optional[Base] = None
    bloqueos: List[Bloqueo] = []
    radio_bloqueo: float = Field(25.0, gt=0)
    params_ag: ParamsAG = ParamsAG()


class HealthResponse(BaseModel):
    status: str
    grafo_cargado: bool
    nodos: int
    aristas: int
