import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st


# CONFIGURACION

BASE_DIR = Path(__file__).parent
EXCEL_PATH = BASE_DIR / "Avances 26-1-PH2.xlsx"
DB_PATH = BASE_DIR / "avances.db"

st.set_page_config(
    page_title="Avances 26-1-PH2",
    page_icon="📋",
    layout="wide"
)


# FUNCIONES GENERALES

def limpiar_texto(valor):
    if pd.isna(valor):
        return ""

    return str(valor).strip()


def normalizar_nombre(valor):
    texto = limpiar_texto(valor)
    texto = texto.replace("\n", " ")
    texto = " ".join(texto.split())

    return texto


def normalizar_avance(valor):
    try:
        numero = float(valor)

        if numero <= 1:
            numero = numero * 100

        numero = round(numero)

        return max(0, min(100, numero))

    except (TypeError, ValueError):
        return 0


def obtener_pines():
    try:
        return st.secrets.get("leader_pins", {})

    except Exception:
        return {}


def validar_pin(lider, pin):
    pines = obtener_pines()

    if not pines:
        return True

    pin_guardado = str(pines.get(lider, ""))

    return pin_guardado == str(pin)


# CARGAR EXCEL

@st.cache_data(show_spinner=False)
def cargar_actividades():
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(
            "No se encontro el archivo Avances 26-1-PH2.xlsx"
        )

    hojas = pd.ExcelFile(
        EXCEL_PATH,
        engine="openpyxl"
    ).sheet_names

    df = None
    hoja_encontrada = None
    fila_encabezado = None

    for nombre_hoja in hojas:
        df_previa = pd.read_excel(
            EXCEL_PATH,
            sheet_name=nombre_hoja,
            header=None,
            engine="openpyxl"
        )

        limite_filas = min(len(df_previa), 50)

        for indice in range(limite_filas):
            fila = df_previa.iloc[indice]

            valores = [
                normalizar_nombre(valor)
                for valor in fila.tolist()
                if pd.notna(valor)
            ]

            encontro_itm = any(
                valor.lower().startswith("itm")
                for valor in valores
            )

            encontro_tarea = any(
                "nombre de tarea" in valor.lower()
                for valor in valores
            )

            encontro_lider = any(
                "líder" in valor.lower()
                or "lider" in valor.lower()
                for valor in valores
            )

            if encontro_itm and encontro_tarea and encontro_lider:
                hoja_encontrada = nombre_hoja
                fila_encabezado = indice
                break

        if fila_encabezado is not None:
            break

    if fila_encabezado is None:
        raise ValueError(
            "No se encontro la fila de encabezados del Excel."
        )

    df = pd.read_excel(
        EXCEL_PATH,
        sheet_name=hoja_encontrada,
        header=fila_encabezado,
        engine="openpyxl"
    )

    df.columns = [
        normalizar_nombre(columna)
        for columna in df.columns
    ]

    renombrar_columnas = {}

    for columna in df.columns:
        columna_normalizada = columna.lower()

        if columna_normalizada.startswith("itm"):
            renombrar_columnas[columna] = "Itm"

        elif "nombre de tarea" in columna_normalizada:
            renombrar_columnas[columna] = "Nombre de tarea"

        elif (
            columna_normalizada == "líder"
            or columna_normalizada == "lider"
        ):
            renombrar_columnas[columna] = "Líder"

        elif columna_normalizada == "%":
            renombrar_columnas[columna] = "%"

        elif columna_normalizada == "activo":
            renombrar_columnas[columna] = "Activo"

        elif (
            columna_normalizada == "ubicación"
            or columna_normalizada == "ubicacion"
        ):
            renombrar_columnas[columna] = "Ubicación"

        elif columna_normalizada == "ot":
            renombrar_columnas[columna] = "OT"

        elif columna_normalizada == "responsable":
            renombrar_columnas[columna] = "Responsable"

        elif columna_normalizada.startswith("comentarios"):
            renombrar_columnas[columna] = "Comentarios"

    df = df.rename(
        columns=renombrar_columnas
    )

    columnas_necesarias = [
        "Itm",
        "Nombre de tarea",
        "Líder",
        "%"
    ]

    columnas_faltantes = [
        columna
        for columna in columnas_necesarias
        if columna not in df.columns
    ]

    if columnas_faltantes:
        raise ValueError(
            "Faltan columnas en el Excel: "
            + ", ".join(columnas_faltantes)
        )

    df["Itm"] = pd.to_numeric(
        df["Itm"],
        errors="coerce"
    )

    df = df[df["Itm"].notna()].copy()
    df["Itm"] = df["Itm"].astype(int)

    columnas_texto = [
        "Líder",
        "Nombre de tarea",
        "Ubicación",
        "Activo",
        "OT",
        "Responsable",
        "Comentarios"
    ]

    for columna in columnas_texto:
        if columna not in df.columns:
            df[columna] = ""

        df[columna] = df[columna].apply(
            limpiar_texto
        )

    df["Avance inicial"] = df["%"].apply(
        normalizar_avance
    )

    df = df[df["Líder"] != ""].copy()
    df = df[df["Nombre de tarea"] != ""].copy()

    return df


