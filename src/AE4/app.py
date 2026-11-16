"""App de Streamlit · Proyecto integrador (AE4) · Salarios en datos y tecnología.

Ejecutar desde la raíz del repositorio:
    streamlit run src/AE4/app.py

Lee el dataset preparado y las tablas de resultados de la AE3 (src/AE3) y
recalcula las métricas para verificar que coinciden con las del notebook.
"""
import html as _html
import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# --------------------------------------------------------------------------- #
# Configuración y rutas
# --------------------------------------------------------------------------- #
SRC = Path(__file__).resolve().parents[1]          # carpeta src/
DIR_AE3 = SRC / "AE3"
RUTA_PREPARADO = DIR_AE3 / "datos" / "demo-salaries-preparado.csv"
DIR_RESULTADOS = DIR_AE3 / "resultados"

# Escribe aquí los nombres del equipo; se muestran en la barra lateral.
INTEGRANTES: list[str] = []

COLUMNAS_ORIGINALES = [
    "work_year", "experience_level", "employment_type", "job_title", "salary",
    "salary_currency", "salary_in_usd", "employee_residence", "remote_ratio",
    "company_location", "company_size",
]
ORDEN_EXPERIENCIA = ["Inicial", "Intermedio", "Senior", "Ejecutivo"]
ORDEN_TAMANO = ["Pequeña", "Mediana", "Grande"]
ORDEN_MODALIDAD = ["Presencial", "Híbrido", "Remoto"]

# Paleta
NAVY, AZUL, TEAL, AMBAR, GRIS = "#0b2545", "#13315c", "#1f7a8c", "#e9a23b", "#7a8793"
COLOR_MODALIDAD = {"Presencial": GRIS, "Híbrido": AMBAR, "Remoto": TEAL}
COLOR_EXPERIENCIA = {"Inicial": "#9ccfe0", "Intermedio": "#5aa3c4",
                     "Senior": "#2c7da0", "Ejecutivo": "#0b2545"}
FUENTE = "Segoe UI, system-ui, -apple-system, Roboto, Helvetica Neue, Arial, sans-serif"

st.set_page_config(page_title="Salarios en datos y tecnología", page_icon="📊",
                   layout="wide", initial_sidebar_state="expanded")

CSS = """
<style>
html, body, [class*="css"] { font-family: "Segoe UI", system-ui, -apple-system, Roboto, "Helvetica Neue", Arial, sans-serif; }
.block-container { padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1280px; }
#MainMenu, footer { visibility: hidden; }
.stTabs [role="tablist"] {
    gap: .4rem; padding: .4rem; background: #eaf1f6; border: 1px solid #dfe8ef;
    border-radius: 14px;
}
.stTabs [role="tab"] {
    min-height: 2.5rem; padding: .58rem .9rem; border: 1px solid transparent;
    border-radius: 10px; color: #526477; font-size: .86rem; font-weight: 600;
    transition: background .15s ease, color .15s ease, box-shadow .15s ease;
}
.stTabs [role="tab"] p { margin: 0; }
.stTabs [role="tab"]:hover { background: #ffffff; color: #0b2545; }
.stTabs [role="tab"][aria-selected="true"] {
    background: #0b2545; border-color: #0b2545; color: #ffffff;
    box-shadow: 0 2px 6px rgba(11, 37, 69, .16);
}
.stTabs [role="tab"]:focus-visible {
    outline: 2px solid #1f7a8c; outline-offset: 2px;
}
.stTabs [role="tablist"]::after { display: none; }
.stTabs [role="tabpanel"] { padding-top: 1rem; }
.hero { background: linear-gradient(120deg, #0b2545 0%, #13315c 55%, #1f7a8c 100%); border-radius: 18px;
        padding: 2rem 2.3rem; color: #ffffff; margin-bottom: 1.1rem; }
.hero .kicker { text-transform: uppercase; letter-spacing: .12em; font-size: .75rem; color: #9ccfe0; font-weight: 600; }
.hero h1 { font-size: 2.15rem; margin: .35rem 0 .55rem; color: #ffffff; font-weight: 700; letter-spacing: -.01em; line-height: 1.15; padding: 0; }
.hero p { margin: 0; color: #d6e4ef; font-size: 1.02rem; max-width: 60rem; line-height: 1.5; }
.chips { margin-top: 1.1rem; display: flex; flex-wrap: wrap; gap: .5rem; }
.chip { background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.25); color: #ffffff; border-radius: 999px;
        padding: .28rem .8rem; font-size: .82rem; }
.chip.alerta { background: #e9a23b; border-color: #e9a23b; color: #3a2606; font-weight: 600; }
.kpis { display: grid; grid-template-columns: repeat(5, 1fr); gap: .8rem; margin: .4rem 0 1.2rem; }
.kpi { background: #ffffff; border: 1px solid #dfe8ef; border-radius: 14px; padding: 1rem 1.1rem; box-shadow: 0 1px 3px rgba(11,37,69,.06); }
.kpi .v { font-size: 1.75rem; font-weight: 700; color: #0b2545; line-height: 1.1; }
.kpi .l { font-size: .74rem; color: #5b6b7b; text-transform: uppercase; letter-spacing: .06em; margin-top: .35rem; }
.sec-kicker { text-transform: uppercase; letter-spacing: .1em; font-size: .72rem; color: #1f7a8c; font-weight: 700; margin: .2rem 0 .1rem; }
.sec-title { font-size: 1.55rem; font-weight: 700; color: #0b2545; line-height: 1.25; margin: 0 0 .8rem; }
.sub-title { font-size: 1.1rem; font-weight: 700; color: #0b2545; margin: 1.3rem 0 .6rem; }
.hallazgo { background: #fff6e3; border: 1px solid #f1d49a; border-left: 5px solid #e9a23b; border-radius: 12px;
            padding: .85rem 1.1rem; color: #4a3410; margin: .2rem 0 1rem; line-height: 1.5; }
.hallazgo b { color: #2e1f06; }
.metrica { display: grid; grid-template-columns: 1.4fr 1.4fr 1fr; gap: .8rem; margin: 0 0 1rem; }
.metrica > div { background: #ffffff; border: 1px solid #dfe8ef; border-radius: 12px; padding: .75rem 1rem; color: #1b2a3a; font-size: .9rem; line-height: 1.45; }
.metrica span { display: block; text-transform: uppercase; letter-spacing: .08em; font-size: .68rem; color: #1f7a8c; font-weight: 700; margin-bottom: .2rem; }
.trio { display: grid; grid-template-columns: repeat(3, 1fr); gap: .9rem; margin: 1rem 0 .6rem; }
.duo { display: grid; grid-template-columns: repeat(2, 1fr); gap: .9rem; margin: .5rem 0 .8rem; }
.cuatro { display: grid; grid-template-columns: repeat(4, 1fr); gap: .9rem; margin: .3rem 0 1.2rem; }
.card { background: #ffffff; border: 1px solid #dfe8ef; border-radius: 14px; padding: 1.05rem 1.2rem; color: #1b2a3a;
        box-shadow: 0 1px 3px rgba(11,37,69,.05); font-size: .93rem; line-height: 1.55; }
.card h4 { margin: 0 0 .55rem; padding: 0; font-size: .74rem; text-transform: uppercase; letter-spacing: .09em; color: #1f7a8c; font-weight: 700; }
.card.lim h4 { color: #b4571b; }
.card.verde h4 { color: #2b7a4b; }
.card p { margin: 0; }
.card ul { margin: 0; padding-left: 1.1rem; }
.card li { margin-bottom: .35rem; }
.card .num { font-size: 1.5rem; font-weight: 700; color: #0b2545; line-height: 1; margin-bottom: .45rem; }
.pill { border-radius: 10px; padding: .6rem .8rem; font-size: .85rem; line-height: 1.4; }
.pill.ok { background: #e4f4ea; color: #17562f; border: 1px solid #b7e0c6; }
.pill.mal { background: #fde8e6; color: #8a1f17; border: 1px solid #f3b8b3; }
.pill.neutro { background: #eef2f6; color: #45566a; border: 1px solid #d5dee7; }
.pie { margin-top: 2.2rem; padding-top: 1rem; border-top: 1px solid #d8e2ea; color: #5b6b7b; font-size: .8rem; line-height: 1.5; }
@media (max-width: 900px) {
    .kpis, .trio, .duo, .cuatro, .metrica { grid-template-columns: 1fr; }
    .stTabs [role="tablist"] { gap: .25rem; padding: .3rem; }
    .stTabs [role="tab"] { padding: .52rem .7rem; font-size: .81rem; }
}
</style>
"""


