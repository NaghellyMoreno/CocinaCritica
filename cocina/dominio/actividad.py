from enum import Enum


class Actividad(Enum):
    """Qué está haciendo un cocinero (la interfaz lo usa para animarlo)."""
    LAVANDO = "lavando"
    BARRERA = "barrera"                  # esperando a los demás en una barrera
    LIBRE = "libre"
    BUSCANDO = "buscando"                # sacando ingredientes de la despensa
    SIN_INGREDIENTES = "sin_ingredientes"
    EN_COLA = "en_cola"
    COCINANDO = "cocinando"
    ENTREGANDO = "entregando"
    FIN = "fin"
