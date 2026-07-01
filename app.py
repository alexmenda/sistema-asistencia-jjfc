import streamlit as st
import pandas as pd
import datetime
import random
import string
import qrcode
from io import BytesIO
from PIL import Image

# Intentar cargar OpenCV para decodificar la foto tomada con la cámara nativa
try:
    import cv2
    import numpy as np
    OPENCV_DISPONIBLE = True
except ImportError:
    OPENCV_DISPONIBLE = False

# Configuracion de la pagina web
st.set_page_config(page_title="Sistema de Asistencia", layout="wide")

# =========================================================================
# CONFIGURACION DEL ESTADO DE SESION (Base de datos simulada)
# =========================================================================
if "asistencias_registradas" not in st.session_state:
    st.session_state.asistencias_registradas = []
if "codigo_actual" not in st.session_state:
    st.session_state.codigo_actual = "QR-PENDIENTE"
if "justificaciones" not in st.session_state:
    st.session_state.justificaciones = [
        {"F. solicitud": "2026-06-15", "CURSO": "Base de Datos Avanzada", "F. clase": "2026-06-14", "ESTADO": "APROBADO"},
        {"F. solicitud": "2026-06-28", "CURSO": "Ingles Tecnico", "F. clase": "2026-06-26", "ESTADO": "PENDIENTE"}
    ]

# Opciones fijas para los desplegables del Perfil Alumno
lista_carreras = [
    "Administracion de Empresas",
    "Contabilidad",
    "Arquitectura de Plataformas y Servicios de T.I. ",
    "Mecatronica Automotriz"
]

lista_ciclos = ["I Ciclo", "II Ciclo", "III Ciclo", "IV Ciclo", "V Ciclo", "VI Ciclo"]
lista_turnos = ["Diurno", "Nocturno"]

if "perfil_alumno" not in st.session_state:
    st.session_state.perfil_alumno = {
        "nombre": "Dani Student",
        "carrera": "Arquitectura de Plataformas y Servicios de T.I. ",
        "ciclo": "III Ciclo",
        "cursos": "Desarrollo de Software I, Base de Datos Avanzada",
        "turno": "Diurno"
    }

if "perfil_docente" not in st.session_state:
    st.session_state.perfil_docente = {
        "nombre": "Ing. Carlos Mendoza",
        "cursos": "Base de Datos Avanzada, Desarrollo de Software I"
    }

# Titulo Principal
st.title("PERFIL DE ASISTENCIA - JJFC")
st.markdown("---")

# Barra lateral para la navegacion de Roles
st.sidebar.header("PANEL DE USUARIOS")
rol = st.sidebar.selectbox("Seleccione su Rol :", ["Alumno", "Docente", "Area de Bienestar", "Administrador"])

# ==========================================
# MODULO: ALUMNO
# ==========================================
if rol == "Alumno":
    st.header("PERFIL DE ALUMNO")
    st.subheader("DATOS PERSONALES")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.perfil_alumno["nombre"] = st.text_input("NOMBRE:", st.session_state.perfil_alumno["nombre"])
        
        try:
            idx_carrera = lista_carreras.index(st.session_state.perfil_alumno["carrera"])
        except ValueError:
            idx_carrera = 2
        st.session_state.perfil_alumno["carrera"] = st.selectbox("CARRERA:", lista_carreras, index=idx_carrera)
        
        try:
            idx_ciclo = lista_ciclos.index(st.session_state.perfil_alumno["ciclo"])
        except ValueError:
            idx_ciclo = 2
        st.session_state.perfil_alumno["ciclo"] = st.selectbox("CICLO:", lista_ciclos, index=idx_ciclo)
        
    with col2:
        st.session_state.perfil_alumno["cursos"] = st.text_input("CURSOS:", st.session_state.perfil_alumno["cursos"])
        
        try:
            idx_turno = lista_turnos.index(st.session_state.perfil_alumno["turno"])
        except ValueError:
            idx_turno = 0
        st.session_state.perfil_alumno["turno"] = st.selectbox("TURNO:", lista_turnos, index=idx_turno)
        
        if st.button("Iniciar Sesion y Generar Codigo QR"):
            letras = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            fecha_str = datetime.datetime.now().strftime("%d%M")
            st.session_state.codigo_actual = f"QR-{fecha_str}-{letras}"
            st.success("Codigo de sesion generado con exito")
            
        st.info(f"**CODIGO DE SESION ACTUAL:** `{st.session_state.codigo_actual}`")

    # Mostrar imagen QR si ya se generó
    if st.session_state.codigo_actual != "QR-PENDIENTE":
        st.markdown("### Tu Codigo QR de Asistencia")
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(st.session_state.codigo_actual)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white")
        
        buf = BytesIO()
        img_qr.save(buf)
        st.image(buf.getvalue(), width=220, caption="Muestra este codigo al docente")

    st.markdown("### ALUMNO")
    data_alumno = {
        "CURSO": ["Desarrollo de Software I", "Base de Datos Avanzada", "Analisis y Diseno de Sistemas", "Ingles Tecnico"],
        "TOTAL HORAS (EN TODO EL CICLO)": [72, 64, 48, 32],
        "DICTADAS": [24, 20, 16, 10],
        "ASISTIDAS": [22, 15, 16, 8],
        "FALTAS": [2, 5, 0, 2]
    }
    df_alumno = pd.DataFrame(data_alumno)
    df_alumno["% FALTAS"] = (df_alumno["FALTAS"] / df_alumno["DICTADAS"] * 100).round(1).astype(str) + '%'
    st.table(df_alumno)