# --------------------------------------------------------------------------- #
# Utilidades de formato y de presentación
# --------------------------------------------------------------------------- #
def num(x, dec: int = 0) -> str:
    texto = f"{x:,.{dec}f}"
    return texto.replace(",", "§").replace(".", ",").replace("§", ".")


def usd(x) -> str:
    return f"USD {num(x)}"


def pct(x, dec: int = 1) -> str:
    return f"{num(x, dec)} %"


def esc(x) -> str:
    return _html.escape(str(x))


def html(contenido: str) -> None:
    """Escribe HTML en una sola línea (evita que Markdown lo interprete como código)."""
    st.markdown(re.sub(r"\n\s*", "", contenido), unsafe_allow_html=True)


def ul(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def encabezado(kicker: str, titulo: str) -> None:
    html(f'<div class="sec-kicker">{kicker}</div><div class="sec-title">{titulo}</div>')


def hallazgo(texto: str) -> None:
    html(f'<div class="hallazgo"><b>Hallazgo principal.</b> {texto}</div>')


def metrica(nombre: str, calculo: str, unidad: str) -> None:
    html(f'<div class="metrica"><div><span>Métrica</span>{nombre}</div>'
         f'<div><span>Cálculo</span>{calculo}</div><div><span>Unidad</span>{unidad}</div></div>')


def lectura(muestran: list[str], interpretacion: str, limitaciones: str) -> None:
    html('<div class="trio">'
         f'<div class="card"><h4>Qué muestran los datos</h4>{ul(muestran)}</div>'
         f'<div class="card verde"><h4>Lectura analítica</h4><p>{interpretacion}</p></div>'
         f'<div class="card lim"><h4>Limitaciones</h4><p>{limitaciones}</p></div></div>')


def estilo(fig: go.Figure, titulo: str, alto: int = 460, leyenda: bool = True) -> go.Figure:
    fig.update_layout(
        template="plotly_white", height=alto, font=dict(family=FUENTE, size=13, color="#1b2a3a"),
        title=dict(text=titulo, x=0.0, xanchor="left", y=0.97, yanchor="top",
                   font=dict(size=16, color=NAVY)),
        margin=dict(t=72, l=12, r=12, b=84 if leyenda else 48),
        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff", showlegend=leyenda,
        separators=",.", uniformtext_minsize=11, uniformtext_mode="hide",
        legend=dict(orientation="h", yanchor="top", y=-0.2, x=0.0, title_text=""),
        hoverlabel=dict(font_size=13, font_family=FUENTE))
    fig.update_xaxes(showgrid=False, linecolor="#c9d4de", ticks="outside", tickcolor="#c9d4de")
    fig.update_yaxes(gridcolor="#e9eef3", zeroline=False)
    return fig


def mostrar(fig: go.Figure) -> None:
    with st.container(border=True):
        st.plotly_chart(fig, width="stretch", theme=None)


# --------------------------------------------------------------------------- #
# Carga de datos y métricas (mismos cálculos que el notebook de la AE3)
# --------------------------------------------------------------------------- #
@st.cache_data(show_spinner=False)
def cargar():
    df = pd.read_csv(RUTA_PREPARADO, encoding="utf-8-sig")
    nombres = {
        "principal": "pregunta_principal_salarios_por_grupo",
        "apoyo1": "pregunta_apoyo_1_registros_por_anio_experiencia_empleo",
        "apoyo2": "pregunta_apoyo_2_cargos_por_registros_y_mediana",
        "apoyo3": "pregunta_apoyo_3_salario_mediano_por_anio",
        "comparacion": "comparacion_antes_despues",
    }
    res = {k: pd.read_csv(DIR_RESULTADOS / f"{v}.csv", encoding="utf-8-sig")
           for k, v in nombres.items()}
    return df, res


def m_principal(d: pd.DataFrame) -> pd.DataFrame:
    return (d.groupby(["experience_level", "remote_work_mode", "company_size"], observed=True)
            .agg(cantidad_registros=("salary_in_usd", "size"),
                 salario_usd_mediana=("salary_in_usd", "median"),
                 salario_usd_promedio=("salary_in_usd", "mean"),
                 salario_usd_q1=("salary_in_usd", lambda v: v.quantile(0.25)),
                 salario_usd_q3=("salary_in_usd", lambda v: v.quantile(0.75)))
            .reset_index())


def m_apoyo1(d: pd.DataFrame) -> pd.DataFrame:
    return (d.groupby(["work_year", "experience_level", "employment_type"], observed=True)
            .size().reset_index(name="cantidad_registros"))


def m_apoyo2(d: pd.DataFrame) -> pd.DataFrame:
    return (d.groupby("job_title", observed=True)
            .agg(cantidad_registros=("salary_in_usd", "size"),
                 salario_usd_mediana=("salary_in_usd", "median"))
            .reset_index()
            .sort_values(["cantidad_registros", "job_title"], ascending=[False, True])
            .reset_index(drop=True))


def m_apoyo3(d: pd.DataFrame) -> pd.DataFrame:
    t = (d.groupby("work_year", observed=True)
         .agg(cantidad_registros=("salary_in_usd", "size"),
              salario_usd_mediano=("salary_in_usd", "median"))
         .reset_index().sort_values("work_year").reset_index(drop=True))
    t["variacion_mediana_usd_vs_anio_anterior"] = t["salario_usd_mediano"].diff()
    t["variacion_mediana_porcentual_vs_anio_anterior"] = t["salario_usd_mediano"].pct_change() * 100
    return t


@st.cache_data(show_spinner=False)
def verificar(df: pd.DataFrame, res: dict) -> dict[str, bool]:
    """Compara lo que calcula la app con los CSV que generó el notebook."""
    pares = {
        "Comparación salarial": (m_principal(df), res["principal"],
                                 ["experience_level", "remote_work_mode", "company_size"]),
        "Composición de la muestra": (m_apoyo1(df), res["apoyo1"],
                                      ["work_year", "experience_level", "employment_type"]),
        "Cargos frecuentes": (m_apoyo2(df), res["apoyo2"], ["job_title"]),
        "Tendencia anual": (m_apoyo3(df), res["apoyo3"], ["work_year"]),
    }
    estado = {}
    for nombre, (calculada, csv, claves) in pares.items():
        a = calculada.sort_values(claves).reset_index(drop=True)
        b = csv.sort_values(claves).reset_index(drop=True)
        try:
            pd.testing.assert_frame_equal(a[list(b.columns)], b, check_dtype=False,
                                          check_exact=False, rtol=1e-9)
            estado[nombre] = True
        except AssertionError:
            estado[nombre] = False
    return estado


# --------------------------------------------------------------------------- #
# Datos, barra lateral y encabezado
# --------------------------------------------------------------------------- #
html(CSS)
df_total, res = cargar()
verificacion = verificar(df_total, res)

with st.sidebar:
    st.markdown("### 📊 Salarios en datos y tecnología")
    st.caption("Proyecto integrador · Analítica de datos")
    st.markdown("**Análisis de sensibilidad**")
    sin_repetidas = st.toggle(
        "Excluir filas repetidas",
        help="Por defecto se usan las 3.755 filas, igual que el notebook. Al activarlo se "
             "descartan las repeticiones exactas para ver cuánto cambian los resultados.")
    st.markdown("**Verificación con el notebook**")
    if sin_repetidas:
        html('<div class="pill neutro">Omitida: esta vista no usa todas las filas.</div>')
    elif all(verificacion.values()):
        html(f'<div class="pill ok">✔ Las {len(verificacion)} tablas de métricas coinciden con '
             'los CSV generados por el notebook.</div>')
    else:
        fallidas = ", ".join(k for k, ok in verificacion.items() if not ok)
        html(f'<div class="pill mal">✖ No coinciden con el notebook: {esc(fallidas)}.</div>')
    if INTEGRANTES:
        st.markdown("**Equipo**")
        for nombre in INTEGRANTES:
            st.write(f"• {nombre}")
    st.caption("Fuente de los datos: `Einstellung/demo-salaries` (Hugging Face).")

d = df_total.drop_duplicates(subset=COLUMNAS_ORIGINALES) if sin_repetidas else df_total
periodo = f"{int(d['work_year'].min())}–{int(d['work_year'].max())}"

chips = (f'<span class="chip">Dataset Einstellung/demo-salaries</span>'
         f'<span class="chip">Periodo {periodo}</span>'
         f'<span class="chip">{num(len(d))} registros</span>')
if sin_repetidas:
    chips += (f'<span class="chip alerta">Vista sin filas repetidas: se excluyeron '
              f'{num(len(df_total) - len(d))}</span>')
html('<div class="hero"><div class="kicker">Proyecto integrador · Métricas y visualización de datos</div>'
     '<h1>Salarios en datos y tecnología</h1>'
     '<p>Comparación descriptiva de los salarios en dólares según la experiencia, la modalidad de '
     'trabajo y el tamaño de la empresa, a partir de un dataset público de salarios reportados.</p>'
     f'<div class="chips">{chips}</div></div>')

# --------------------------------------------------------------------------- #
# Cálculos compartidos por varias secciones
# --------------------------------------------------------------------------- #
def resumen_grupo(columna, orden):
    """Mediana y n por categoría, y qué tan distinta es la mezcla del grupo de mediana más baja."""
    meds = d.groupby(columna)["salary_in_usd"].median().reindex(orden)
    ns = d.groupby(columna).size().reindex(orden)
    bajo = meds.idxmin()
    es_bajo = d[columna] == bajo
    ini = d.loc[es_bajo, "experience_level"].eq("Inicial").mean() * 100
    ini_r = d.loc[~es_bajo, "experience_level"].eq("Inicial").mean() * 100
    eeuu = d.loc[es_bajo, "company_location"].eq("US").mean() * 100
    eeuu_r = d.loc[~es_bajo, "company_location"].eq("US").mean() * 100
    return meds, ns, bajo, ini, ini_r, eeuu, eeuu_r


med_exp = d.groupby("experience_level")["salary_in_usd"].median().reindex(ORDEN_EXPERIENCIA)
med_mod, n_mod, bajo_mod, ini_mod, ini_mod_r, us_mod, us_mod_r = resumen_grupo("remote_work_mode", ORDEN_MODALIDAD)
med_tam, n_tam, bajo_tam, ini_tam, ini_tam_r, us_tam, us_tam_r = resumen_grupo("company_size", ORDEN_TAMANO)

a1 = m_apoyo1(d)
a2 = m_apoyo2(d)
a3 = m_apoyo3(d)
tot_anio = a1.groupby("work_year")["cantidad_registros"].sum()
senior = a1[a1["experience_level"] == "Senior"].groupby("work_year")["cantidad_registros"].sum()
p_sen = (senior / tot_anio * 100).reindex(tot_anio.index).fillna(0)
anios = list(tot_anio.index)
emp = (a1.groupby("employment_type", as_index=False)["cantidad_registros"].sum()
       .sort_values("cantidad_registros"))
emp["participacion"] = emp["cantidad_registros"] / emp["cantidad_registros"].sum() * 100
ft = emp.set_index("employment_type").loc["Tiempo completo"]
c1, c2 = a2.iloc[0], a2.iloc[1]
top10 = a2.head(10)
f_a3, u_a3 = a3.iloc[0], a3.iloc[-1]

(tab_res, tab_grupos, tab_dist, tab_cargos, tab_evol, tab_fin) = st.tabs([
    "Resumen", "Salarios por grupo", "Distribución de los datos", "Cargos",
    "Evolución anual", "Conclusiones"])

# --------------------------------------------------------------------------- #
# Resumen
# --------------------------------------------------------------------------- #
with tab_res:
    encabezado("Contexto", "Alcance del análisis y los datos")
    html('<div class="card"><h4>Propósito del análisis</h4><p>Describir los salarios reportados en '
         'el dataset y explorar cómo se distribuyen según la experiencia, la modalidad de trabajo, '
         'el tamaño de la empresa, el cargo y el año de referencia. Los resultados son descriptivos '
         'y se limitan a los registros disponibles.</p></div>')
    html('<div class="sub-title">Preguntas que orientan el análisis</div>')
    html('<div class="cuatro">'
         '<div class="card"><h4>Comparación salarial</h4><p>¿Cómo se comparan '
         'los salarios en USD por experiencia, modalidad y tamaño de empresa?</p></div>'
         '<div class="card"><h4>Composición de la muestra</h4><p>¿Cuántos registros hay '
         'por año, nivel de experiencia y tipo de empleo?</p></div>'
         '<div class="card"><h4>Cargos frecuentes</h4><p>¿Qué cargos tienen más registros y cuál '
         'es su salario mediano?</p></div>'
         '<div class="card"><h4>Tendencia anual</h4><p>¿Cómo cambia el salario mediano '
         'entre los años disponibles?</p></div></div>')
    html('<div class="sub-title">El dataset en cifras</div>')
    html('<div class="kpis">'
         f'<div class="kpi"><div class="v">{num(len(d))}</div><div class="l">Registros</div></div>'
         f'<div class="kpi"><div class="v">{num(d["job_title"].nunique())}</div><div class="l">Cargos distintos</div></div>'
         f'<div class="kpi"><div class="v">{periodo}</div><div class="l">Periodo (work_year)</div></div>'
         f'<div class="kpi"><div class="v">{num(int(d.isna().sum().sum()))}</div><div class="l">Valores nulos</div></div>'
         f'<div class="kpi"><div class="v">{num(int(d.duplicated(subset=COLUMNAS_ORIGINALES).sum()))}</div>'
         '<div class="l">Filas repetidas</div></div></div>')
    html('<div class="duo">'
         '<div class="card"><h4>Qué contiene</h4><p>Un registro por salario reportado: año, experiencia, '
         'tipo de empleo, cargo, salario original y en USD, residencia del empleado, porcentaje remoto, '
         'ubicación y tamaño de la empresa. <b>No</b> tiene identificador de persona ni de empresa, ni fecha '
         'exacta, y la periodicidad del salario no está especificada.</p></div>'
         '<div class="card"><h4>Qué se hizo en la preparación (AE3)</h4><p>Se tradujeron los códigos a '
         'etiquetas legibles y se crearon variables derivadas: <code>remote_work_mode</code>, '
         '<code>experience_level_order</code>, <code>company_size_order</code>, '
         '<code>work_location_relation</code> y <code>salary_usd_quartile</code>.</p></div></div>')
    with st.expander("Ver una muestra del dataset preparado"):
        st.dataframe(d.head(20), width="stretch", hide_index=True)
    html('<div class="pie">Los salarios no son ingresos ni rentabilidad de ninguna empresa: son los valores '
         'registrados por persona. Esta aplicación describe el dataset; no demuestra causas.</div>')

# --------------------------------------------------------------------------- #
# Salarios por grupo
# --------------------------------------------------------------------------- #
with tab_grupos:
    encabezado("Comparación salarial",
               "¿Cómo se comparan los salarios por experiencia, modalidad y tamaño de empresa?")
    hallazgo(f"La experiencia es lo que mejor ordena los salarios: la mediana va de "
             f"<b>{usd(med_exp['Inicial'])}</b> (Inicial) a <b>{usd(med_exp['Ejecutivo'])}</b> (Ejecutivo).")
    metrica("Mediana del salario en USD (<code>salary_in_usd</code>) de cada grupo, con su rango Q1–Q3 "
            "(barra de error) y el número de registros (n).",
            "Se agrupan los registros por experiencia × modalidad × tamaño de empresa y se toma el valor "
            "central de los salarios ordenados; Q1 y Q3 son los cuartiles 25 y 75.",
            "USD (periodicidad no especificada)")
    n_min = st.slider("Mostrar solo grupos con al menos n registros", 1, 50, 10,
                      help="Los grupos con pocos registros tienen medianas poco confiables.")
    t_all = m_principal(d)
    t = t_all[t_all["cantidad_registros"] >= n_min].copy()
    t["arriba"] = t["salario_usd_q3"] - t["salario_usd_mediana"]
    t["abajo"] = t["salario_usd_mediana"] - t["salario_usd_q1"]
    fig = px.bar(
        t, x="experience_level", y="salario_usd_mediana", color="remote_work_mode",
        facet_col="company_size", barmode="group", error_y="arriba", error_y_minus="abajo",
        category_orders={"experience_level": ORDEN_EXPERIENCIA, "company_size": ORDEN_TAMANO,
                         "remote_work_mode": ORDEN_MODALIDAD},
        color_discrete_map=COLOR_MODALIDAD,
        labels={"experience_level": "Nivel de experiencia",
                "salario_usd_mediana": "Mediana salarial (USD)",
                "remote_work_mode": "Modalidad"},
        hover_data={"cantidad_registros": True, "salario_usd_q1": ":,.0f",
                    "salario_usd_q3": ":,.0f", "arriba": False, "abajo": False})
    fig.for_each_annotation(lambda a: a.update(text="Empresa " + a.text.split("=")[-1].lower()))
    fig.update_traces(error_y=dict(color="#4a5b6b", thickness=1.2))
    estilo(fig, f"Mediana salarial en USD por experiencia, modalidad y tamaño de empresa ({periodo})", 500)
    fig.update_yaxes(tickformat=",.0f")
    mostrar(fig)
    ocultos = t_all[t_all["cantidad_registros"] < n_min]
    if len(ocultos):
        st.caption(f"Se ocultaron {len(ocultos)} de {len(t_all)} grupos con menos de {n_min} registros "
                   f"({num(int(ocultos['cantidad_registros'].sum()))} registros en total).")
    top = t.loc[t["salario_usd_mediana"].idxmax()]
    lectura(
        [f"<b>Experiencia:</b> " + ", ".join(f"{k} {usd(v)}" for k, v in med_exp.items()) + ".",
         "<b>Modalidad:</b> " + ", ".join(f"{k} {usd(med_mod[k])} (n = {num(n_mod[k])})" for k in ORDEN_MODALIDAD) + ".",
         "<b>Tamaño de empresa:</b> " + ", ".join(f"{k} {usd(med_tam[k])} (n = {num(n_tam[k])})" for k in ORDEN_TAMANO) + ".",
         f"<b>Mayor mediana entre los grupos mostrados:</b> {top['experience_level']}, "
         f"{top['remote_work_mode'].lower()}, empresa {top['company_size'].lower()}: "
         f"{usd(top['salario_usd_mediana'])} (n = {num(int(top['cantidad_registros']))})."],
        "La experiencia ordena los salarios de forma clara. También hay diferencias por modalidad y tamaño: "
        f"la mediana más baja es la de la modalidad <b>{bajo_mod.lower()}</b> (n = {num(n_mod[bajo_mod])}) y la de las "
        f"empresas <b>{bajo_tam.lower()}s</b> (n = {num(n_tam[bajo_tam])}). Pero esos grupos son pequeños y tienen "
        f"otra mezcla: la modalidad {bajo_mod.lower()} tiene {pct(ini_mod)} de registros de nivel Inicial (resto: "
        f"{pct(ini_mod_r)}) y {pct(us_mod)} de empresas en EE. UU. (resto: {pct(us_mod_r)}); las empresas "
        f"{bajo_tam.lower()}s, {pct(ini_tam)} de nivel Inicial (resto: {pct(ini_tam_r)}) y {pct(us_tam)} en EE. UU. "
        f"(resto: {pct(us_tam_r)}). Por eso no se atribuye la diferencia a la modalidad ni al tamaño. Como lectura "
        "descriptiva, la experiencia permite ordenar los salarios; las diferencias por modalidad y tamaño deben "
        "interpretarse con cautela al variar también la experiencia y el país.",
        "Las diferencias describen este dataset; no demuestran que la experiencia, la modalidad o el tamaño de la "
        "empresa <i>causen</i> diferencias salariales. Los grupos difieren a la vez en experiencia, país y cargo, y "
        "muchos tienen pocos registros. Son salarios, no rentabilidad ni productividad.")
    with st.expander("Ver la tabla de datos de este gráfico"):
        st.dataframe(t_all.round(0), width="stretch", hide_index=True)

# --------------------------------------------------------------------------- #
# Distribución de los datos
# --------------------------------------------------------------------------- #
with tab_dist:
    encabezado("Composición de la muestra",
               "¿Cuántos registros hay por año, nivel de experiencia y tipo de empleo?")
    rango_anios = st.slider(
        "Periodo de referencia",
        min_value=int(d["work_year"].min()),
        max_value=int(d["work_year"].max()),
        value=(int(d["work_year"].min()), int(d["work_year"].max())),
        step=1,
    )
    d_rango = d[d["work_year"].between(*rango_anios)]
    niveles_disponibles = [
        nivel for nivel in ORDEN_EXPERIENCIA
        if d_rango["experience_level"].eq(nivel).any()
    ]
    niveles_seleccionados = st.multiselect(
        "Nivel de experiencia",
        options=niveles_disponibles,
        default=niveles_disponibles,
        help="Selecciona los niveles que quieras incluir. Si no eliges ninguno, se incluyen todos.",
    )
    niveles_activos = niveles_seleccionados or niveles_disponibles
    d_dist = d_rango[d_rango["experience_level"].isin(niveles_activos)]
    st.caption(
        "Los filtros actualizan ambas gráficas y el resumen de esta sección; "
        "las demás pestañas no cambian."
    )
    a1_dist = m_apoyo1(d_dist)
    tot_anio_dist = a1_dist.groupby("work_year")["cantidad_registros"].sum()
    senior_dist = (a1_dist[a1_dist["experience_level"] == "Senior"]
                   .groupby("work_year")["cantidad_registros"].sum())
    p_sen_dist = (senior_dist / tot_anio_dist * 100).reindex(tot_anio_dist.index).fillna(0)
    anios_dist = list(tot_anio_dist.index)
    emp_dist = (d_dist.groupby("employment_type", as_index=False).size()
                .rename(columns={"size": "cantidad_registros"})
                .sort_values("cantidad_registros"))
    emp_dist["participacion"] = emp_dist["cantidad_registros"] / len(d_dist) * 100
    n_tiempo_completo = int(emp_dist.loc[
        emp_dist["employment_type"] == "Tiempo completo", "cantidad_registros"
    ].sum())
    pct_tiempo_completo = n_tiempo_completo / len(d_dist) * 100
    periodo_dist = f"{int(d_dist['work_year'].min())}–{int(d_dist['work_year'].max())}"
    conteo_anio = d_dist.groupby("work_year").size()
    anio_mayor = int(conteo_anio.idxmax())
    hallazgo(f"El periodo seleccionado reúne <b>{num(len(d_dist))}</b> registros; "
             f"{anio_mayor} concentra la mayor cantidad ({num(int(conteo_anio.max()))}).")
    metrica("Número de registros y su participación (%) dentro de cada año o del total.",
            "Conteo de filas por año de referencia (<code>work_year</code>), nivel de experiencia y tipo de "
            "empleo; participación = registros de la categoría / registros del grupo × 100.",
            "Registros y porcentaje")
    vista = st.radio("Ver como", ["Número de registros", "Porcentaje del año"], horizontal=True)
    por_anio = a1_dist.groupby(["work_year", "experience_level"], as_index=False)["cantidad_registros"].sum()
    fig = px.bar(por_anio, x="work_year", y="cantidad_registros", color="experience_level",
                 barmode="relative", text_auto=",.0f",
                 category_orders={"experience_level": niveles_activos},
                 color_discrete_map=COLOR_EXPERIENCIA,
                 labels={"work_year": "Año de referencia", "cantidad_registros": "Registros",
                         "experience_level": "Experiencia"})
    if vista == "Porcentaje del año":
        fig.update_layout(barnorm="percent")
        fig.update_yaxes(title_text="% del año · niveles seleccionados")
        fig.update_traces(texttemplate="%{y:.0f}%")
    fig.update_xaxes(type="category")
    estilo(fig, f"Registros por año de referencia y nivel de experiencia ({periodo_dist})", 470)
    mostrar(fig)

    emp_dist["etiqueta"] = [
        f"{num(r)} ({pct(p)})"
        for r, p in zip(emp_dist["cantidad_registros"], emp_dist["participacion"])
    ]
    fig2 = px.bar(emp_dist, x="cantidad_registros", y="employment_type", orientation="h", text="etiqueta",
                  labels={"cantidad_registros": "Registros", "employment_type": "Tipo de empleo"},
                  color_discrete_sequence=[TEAL])
    fig2.update_traces(textposition="outside", cliponaxis=False)
    fig2.update_xaxes(range=[0, emp_dist["cantidad_registros"].max() * 1.3])
    estilo(fig2, f"Registros por tipo de empleo ({periodo_dist})", 330, leyenda=False)
    mostrar(fig2)

    hallazgos_dist = [
        "<b>Por año:</b> " + ", ".join(f"{a}: {num(v)}" for a, v in tot_anio_dist.items()) + " registros.",
        "<b>Niveles incluidos:</b> " + ", ".join(niveles_activos) + ".",
        f"<b>Tipo de empleo:</b> tiempo completo representa {num(n_tiempo_completo)} registros "
        f"({pct(pct_tiempo_completo)}).",
    ]
    if "Senior" in niveles_activos:
        if anios_dist[0] == anios_dist[-1]:
            participacion_senior = (
                f"<b>Participación Senior:</b> {pct(p_sen_dist.iloc[0])} en {anios_dist[0]}."
            )
        else:
            participacion_senior = (
                f"<b>Participación Senior:</b> {pct(p_sen_dist.iloc[0])} en {anios_dist[0]} y "
                f"{pct(p_sen_dist.iloc[-1])} en {anios_dist[-1]}."
            )
        hallazgos_dist.insert(1, participacion_senior)
    lectura(
        hallazgos_dist,
        "Permite observar cómo se distribuyen los registros entre años y categorías, y en qué grupos hay "
        "más o menos observaciones.",
        "Los conteos describen el dataset, no el mercado laboral. El crecimiento de registros entre años puede "
        "deberse a cuántos datos se recopilaron y no a un cambio real. Los tipos de empleo distintos de tiempo "
        "completo tienen muy pocos registros.")
    with st.expander("Ver la tabla de datos de este gráfico"):
        st.dataframe(a1_dist, width="stretch", hide_index=True)

# --------------------------------------------------------------------------- #
# Cargos
# --------------------------------------------------------------------------- #
with tab_cargos:
    encabezado("Frecuencia por cargo", "¿Qué cargos tienen más registros y cuál es su salario mediano?")
    metrica("Registros por cargo (con su participación en el total) y mediana del salario en USD.",
            "Conteo de filas por <code>job_title</code>; participación = registros del cargo / registros totales "
            "× 100; mediana de <code>salary_in_usd</code> de cada cargo.",
            "Registros, % y USD")
    n_top = st.slider("Cantidad de cargos a mostrar (los más frecuentes)", 5, 20, 10)
    top_c = a2.head(n_top).copy()
    top_c["participacion"] = top_c["cantidad_registros"] / len(d) * 100
    orden_cargos = list(top_c["job_title"][::-1])
    top_c["etq_reg"] = [f"{num(r)} ({pct(p)})" for r, p in zip(top_c["cantidad_registros"], top_c["participacion"])]
    top_c["etq_med"] = [f"{usd(m)} · n={num(r)}" for m, r in zip(top_c["salario_usd_mediana"], top_c["cantidad_registros"])]
    mayor = top_c.loc[top_c["salario_usd_mediana"].idxmax()]
    menor = top_c.loc[top_c["salario_usd_mediana"].idxmin()]
    hallazgo(f"<b>{esc(c1['job_title'])}</b> es el cargo con más registros ({num(c1['cantidad_registros'])}), "
             f"y los {n_top} más frecuentes reúnen <b>{pct(top_c['participacion'].sum())}</b> de los datos.")
    col_a, col_b = st.columns(2)
    f3a = px.bar(top_c, x="cantidad_registros", y="job_title", orientation="h", text="etq_reg",
                 category_orders={"job_title": orden_cargos}, color_discrete_sequence=[TEAL],
                 labels={"cantidad_registros": "Registros", "job_title": "Cargo"})
    f3a.update_traces(textposition="outside", cliponaxis=False)
    f3a.update_xaxes(range=[0, top_c["cantidad_registros"].max() * 1.4])
    estilo(f3a, f"Registros por cargo ({periodo})", 150 + 38 * n_top, leyenda=False)
    with col_a:
        mostrar(f3a)
    f3b = px.bar(top_c, x="salario_usd_mediana", y="job_title", orientation="h", text="etq_med",
                 category_orders={"job_title": orden_cargos}, color_discrete_sequence=[AMBAR],
                 labels={"salario_usd_mediana": "Mediana salarial (USD)", "job_title": "Cargo"})
    f3b.update_traces(textposition="outside", cliponaxis=False)
    f3b.update_xaxes(range=[0, top_c["salario_usd_mediana"].max() * 1.55], tickformat=",.0f")
    estilo(f3b, f"Mediana salarial por cargo, en USD ({periodo})", 150 + 38 * n_top, leyenda=False)
    with col_b:
        mostrar(f3b)
    interpretacion = ""
    if c1["job_title"] != mayor["job_title"]:
        interpretacion = (f"El cargo con más registros ({esc(c1['job_title'])}) no es el de mayor mediana entre los "
                          f"mostrados ({esc(mayor['job_title'])}): ambas medidas cuentan cosas distintas. ")
    interpretacion += ("La frecuencia y la mediana describen aspectos distintos; el número de registros ayuda a "
                       "contextualizar cada mediana.")
    lectura(
        [f"<b>Más registros:</b> {esc(c1['job_title'])} ({num(c1['cantidad_registros'])}; mediana "
         f"{usd(c1['salario_usd_mediana'])}) y {esc(c2['job_title'])} ({num(c2['cantidad_registros'])}; mediana "
         f"{usd(c2['salario_usd_mediana'])}).",
         f"<b>Concentración:</b> los {n_top} cargos más frecuentes reúnen {pct(top_c['participacion'].sum())} de "
         f"los registros, de {num(len(a2))} cargos distintos.",
         f"<b>Entre los {n_top} mostrados,</b> la mediana más alta es {esc(mayor['job_title'])} "
         f"({usd(mayor['salario_usd_mediana'])}) y la más baja {esc(menor['job_title'])} "
         f"({usd(menor['salario_usd_mediana'])})."],
        interpretacion,
        "Las medianas de cargos con pocos registros son poco confiables (por eso se muestra n). Los cargos no "
        "son comparables sin controlar experiencia, país y tamaño de la empresa. No son recomendaciones "
        "salariales ni representan necesariamente el mercado.")
    with st.expander("Ver la tabla completa de cargos"):
        st.dataframe(a2, width="stretch", hide_index=True)

# --------------------------------------------------------------------------- #
# Evolución anual
# --------------------------------------------------------------------------- #
with tab_evol:
    encabezado("Tendencia anual", "¿Cómo cambia el salario mediano entre los años disponibles?")
    hallazgo(f"La mediana pasó de <b>{usd(f_a3['salario_usd_mediano'])}</b> en {int(f_a3['work_year'])} a "
             f"<b>{usd(u_a3['salario_usd_mediano'])}</b> en {int(u_a3['work_year'])}, pero los registros pasaron de "
             f"{num(f_a3['cantidad_registros'])} a {num(u_a3['cantidad_registros'])}.")
    metrica("Mediana anual del salario en USD y su variación frente al año anterior (USD y %).",
            "Mediana de <code>salary_in_usd</code> por <code>work_year</code>; variación = mediana del año − "
            "mediana del año anterior; variación % = variación / mediana anterior × 100.",
            "USD y porcentaje")
    etiquetas_anio = [f"{int(a)}<br>n = {num(n)}" for a, n in zip(a3["work_year"], a3["cantidad_registros"])]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=etiquetas_anio, y=a3["cantidad_registros"], name="Registros (n)",
                         marker_color="#d5dee7"), secondary_y=False)
    fig.add_trace(go.Scatter(x=etiquetas_anio, y=a3["salario_usd_mediano"],
                             name="Mediana salarial (USD)", mode="lines+markers+text",
                             line=dict(color=NAVY, width=3), marker=dict(size=9),
                             text=[usd(v) for v in a3["salario_usd_mediano"]],
                             textposition="top center"), secondary_y=True)
    fig.update_yaxes(title_text="Registros", secondary_y=False)
    fig.update_yaxes(title_text="Mediana salarial (USD)", tickformat=",.0f",
                     range=[0, a3["salario_usd_mediano"].max() * 1.3], secondary_y=True, showgrid=False)
    fig.update_xaxes(title_text="Año de referencia")
    estilo(fig, f"Mediana salarial en USD y número de registros por año ({periodo})", 470)
    mostrar(fig)

    sub = (d.groupby(["work_year", "experience_level"]).agg(n=("salary_in_usd", "size"),
           mediana=("salary_in_usd", "median")).reset_index())
    sub = sub[sub["n"] >= 10]
    fig2 = px.line(sub, x=sub["work_year"].astype(str), y="mediana", color="experience_level", markers=True,
                   category_orders={"experience_level": ORDEN_EXPERIENCIA},
                   color_discrete_map=COLOR_EXPERIENCIA, hover_data={"n": True},
                   labels={"x": "Año de referencia", "mediana": "Mediana salarial (USD)",
                           "experience_level": "Experiencia"})
    fig2.update_traces(line=dict(width=3), marker=dict(size=8))
    fig2.update_yaxes(tickformat=",.0f")
    estilo(fig2, "Vista complementaria: mediana por año dentro de cada nivel de experiencia "
                 "(grupos con al menos 10 registros)", 450)
    mostrar(fig2)
    st.caption("Esta segunda vista se calcula en la app a partir del dataset preparado; no es una tabla del "
               "notebook. Sirve para ver si el cambio de la mediana se mantiene dentro de cada nivel.")

    piv = sub.pivot(index="experience_level", columns="work_year", values="mediana").reindex(ORDEN_EXPERIENCIA)
    anios_comp = [c for c in piv.columns if piv[c].notna().all()]
    dentro = []
    if len(anios_comp) >= 2:
        a_ref, a_fin = anios_comp[0], anios_comp[-1]
        cambios = ((piv[a_fin] / piv[a_ref] - 1) * 100).round(1)
        dentro = [f"<b>Dentro de cada nivel</b> (de {a_ref} a {a_fin}): "
                  + ", ".join(f"{k} {'+' if v >= 0 else ''}{num(v, 1)} %" for k, v in cambios.items()) + "."]
    mx = a3.loc[a3["variacion_mediana_usd_vs_anio_anterior"].idxmax()]
    lectura(
        [f"La mediana pasó de {usd(f_a3['salario_usd_mediano'])} en {int(f_a3['work_year'])} a "
         f"{usd(u_a3['salario_usd_mediano'])} en {int(u_a3['work_year'])}.",
         f"El mayor aumento interanual fue en {int(mx['work_year'])}: "
         f"{usd(mx['variacion_mediana_usd_vs_anio_anterior'])} "
         f"({pct(mx['variacion_mediana_porcentual_vs_anio_anterior'])}).",
         f"Los registros pasaron de {num(f_a3['cantidad_registros'])} a {num(u_a3['cantidad_registros'])} y la "
         f"proporción de registros Senior de {pct(p_sen.iloc[0])} a {pct(p_sen.iloc[-1])}."] + dentro,
        "Resume cómo varió la mediana observada entre años. La composición de cada año debe considerarse al "
        "interpretar esa variación; estos datos no permiten proyectar salarios.",
        "Los registros crecen mucho y la mezcla de experiencia cambia entre años, por lo que parte del aumento de "
        "la mediana puede deberse a quién aparece en la muestra y no a un cambio de los salarios. No hay datos de "
        "inflación ni de otros factores, así que no se puede atribuir una causa.")
    with st.expander("Ver la tabla de datos de este gráfico"):
        st.dataframe(a3.round(1), width="stretch", hide_index=True)