# BASE DE DATOS

def conectar_bd():
    conexion = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )

    consulta = (
        "CREATE TABLE IF NOT EXISTS avances ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "item INTEGER NOT NULL, "
        "lider TEXT NOT NULL, "
        "avance INTEGER NOT NULL, "
        "comentario TEXT, "
        "usuario TEXT NOT NULL, "
        "fecha TEXT NOT NULL"
        ")"
    )

    conexion.execute(consulta)
    conexion.commit()

    return conexion


def guardar_avance(
    item,
    lider,
    avance,
    comentario,
    usuario
):
    conexion = conectar_bd()

    consulta = (
        "INSERT INTO avances "
        "(item, lider, avance, comentario, usuario, fecha) "
        "VALUES (?, ?, ?, ?, ?, ?)"
    )

    fecha_actual = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    conexion.execute(
        consulta,
        (
            int(item),
            str(lider),
            int(avance),
            comentario.strip(),
            usuario.strip(),
            fecha_actual
        )
    )

    conexion.commit()
    conexion.close()


def cargar_historial():
    conexion = conectar_bd()

    consulta = (
        "SELECT id, item, lider, avance, comentario, "
        "usuario, fecha "
        "FROM avances "
        "ORDER BY id DESC"
    )

    historial = pd.read_sql_query(
        consulta,
        conexion
    )

    conexion.close()

    return historial


def obtener_ultimos_avances():
    historial = cargar_historial()

    if historial.empty:
        return historial

    historial = historial.sort_values(
        by="id",
        ascending=True
    )

    ultimos = historial.drop_duplicates(
        subset=["item"],
        keep="last"
    )

    return ultimos


def combinar_con_avances(df):
    resultado = df.copy()
    ultimos = obtener_ultimos_avances()

    if ultimos.empty:
        resultado["avance"] = pd.NA
        resultado["comentario"] = ""
        resultado["usuario"] = ""
        resultado["fecha"] = ""

    else:
        columnas = [
            "item",
            "avance",
            "comentario",
            "usuario",
            "fecha"
        ]

        resultado = resultado.merge(
            ultimos[columnas],
            left_on="Itm",
            right_on="item",
            how="left"
        )

    resultado["Avance actual"] = (
        resultado["avance"]
        .fillna(resultado["Avance inicial"])
        .astype(int)
    )

    return resultado


def calcular_estado(avance):
    if avance == 0:
        return "Sin iniciar"

    if avance == 100:
        return "Finalizada"

    return "En proceso"


# ENCABEZADO

st.title("📋 Registro de avances 26-1-PH2")


# LEER INFORMACION

try:
    actividades = cargar_actividades()

