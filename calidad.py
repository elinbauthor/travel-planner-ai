import re

def comprobar_calidad(itinerario, destino, duracion):
    avisos = []

    if destino.lower() not in itinerario.lower():
        avisos.append("El destino no aparece en el itinerario.")

    dias = [
        int(n) for n in re.findall(
            r"\bDía\s+(\d+)\b", itinerario, re.IGNORECASE
        )
    ]

    faltantes = [
        n for n in range(1, duracion + 1)
        if n not in dias
    ]

    if faltantes:
        avisos.append(
            f"No se identifican los días: {faltantes}."
        )

    if not re.search(
        r"estimad|aproximad|orientativ|verific|consultar|confirmar",
        itinerario,
        re.IGNORECASE
    ):
        avisos.append(
            "Revisa los precios, horarios y disponibilidad antes de viajar."
        )

    return avisos
