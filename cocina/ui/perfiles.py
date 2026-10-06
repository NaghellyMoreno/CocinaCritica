MAX_NOMBRE = 12


def validar_nombres(nombres):
    """Devuelve un mensaje de error, o None si los nombres sirven.

    Los nombres identifican a cada hilo y a cada cocinero en pantalla, así que
    no pueden faltar ni repetirse.
    """
    limpios = [n.strip() for n in nombres]
    if any(not n for n in limpios):
        return "Todos los cocineros necesitan un nombre."
    largo = next((n for n in limpios if len(n) > MAX_NOMBRE), None)
    if largo:
        return f"«{largo}» es muy largo (máximo {MAX_NOMBRE} letras)."
    vistos = set()
    for n in limpios:
        if n.lower() in vistos:
            return f"Hay dos cocineros llamados «{n}»."
        vistos.add(n.lower())
    return None