# ==========================================
# MODULO: DOCENTE
# ==========================================
elif rol == "Docente":
    st.header("PERFIL DEL DOCENTE")
    st.subheader("DATOS PERSONALES")
    
    st.session_state.perfil_docente["cursos"] = st.text_input("CURSO:", st.session_state.perfil_docente["cursos"])
    st.session_state.perfil_docente["nombre"] = st.text_input("NOMBRE:", st.session_state.perfil_docente["nombre"])
    
    st.markdown("### Escaner QR de Asistencia por Camara")
    
    # Camara nativa integrada de Streamlit (Compatible con Brave sin bloqueos locales)
    imagen_foto = st.camera_input("Enfoque el codigo QR del alumno y capture la foto:")
    
    if imagen_foto and OPENCV_DISPONIBLE:
        bytes_data = imagen_foto.getvalue()
        img_np = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        
        detector = cv2.QRCodeDetector()
        valor_qr, _, _ = detector.detectAndDecode(img_np)
        
        if valor_qr:
            ya_registrado = any(r["Codigo Usado"] == valor_qr for r in st.session_state.asistencias_registradas)
            if not ya_registrado:
                st.session_state.asistencias_registradas.append({
                    "Fecha/Hora": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Alumno": st.session_state.perfil_alumno["nombre"],
                    "Codigo Usado": valor_qr,
                    "Estado": "Presente"
                })
                st.success(f"Codigo detectado: Asistencia registrada para {valor_qr}")
                st.rerun()
        else:
            st.warning("No se pudo detectar un codigo QR valido en la foto. Intenta centrar la imagen o mejorar la iluminacion.")
    elif imagen_foto and not OPENCV_DISPONIBLE:
        st.error("OpenCV no esta disponible para procesar la imagen.")

    codigo_escaneado = st.text_input("Entrada Manual de Respaldo (Ingresa el codigo aqui):")
    if st.button("Registrar Asistencia Manual"):
        if codigo_escaneado:
            st.session_state.asistencias_registradas.append({
                "Fecha/Hora": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Alumno": st.session_state.perfil_alumno["nombre"],
                "Codigo Usado": codigo_escaneado,
                "Estado": "Presente"
            })
            st.success(f"Asistencia procesada para el codigo {codigo_escaneado}")
            st.rerun()
            
    if st.session_state.asistencias_registradas:
        st.markdown("#### Ultimos registros procesados:")
        st.dataframe(pd.DataFrame(st.session_state.asistencias_registradas))

    st.markdown("### DOCENTE")
    data_docente = {
        "CURSOS": ["Base de Datos Avanzada", "Desarrollo de Software I"],
        "TOTAL HORAS": [64, 72],
        "DICTADAS": [20, 24],
        "% FALTAS EN TODA EL AULA": ["25.0%", "8.3%"],
        "DETALLE (POR ALUMNO) ALUMNO QUE SUPERA EL % DE FALTAS.": [f"{st.session_state.perfil_alumno['nombre']} (25.0% Faltas)", "Ninguno supera el limite"],
        "E": ["Alto % de Faltas", "Estado Normal"]
    }
    st.table(pd.DataFrame(data_docente))