except Exception as error:
    st.error("No se pudo cargar correctamente el archivo Excel.")

    st.code(str(error))

    st.info(
        "Verifica que Avances 26-1-PH2.xlsx "
        "este en la misma carpeta que streamlit_app.py."
    )

    st.stop()


lideres = sorted(
    actividades["Líder"]
    .dropna()
    .unique()
    .tolist()
)

if not lideres:
    st.error(
        "No se encontraron lideres en el archivo Excel."
    )

    st.stop()


# MENU

vista = st.sidebar.radio(
    "Menu",
    [
        "Registrar avance",
        "Panel general",
        "Historial"
    ]
)


# REGISTRAR AVANCE

if vista == "Registrar avance":
    st.subheader("Registrar avance")

    lider = st.selectbox(
        "Selecciona el codigo del lider",
        lideres
    )

    pines = obtener_pines()

    if pines:
        pin = st.text_input(
            "PIN",
            type="password"
        )

    else:
        pin = ""

    actividades_lider = actividades[
        actividades["Líder"] == lider
    ].copy()

    actividades_lider = combinar_con_avances(
        actividades_lider
    )

    actividades_lider["Etiqueta"] = (
        actividades_lider.apply(
            lambda fila: (
                str(fila["Ubicación"])
                + " | "
                + str(fila["Nombre de tarea"])
                + " | "
                + str(fila["Avance actual"])
                + "%"
            ),
            axis=1
        )
    )

    st.info(
        "Actividades asignadas a "
        + str(lider)
        + ": "
        + str(len(actividades_lider))
    )

    etiqueta = st.selectbox(
        "Selecciona la actividad",
        actividades_lider["Etiqueta"].tolist()
    )

    fila = actividades_lider[
        actividades_lider["Etiqueta"] == etiqueta
    ].iloc[0]

    columna1, columna2, columna3 = st.columns(3)

    codigo_equipo = str(
        fila["Ubicación"]
    ).strip()

    if not codigo_equipo:
        codigo_equipo = "Sin codigo"

    columna1.metric(
        "Codigo del equipo",
        codigo_equipo
    )

    texto_ot = fila["OT"]

    if not texto_ot:
        texto_ot = "Sin OT"

    columna2.metric(
        "OT",
        texto_ot
    )

    columna3.metric(
        "Avance actual",
        str(int(fila["Avance actual"])) + "%"
    )

    responsable = fila["Responsable"]

    if not responsable:
        responsable = "No indicado"

    st.write(
        "**Responsable:** " + responsable
    )

    fecha_anterior = fila.get("fecha", "")
    usuario_anterior = fila.get("usuario", "")
    comentario_anterior = fila.get(
        "comentario",
        ""
    )

    if pd.notna(fecha_anterior):
        if str(fecha_anterior).strip():
            st.write(
                "**Ultima actualizacion:** "
                + str(fecha_anterior)
            )

    if pd.notna(usuario_anterior):
        if str(usuario_anterior).strip():
            st.write(
                "**Actualizado por:** "
                + str(usuario_anterior)
            )

    if pd.notna(comentario_anterior):
        if str(comentario_anterior).strip():
            st.write(
                "**Ultimo comentario:** "
                + str(comentario_anterior)
            )

    with st.form("formulario_avance"):
        nuevo_avance = st.slider(
            "Nuevo avance (%)",
            min_value=0,
            max_value=100,
            value=int(fila["Avance actual"]),
            step=5
        )

        usuario = st.text_input(
            "Nombre de quien actualiza"
        )

        comentario = st.text_area(
            "Comentario o novedad",
            placeholder=(
                "Ejemplo: actividad terminada, "
                "pendiente prueba de funcionamiento."
            )
        )

        boton_guardar = st.form_submit_button(
            "Guardar avance",
            use_container_width=True
        )

    if boton_guardar:
        if not validar_pin(lider, pin):
            st.error(
                "El PIN no corresponde al lider."
            )

        elif not usuario.strip():
            st.warning(
                "Escribe el nombre de quien actualiza."
            )

        else:
            guardar_avance(
                item=fila["Itm"],
                lider=lider,
                avance=nuevo_avance,
                comentario=comentario,
                usuario=usuario
            )

            st.success(
                "Avance guardado correctamente."
            )

            st.rerun()


