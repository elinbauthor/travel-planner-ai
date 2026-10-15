from gemini_helper import generar_con_reintentos

import streamlit as st
from google import genai
from rag import recuperar_contexto

st.set_page_config(page_title="Travel Planner AI", page_icon="✈️")

st.title("✈️ Travel Planner AI")
st.write("Planifica tu próximo viaje con inteligencia artificial.")
st.info("📚 Demostración RAG: selecciona Roma para consultar información turística recuperada de nuestra base documental.")
st.caption("Para otros destinos, Gemini genera el itinerario sin documentación RAG específica.")

destino = st.text_input("¿A dónde quieres viajar?", "Roma")
duracion = st.number_input("¿Cuántos días?", min_value=1, max_value=30, value=3)
presupuesto = st.number_input("Presupuesto total (€)", min_value=0, value=500)

intereses = st.multiselect(
    "¿Qué te interesa?",
    ["Cultura", "Gastronomía", "Naturaleza", "Aventura", "Compras", "Relax"],
    default=["Cultura", "Gastronomía"]
)

restricciones = st.text_area("Restricciones o preferencias adicionales")

if st.button("✨ Generar itinerario"):
    if not destino.strip():
        st.error("Introduce un destino.")
    else:
        contexto_rag = recuperar_contexto(destino, intereses)
    prompt = f"""
        Actúa como un planificador de viajes profesional.

        Diseña un itinerario personalizado con estos datos:
        - Destino: {destino}
        - Duración: {duracion} días
        - Presupuesto total: {presupuesto} euros
        - Intereses: {', '.join(intereses) or 'Sin preferencias'}
        - Restricciones: {restricciones or 'Ninguna'}

        INFORMACIÓN TURÍSTICA RECUPERADA (RAG):
        {contexto_rag or "No se ha encontrado información específica para este destino."}

        Utiliza la información recuperada cuando sea relevante.
        No presentes como verificados los datos que no estén respaldados
        por las fuentes. Si falta información, indícalo.
        Instrucciones:
        1. Organiza el itinerario día por día.
        2. Propón actividades de mañana, tarde y noche.
        3. Adapta las recomendaciones a los intereses.
        4. Incluye estimaciones de costes y un presupuesto total.
        5. Respeta las restricciones indicadas.
        6. No inventes horarios, precios exactos ni disponibilidad.
        7. Responde en español con formato Markdown.
        """

    with st.spinner("Preparando tu viaje..."):
        try:
            client = genai.Client(
                api_key=st.secrets["GEMINI_API_KEY"]
            )

            response = generar_con_reintentos(client, prompt
            )

            if response.text:
                st.subheader("🗺️ Tu itinerario personalizado")
                st.session_state.itinerario_actual = response.text
                st.markdown(response.text)
                with st.expander("📚 Ver información recuperada mediante RAG"):
                    if contexto_rag:
                        st.text(contexto_rag)
                    else:
                        st.info("No hay documentos específicos para este destino.")
            else:
                st.warning("Gemini no ha generado una respuesta.")

        except Exception as e:
            st.error(f"Error al generar el itinerario: {e}")


# Guardar el itinerario generado para poder editarlo.
# Este bloque se ejecuta después del código de generación.
if "itinerario_actual" not in st.session_state:
    st.session_state.itinerario_actual = ""

if "valoracion" not in st.session_state:
    st.session_state.valoracion = 3

if "comentario" not in st.session_state:
    st.session_state.comentario = ""

if st.session_state.itinerario_actual:
    st.divider()
    st.subheader("📝 Itinerario actualizado")
    st.markdown(st.session_state.itinerario_actual)
    st.divider()
    st.subheader("✏️ Personaliza tu itinerario")

    cambios = st.text_area(
        "¿Qué quieres modificar?",
        placeholder="Ejemplo: Reduce el presupuesto y añade más actividades gratuitas.",
        key="solicitud_cambios"
    )

    if st.button("🔄 Aplicar cambios"):
        if cambios.strip():
            with st.spinner("Actualizando el itinerario..."):
                try:
                    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
                    respuesta = generar_con_reintentos(client, (
                            "Modifica el siguiente itinerario respetando la petición "
                            "del usuario. Mantén el formato por días, las restricciones "
                            "y las estimaciones de presupuesto. No inventes precios "
                            "ni horarios exactos.\n\n"
                            f"ITINERARIO ACTUAL:\n{st.session_state.itinerario_actual}\n\n"
                            f"CAMBIOS SOLICITADOS:\n{cambios}"
                        )
                    )
                    if respuesta.text:
                        st.session_state.itinerario_actual = respuesta.text
                        st.rerun()
                    else:
                        st.warning("No se ha podido actualizar el itinerario.")
                except Exception as e:
                    st.error(f"Error al modificar el itinerario: {e}")
        else:
            st.warning("Escribe qué quieres modificar.")

    st.subheader("⭐ Valora tu itinerario")
    st.session_state.valoracion = st.slider(
        "Valoración (1 = muy malo, 5 = excelente)",
        min_value=1,
        max_value=5,
        value=st.session_state.valoracion
    )
    st.session_state.comentario = st.text_area(
        "Comentarios sobre el resultado",
        value=st.session_state.comentario
    )

    if st.button("💬 Enviar valoración"):
        st.success("Valoración registrada durante esta sesión.")

# Guardar el itinerario generado para poder editarlo.
# Este bloque se ejecuta después del código de generación.

# Control de calidad del itinerario
if st.session_state.get("itinerario_actual"):
    from calidad import comprobar_calidad

    st.divider()
    st.subheader("🛡️ Control de calidad")

    avisos = comprobar_calidad(
        st.session_state.itinerario_actual,
        destino,
        duracion
    )

    if avisos:
        for aviso in avisos:
            st.warning(aviso)
    else:
        st.success("Comprobaciones básicas superadas.")

    st.caption(
        "Control automático orientativo. No garantiza la ausencia "
        "de errores, sesgos ni información desactualizada."
    )
st.divider()
st.subheader("🧠 Metodología y fine-tuning")

st.markdown("""
**Modelo principal:** Gemini, utilizado para generar y modificar itinerarios personalizados.

**RAG:** recuperación de información turística desde una base documental local.
Roma se utiliza como destino de demostración.

**Fine-tuning experimental:** se realizó un ajuste de un modelo
preentrenado mediante LoRA en Google Colab, utilizando cuatro ejemplos
de itinerarios personalizados.

**Resultados del entrenamiento:**
- 6 épocas y 12 pasos de entrenamiento.
- Pérdida inicial registrada: 2,6126.
- Pérdida final registrada: 2,2810.
- Aproximadamente 540.672 parámetros entrenables.

La disminución de la pérdida indica que el modelo se adaptó a los
ejemplos de entrenamiento, aunque el conjunto de datos es demasiado
pequeño para demostrar una mejora general de calidad.

**Nota:** el fine-tuning se realizó como experimento independiente.
La aplicación pública utiliza Gemini y no ejecuta el modelo ajustado.

**Control de calidad:** comprobaciones automáticas básicas,
instrucciones para evitar información no verificada y posibilidad
de modificar y valorar los itinerarios.
""")
