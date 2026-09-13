"""
processing/modalidad_analyzer.py

Sección 8.4 - Análisis de Modalidades (funcionalidad opcional), y su
misma lógica reutilizada para el Análisis de Delitos.
Cuenta ocurrencias de una columna y genera el ranking ordenado de mayor
a menor frecuencia. Si se indica un separador (por ejemplo ","), primero
divide el contenido de cada celda en varias ocurrencias independientes
(caso modalidades, que pueden venir combinadas). Si no hay separador
(separador=None o vacío), cada celda se cuenta como un único valor tal
cual está (caso delitos, sin combinaciones en una misma celda).
"""
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Optional

from ..models.event import Event


@dataclass
class ItemRanking:
    posicion: int
    modalidad: str
    frecuencia: int
    porcentaje: float


@dataclass
class ModalidadAnalyzer:
    separador: Optional[str] = ","
    contador: Counter = field(default_factory=Counter)

    def procesar(self, eventos: List[Event], atributo: str = "modalidad") -> Counter:
        self.contador = Counter()
        for evento in eventos:
            valor = evento.valor_atributo(atributo)
            if not valor:
                continue
            if self.separador:
                partes = [p.strip() for p in str(valor).split(self.separador) if p.strip()]
            else:
                partes = [str(valor).strip()] if str(valor).strip() else []
            self.contador.update(partes)
        return self.contador

    def ranking(self, top: Optional[int] = None) -> List[ItemRanking]:
        total = sum(self.contador.values())
        items = self.contador.most_common(top)
        resultado = []
        for posicion, (modalidad, frecuencia) in enumerate(items, start=1):
            porcentaje = (frecuencia / total * 100.0) if total else 0.0
            resultado.append(ItemRanking(posicion, modalidad, frecuencia, porcentaje))
        return resultado
