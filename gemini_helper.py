import time
from google.genai import errors

MODELOS = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash",
]

def generar_con_reintentos(client, prompt, intentos=2):
    ultimo_error = None

    for modelo in MODELOS:
        for intento in range(intentos):
            try:
                return client.models.generate_content(
                    model=modelo,
                    contents=prompt
                )
            except errors.APIError as e:
                ultimo_error = e

                if e.code not in (404, 429, 500, 502, 503, 504):
                    raise

                if intento < intentos - 1:
                    time.sleep(2)

    raise ultimo_error
