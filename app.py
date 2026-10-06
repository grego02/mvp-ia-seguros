
import streamlit as st
from google import genai
from google.genai import types
import tempfile
import os
import json

# Configuración de la interfaz web corporativa
st.set_page_config(page_title="Plataforma IA Seguros", page_icon="🛡️", layout="wide")

# Barra lateral común únicamente para Navegación
with st.sidebar:
    st.header("🛡️ Panel de Control IA")
    app_mode = st.selectbox("Selecciona la herramienta:", ["Copiloto de Pólizas (RAG)", "Analista de Siniestros (JSON)"])
    st.markdown("---")
    st.info("MVP de soluciones satélites para el sector asegurador. Credenciales corporativas embebidas de forma segura.")

# ====================================================================
# EXTRACCIÓN SEGURA DE LA API KEY DESDE LOS SECRETOS DE STREAMLIT
# ====================================================================
try:
    # Captura la clave directo de la plataforma en la nube sin mostrarla en pantalla
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
    api_disponible = True
except Exception:
    st.error("⚠️ Error de configuración: La clave de la API no está configurada en los Secretos de la plataforma.")
    api_disponible = False

# Ejecutar la aplicación solo si la clave se cargó correctamente de fondo
if api_disponible:

    # ====================================================================
    # MÓDULO 1: COPILOTO DE PÓLIZAS (RAG)
    # ====================================================================
    if app_mode == "Copiloto de Pólizas (RAG)":
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
                            "di de manera muy profesional que esa información no figura en los registros de la póliza cargada. "
                            "Siempre sé estructurado y cita las secciones o cláusulas de ser posible."
                        )
                        
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=[archivo_google, f"{prompt_instrucciones}\n\nPregunta del usuario: {pregunta}"]
                        )
                        
                        st.markdown("### 📝 Respuesta del Copiloto:")
                        st.info(response.text)
                        
                    except Exception as e:
                        st.error(f"Ocurrió un error al procesar el archivo: {e}")
                    finally:
                        if os.path.exists(tmp_file_path):
                            os.remove(tmp_file_path)

    # ====================================================================
    # MÓDULO 2: ANALISTA DE SINIESTROS (JSON)
    # ====================================================================
    elif app_mode == "Analista de Siniestros (JSON)":
        st.title("🚗 Analista de Siniestros Express")
        st.subheader("Automatización de Triaje e Integración ERP (SAP Cloud)")
        st.markdown("Conversión automatizada de denuncias en texto libre a payloads estructurados compatibles con APIs corporativas.")

        texto_ejemplo_defecto = "Estimados, el pasado martes 22 de septiembre, venía manejando mi auto asegurado bajo la póliza POL-9988 por la Avenida Rivadavia al 4500. Yo soy Juan Pérez. De repente, el auto de adelante frenó de golpe y no llegué a reaccionar, lo choqué por atrás. Mi auto rompió todo el paragolpes delantero y el radiador, pierde líquido y no arranca. El otro conductor, un señor llamado Carlos Gómez, por suerte no se hizo nada, solo tiene el paragolpes trasero abollado. Yo me golpeé un poco la muñeca pero no hizo falta ambulancia. Adjunto los datos."

        relato_siniestro = st.text_area("Relato de la denuncia enviado por el asegurado (Texto libre):", value=texto_ejemplo_defecto, height=200)

        if st.button("🚀 Analizar Siniestro y Estructurar Datos"):
            with st.spinner("Procesando texto y generando payload para SAP..."):
                try:
                    prompt_sistema = "Eres un Analista Avanzado de Siniestros de Seguros. Tu tarea es recibir el relato del accidente, analizarlo y mapear los datos exactamente según el esquema JSON solicitado."

                    esquema_nativo = types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "fecha_ocurrencia": types.Schema(type=types.Type.STRING, description="Fecha del accidente en formato DD/MM/AAAA."),
                            "causa_principal": types.Schema(type=types.Type.STRING, description="Breve resumen de la causa del accidente."),
                            "vehiculos_involucrados": types.Schema(type=types.Type.INTEGER, description="Cantidad total de vehículos involucrados."),
                            "terceros_afectados": types.Schema(type=types.Type.STRING, description="¿Hubo otros autos o peatones afectados? SI/NO y detalle."),
                            "lesionados": types.Schema(type=types.Type.STRING, description="¿Se mencionan personas heridas o lesionadas? SI/NO y detalle."),
                            "estimacion_gravedad": types.Schema(type=types.Type.STRING, description="Clasificar estrictamente como: BAJA, MEDIA, o ALTA."),
                            "datos_para_sap": types.Schema(
                                type=types.Type.OBJECT,
                                properties={
                                    "id_poliza": types.Schema(type=types.Type.STRING, description="Código de póliza detectado, ej: POL-9988."),
                                    "nombre_conductor": types.Schema(type=types.Type.STRING, description="Nombre completo del conductor asegurado."),
                                    "lugar_hecho": types.Schema(type=types.Type.STRING, description="Dirección o calle donde ocurrió el evento.")
                                },
                                required=["id_poliza", "nombre_conductor", "lugar_hecho"]
                            )
                        },
                        required=["fecha_ocurrencia", "causa_principal", "vehiculos_involucrados", "terceros_afectados", "lesionados", "estimacion_gravedad", "datos_para_sap"]
                    )

                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=f"{prompt_sistema} \n\n Denuncia del cliente: \n {relato_siniestro}",
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=esquema_nativo,
                            temperature=0.1
                        ),
                    )

                    datos_extraidos = json.loads(response.text)
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("### 📋 Vista del Operador (Triaje Automatizado)")
                        st.metric(label="🚨 Nivel de Gravedad", value=datos_extraidos['estimacion_gravedad'])
                        st.write(f"**📅 Fecha detectada:** {datos_extraidos['fecha_ocurrencia']}")
                        st.write(f"**💥 Causa principal:** {datos_extraidos['causa_principal']}")
                        st.write(f"**🚗 Vehículos implicados:** {datos_extraidos['vehiculos_involucrados']}")
                        st.write(f"**👥 Terceros afectados:** {datos_extraidos['terceros_afectados']}")
                        st.write(f"**🏥 Lesionados:** {datos_extraidos['lesionados']}")
                        
                    with col2:
                        st.markdown("### 🤖 Payload JSON generado para SAP S/4HANA")
                        st.caption("Este bloque de datos es el que se inyecta directamente vía API en el ERP sin intervención humana:")
                        st.json(datos_extraidos)

                    st.success("🎉 ¡Análisis completado! Datos listos para su integración en el flujo de SAP Cloud.")

                except Exception as e:
                    st.error(f"Error en el procesamiento: {e}")


