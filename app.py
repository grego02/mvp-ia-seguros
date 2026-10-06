import streamlit as st
from google import genai
from google.genai import types
import tempfile
import os
import json
import time

# Configuración de la interfaz web corporativa
st.set_page_config(page_title="Mesa de Ayuda IA & Seguros", page_icon="🛡️", layout="wide")

# Lista de modelos híbrida para mitigar caídas globales de la cuota gratuita
MODELO_PRINCIPAL = "gemini-3.8-flash"
MODELO_RESPALDO = "gemini-2.0-flash"

# Barra lateral común únicamente para Navegación
with st.sidebar:
    st.header("🛡️ Panel de Control IA")
    app_mode = st.selectbox("Selecciona la herramienta:", ["Gestor de Tickets SAP (JSON)", "Copiloto de Pólizas (RAG)"])
    st.markdown("---")
    st.info("MVP de automatización con redundancia de servidores en la nube.")

# ====================================================================
# EXTRACCIÓN SEGURA DE LA API KEY DESDE LOS SECRETOS DE STREAMLIT
# ====================================================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
    api_disponible = True
except Exception:
    st.error("⚠️ Error de configuración: La clave de la API no está configurada en los Secretos de la plataforma.")
    api_disponible = False

if api_disponible:

    # ====================================================================
    # MÓDULO 1: GESTOR DE TICKETS SAP (JSON MULTI-MÓDULO)
    # ====================================================================
    if app_mode == "Gestor de Tickets SAP (JSON)":
        st.title("⚙️ Analista de Incidentes SAP Express")
        st.subheader("Automatización de Tickets e Integración con Service Desk")
        st.markdown("Conversión automatizada de reportes de usuarios a payloads estructurados para la creación de tickets.")

        texto_ejemplo_defecto = "Al intentar anular la factura 45001234, me sale el error 'el valor del material se hará negativo' en el ambiente de producción. Necesito ayuda urgente porque frena el despacho."
        relato_incidente = st.text_area("Describe el problema o error de SAP (Texto libre):", value=texto_ejemplo_defecto, height=200)

        if st.button("🚀 Procesar Incidente y Estructurar Ticket"):
            with st.spinner("Analizando el error SAP y mapeando variables del ticket..."):
                try:
                    prompt_sistema = (
                        "Eres un Analista Avanzado de Mesa de Ayuda SAP. Tu tarea es recibir el reporte de error del usuario, "
                        "analizar el contexto técnico del mensaje y mapear los datos exactamente según el esquema JSON solicitado.\n\n"
                        "INSTRUCCIÓN CRÍTICA DE VALIDACIÓN:\n"
                        "Debes determinar con precisión el módulo SAP afectado (MM, SD, FI, CO, PP, WM, etc.). "
                        "Si el usuario describe un síntoma (ej: 'problema al facturar') pero por el contexto técnico NO logras "
                        "deducir con certeza el módulo exacto, DEBES completar el campo 'informacion_faltante' especificando "
                        "qué aclaración se necesita. Si el módulo queda claro por el tipo de error, deja el campo vacío."
                    )

                    esquema_ticket = types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "titulo_ticket": types.Schema(type=types.Type.STRING, description="Título corto para el ticket."),
                            "fecha_reporte": types.Schema(type=types.Type.STRING, description="Fecha detectada DD/MM/AAAA o la fecha actual."),
                            "modulo_sap": types.Schema(type=types.Type.STRING, description="Módulo afectado (MM, SD, FI, etc.). Poner 'DESCONOCIDO' si falta información."),
                            "prioridad": types.Schema(type=types.Type.STRING, description="Clasificar como: MUY ALTA, ALTA, NORMAL, o BAJA."),
                            "codigo_error": types.Schema(type=types.Type.STRING, description="Mensaje de error explícito de SAP."),
                            "informacion_faltante": types.Schema(type=types.Type.STRING, description="Pregunta amable al usuario si faltan datos clave. De lo contrario, dejar vacío.")
                        },
                        required=["titulo_ticket", "fecha_reporte", "modulo_sap", "prioridad", "codigo_error", "informacion_faltante"]
                    )

                    response = None
                    # Intentar primero con el modelo principal, si falla usa el de respaldo
                    for modelo in [MODELO_PRINCIPAL, MODELO_RESPALDO]:
                        try:
                            response = client.models.generate_content(
                                model=modelo,
                                contents=f"{prompt_sistema} \n\n Reporte del usuario: \n {relato_incidente}",
                                config=types.GenerateContentConfig(
                                    response_mime_type="application/json",
                                    response_schema=esquema_ticket,
                                    temperature=0.1
                                )
                            )
                            break
                        except Exception as e:
                            if "503" in str(e) and modelo == MODELO_PRINCIPAL:
                                st.warning("⚠️ Servidor principal saturado. Activando modelo de contingencia...")
                                time.sleep(1)
                                continue
                            raise e

                    if response:
                        datos_json = json.loads(response.text)
                        if datos_json.get("informacion_faltante") and datos_json["informacion_faltante"].strip() != "":
                            st.warning(f"📋 **Información Adicional Requerida:** {datos_json['informacion_faltante']}")
                        else:
                            st.success("✅ ¡Análisis completado con éxito! Información suficiente para el envío.")
                        st.json(datos_json)

                except Exception as e:
                    st.error(f"Ocurrió un error al procesar el incidente: {e}")

    # ====================================================================
    # MÓDULO 2: COPILOTO DE PÓLIZAS (RAG)
    # ====================================================================
    elif app_mode == "Copiloto de Pólizas (RAG)":
        st.title("🛡️ Copiloto Experto en Pólizas de Seguros")
        st.subheader("Auditoría analítica de documentación no estructurada")
        st.markdown("Carga una póliza real en formato PDF para realizar consultas de cobertura complejas.")

        uploaded_file = st.file_uploader("Carga el PDF de la póliza oficial aquí:", type=["pdf"])

        if uploaded_file is not None:
            st.success("✅ Archivo cargado correctamente.")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            pregunta = st.text_input("¿Qué deseas consultar sobre esta póliza?")

            if pregunta:
                with st.spinner("Analizando el documento y generando respuesta oficial..."):
                    try:
                        archivo_google = client.files.upload(file=tmp_file_path)
                        
                        prompt_instrucciones = (
                            "Eres un Copiloto Experto en Pólizas de Seguros. Tu trabajo es responder las dudas del usuario "
                            "basándote UNICAMENTE en el archivo PDF provisto. Si la respuesta no se puede deducir del texto, "
                            "di de manera muy profesional que esa información no figura en los registros de la póliza cargada."
                        )
                        
                        response = None
                        for modelo in [MODELO_PRINCIPAL, MODELO_RESPALDO]:
                            try:
                                response = client.models.generate_content(
                                    model=modelo,
                                    contents=[archivo_google, f"{prompt_instrucciones}\n\nPregunta del usuario: {pregunta}"]
                                )
                                break
                            except Exception as e:
                                if "503" in str(e) and modelo == MODELO_PRINCIPAL:
                                    st.warning("⚠️ Servidor principal ocupado. Procesando por canal secundario...")
                                    time.sleep(1)
                                    continue
                                raise e

                        if response:
                            st.markdown("### 📝 Respuesta del Copiloto:")
                            st.info(response.text)
                        
                    except Exception as e:
                        st.error(f"Ocurrió un error al procesar el archivo: {e}")
                    finally:
                        if os.path.exists(tmp_file_path):
                            os.remove(tmp_file_path)

