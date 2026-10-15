
from pathlib import Path
import re

CARPETA_CONOCIMIENTO = Path(__file__).parent / "knowledge"


def recuperar_contexto(destino, intereses, max_fragmentos=4):
    """Recupera fragmentos relevantes de la base de conocimiento."""

    palabras_clave = set(
        re.findall(
            r"\w+",
            f"{destino} {' '.join(intereses)}".lower()
        )
    )

    resultados = []

    for archivo in CARPETA_CONOCIMIENTO.glob("*.txt"):
        contenido = archivo.read_text(encoding="utf-8")

        # Evita recuperar información de otros destinos.
        if destino.lower() not in contenido.lower():
            continue

        fragmentos = contenido.split("\n\n")

        for fragmento in fragmentos:
            fragmento = fragmento.strip()

            if not fragmento:
                continue

            palabras_fragmento = set(
                re.findall(r"\w+", fragmento.lower())
            )

            puntuacion = len(
                palabras_clave.intersection(palabras_fragmento)
            )

            resultados.append(
                (puntuacion, archivo.name, fragmento)
            )

    resultados.sort(key=lambda x: x[0], reverse=True)

    seleccionados = resultados[:max_fragmentos]

    contexto = "\n\n".join(
        f"Fuente: {nombre}\n{fragmento}"
        for _, nombre, fragmento in seleccionados
    )

    return contexto