# PANEL GENERAL

elif vista == "Panel general":
    st.subheader("Panel general")

    panel = combinar_con_avances(
        actividades
    )

    panel["Estado"] = panel[
        "Avance actual"
    ].apply(calcular_estado)

    total = len(panel)

    finalizadas = int(
        (panel["Avance actual"] == 100).sum()
    )

    en_proceso = int(
        panel["Avance actual"]
        .between(1, 99)
        .sum()
    )

    sin_iniciar = int(
        (panel["Avance actual"] == 0).sum()
    )

    promedio = panel[
        "Avance actual"
    ].mean()

    columna1, columna2, columna3, columna4 = (
        st.columns(4)
    )

    columna1.metric(
        "Actividades",
        total
    )

    columna2.metric(
        "Finalizadas",
        finalizadas
    )

    columna3.metric(
        "En proceso",
        en_proceso
    )

    columna4.metric(
        "Avance promedio",
        f"{promedio:.1f}%"
    )

    st.write(
        "Actividades sin iniciar: "
        + str(sin_iniciar)
    )

    filtro_lideres = st.multiselect(
        "Filtrar por lider",
        lideres
    )

    filtro_estados = st.multiselect(
        "Filtrar por estado",
        [
            "Sin iniciar",
            "En proceso",
            "Finalizada"
        ]
    )

    if filtro_lideres:
        panel = panel[
            panel["Líder"].isin(filtro_lideres)
        ]

    if filtro_estados:
        panel = panel[
            panel["Estado"].isin(filtro_estados)
        ]

    columnas_panel = [
        "Itm",
        "Líder",
        "Activo",
        "Nombre de tarea",
        "OT",
        "Avance inicial",
        "Avance actual",
        "Estado",
        "comentario",
        "usuario",
        "fecha"
    ]

    panel_mostrar = panel[
        columnas_panel
    ].copy()

    panel_mostrar = panel_mostrar.rename(
        columns={
            "comentario": "Ultimo comentario",
            "usuario": "Actualizado por",
            "fecha": "Fecha actualizacion"
        }
    )

    st.dataframe(
        panel_mostrar,
        use_container_width=True,
        hide_index=True
    )

    archivo_panel = panel_mostrar.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "Descargar panel CSV",
        data=archivo_panel,
        file_name="panel_avances_ph2.csv",
        mime="text/csv",
        use_container_width=True
    )


# HISTORIAL

elif vista == "Historial":
    st.subheader("Historial de actualizaciones")

    historial = cargar_historial()

    if historial.empty:
        st.info(
            "Todavia no existen avances registrados."
        )

    else:
        filtro_lideres = st.multiselect(
            "Filtrar historial por lider",
            lideres
        )

        if filtro_lideres:
            historial = historial[
                historial["lider"].isin(
                    filtro_lideres
                )
            ]

        historial_mostrar = historial.rename(
            columns={
                "id": "Registro",
                "item": "Item",
                "lider": "Lider",
                "avance": "Avance",
                "comentario": "Comentario",
                "usuario": "Actualizado por",
                "fecha": "Fecha"
            }
        )

        st.dataframe(
            historial_mostrar,
            use_container_width=True,
            hide_index=True
        )

        archivo_historial = (
            historial_mostrar
            .to_csv(index=False)
            .encode("utf-8-sig")
        )

        st.download_button(
            "Descargar historial CSV",
            data=archivo_historial,
            file_name="historial_avances_ph2.csv",
            mime="text/csv",
            use_container_width=True
        )


# PIE DE PAGINA

st.divider()

st.caption(
    "Seguimiento de actividades del paro de Horno 2."
)