# ==========================================
# MODULO: AREA DE BIENESTAR
# ==========================================
elif rol == "Area de Bienestar":
    st.header("AREA DE BIENESTAR)")
    st.subheader("LISTADO DE ALUMNOS JUSTIFICADOS")
    
    df_bienestar = pd.DataFrame(st.session_state.justificaciones)
    st.table(df_bienestar)
    
    st.markdown("---")
    st.subheader("Formulario de Evaluacion de Justificaciones")
    with st.form("evaluar_justificacion"):
        alumno_select = st.selectbox("Seleccione Alumno:", [st.session_state.perfil_alumno["nombre"]])
        curso_select = st.selectbox("Curso de la Inasistencia:", ["Base de Datos Avanzada", "Desarrollo de Software I", "Ingles Técnico"])
        fecha_clase_sel = st.date_input("Fecha de la clase a justificar:")
        nuevo_estado = st.radio("Dictamen Medico / Decision:", ["APROBADO", "RECHAZADO"])
        
        if st.form_submit_button("Guardar Estado"):
            st.session_state.justificaciones.append({
                "F. solicitud": datetime.date.today().strftime("%Y-%m-%d"),
                "CURSO": curso_select,
                "F. clase": str(fecha_clase_sel),
                "ESTADO": nuevo_estado
            })
            st.success("La base de datos ha sido actualizada.")
            st.rerun()

# ==========================================
# MODULO: ADMINISTRADOR
# ==========================================
elif rol == "Administrador":
    st.header("Panel de Control del Administrador")
    
    # Sistema de seguridad con tu contraseña personalizada
    contrasenia_correcta = "admin_123"
    
    ingreso = st.text_input("Ingrese la contraseña de Administrador:", type="password")
    
    if ingreso == contrasenia_correcta:
        st.success("Acceso concedido")
        st.subheader("Base de Datos")
        
        st.markdown("#### Perfiles Registrados")
        col_adm1, col_adm2 = st.columns(2)
        with col_adm1:
            st.info(f"""
            **Estudiante Actual:**
            - **Nombre:** {st.session_state.perfil_alumno['nombre']}
            - **Carrera:** {st.session_state.perfil_alumno['carrera']}
            - **Ciclo:** {st.session_state.perfil_alumno['ciclo']}
            - **Cursos:** {st.session_state.perfil_alumno['cursos']}
            - **Turno:** {st.session_state.perfil_alumno['turno']}
            """)
        with col_adm2:
            st.success(f"""
            **Docente Actual:**
            - **Nombre:** {st.session_state.perfil_docente['nombre']}
            - **Cursos:** {st.session_state.perfil_docente['cursos']}
            """)
            
        st.markdown("#### Historial Global de Asistencias por QR")
        if st.session_state.asistencias_registradas:
            st.dataframe(pd.DataFrame(st.session_state.asistencias_registradas), use_container_width=True)
        else:
            st.warning("No hay registros de asistencias escaneadas por el docente aun.")
            
        st.markdown("#### Registro Global de Justificaciones")
        if st.session_state.justificaciones:
            st.dataframe(pd.DataFrame(st.session_state.justificaciones), use_container_width=True)
            
        st.markdown("#### Acciones de Control Técnico")
        st.checkbox("Habilitar sincronizacion automatica con el servidor del instituto")
        st.checkbox("Permitir tolerancia de 15 minutos en el escaneo de codigos")
        if st.button("Reiniciar Base de Datos del Ciclo"):
            st.session_state.asistencias_registradas = []
            st.session_state.codigo_actual = "QR-PENDIENTE"
            st.success("Datos del ciclo restablecidos con exito")
            st.rerun()
            
    elif ingreso != "":
        st.error("Contraseña incorrecta. Acceso denegado.")