# --------------------------------------------------------------------------- #
# Conclusiones
# --------------------------------------------------------------------------- #
with tab_fin:
    encabezado("Cierre", "Hallazgos y alcance del análisis")
    texto_cargo = (f"{esc(c1['job_title'])} y {esc(c2['job_title'])} son los cargos con más registros"
                   + ("; el de más registros no es el de mayor salario mediano entre los diez más frecuentes."
                      if c1["salario_usd_mediana"] < top10["salario_usd_mediana"].max() else "."))
    html('<div class="sub-title">Síntesis de resultados</div>')
    html('<div class="duo">'
         f'<div class="card"><h4>Comparación salarial</h4><p>La mediana sube con la experiencia, de '
         f'{usd(med_exp["Inicial"])} (Inicial) a {usd(med_exp["Ejecutivo"])} (Ejecutivo). La modalidad '
         f'{bajo_mod.lower()} (n = {num(n_mod[bajo_mod])}) y las empresas {bajo_tam.lower()}s '
         f'(n = {num(n_tam[bajo_tam])}) tienen las medianas más bajas, pero son grupos pequeños con otra mezcla '
         'de experiencia y países, por lo que no se atribuye la diferencia a la modalidad ni al tamaño.</p></div>'
         f'<div class="card"><h4>Composición de la muestra</h4><p>{num(len(d))} registros, concentrados en '
         f'{anios[-2]} y {anios[-1]}, con predominio del tiempo completo ({pct(ft["participacion"])}) y de los '
         'niveles Senior.</p></div>'
         f'<div class="card"><h4>Cargos frecuentes</h4><p>{texto_cargo}</p></div>'
         f'<div class="card"><h4>Tendencia anual</h4><p>La mediana pasó de {usd(f_a3["salario_usd_mediano"])} a '
         f'{usd(u_a3["salario_usd_mediano"])}, pero la muestra y su mezcla de experiencia cambiaron mucho entre '
         'años.</p></div></div>')
    html('<div class="duo">'
         '<div class="card verde"><h4>Criterios de interpretación</h4>' + ul([
             "Leer las <b>medianas y los rangos (Q1–Q3)</b> junto con el número de registros.",
             "Considerar el <b>nivel de experiencia</b> y la composición de cada grupo al comparar salarios.",
             "Tener en cuenta el <b>año de referencia</b> al interpretar las diferencias observadas.",
             "Complementar el análisis con otras fuentes antes de generalizar estos resultados."])
         + '</div><div class="card lim"><h4>Limitaciones</h4>' + ul([
             "Los datos son salarios reportados, <b>no ingresos ni rentabilidad</b>; no miden productividad.",
             "No se demuestran causas: las diferencias describen este dataset y no necesariamente el mercado.",
             "No hay identificador de persona ni de empresa ni fecha exacta; la periodicidad del salario no está "
             "especificada.",
             "Hay <b>1.171 filas exactamente repetidas (31,2 %)</b>; se conservaron porque no se puede probar que "
             "sean errores.",
             "Para contextualizar los resultados harían falta variables como país y costo de vida, sector, "
             "antigüedad en el cargo, beneficios y desempeño."]) + '</div></div>')
    html('<div class="sub-title">Antes y después de la preparación, y sensibilidad a las filas repetidas</div>')
    comp = res["comparacion"].rename(columns={
        "version": "Versión", "filas": "Filas", "columnas": "Columnas",
        "duplicados_exactos": "Filas repetidas", "porcentaje_duplicados_exactos": "% repetidas",
        "valores_nulos": "Nulos", "salario_usd_promedio": "Promedio (USD)",
        "salario_usd_mediana": "Mediana (USD)"})
    st.dataframe(comp, width="stretch", hide_index=True)
    st.caption("Tabla `comparacion_antes_despues.csv`, generada por el notebook de la AE3. Activa el filtro de la "
               "barra lateral para ver todas las gráficas sin las filas repetidas.")
    html('<div class="pie">Proyecto integrador · Analítica de datos · Datos: Einstellung/demo-salaries '
         '(Hugging Face). Resultados descriptivos: no demuestran causas ni representan rentabilidad.</div>')
