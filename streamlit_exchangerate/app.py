import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import settings
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from config.database import get_connection

st.set_page_config(
    page_title="Exchange Rate Dashboard",
    page_icon=None,
    layout="wide"
)

st.markdown("""
<style>
    /* Forzar tema claro */
    .stApp {
        background-color: #FFFFFF;
    }
    /* Estilos generales */
    .main-title {
        font-size: 36px;
        font-weight: 700;
        color: #0E2F44;
        margin-bottom: 15px;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    .section-header {
        font-size: 22px;
        font-weight: 600;
        color: #0E2F44;
        border-bottom: 3px solid #0077B6;
        padding-bottom: 10px;
        margin-bottom: 25px;
        margin-top: 30px;
    }
    .sidebar-header {
        font-size: 18px;
        font-weight: 600;
        color: #023E8A;
        margin-bottom: 15px;
    }
    /* Metricas */
    div[data-testid="stMetric"] {
        background-color: #F0F8FF;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #0077B6;
    }
    div[data-testid="stMetricLabel"] {
        color: #555555;
        font-size: 14px;
        font-weight: 500;
    }
    div[data-testid="stMetricValue"] {
        color: #023E8A;
        font-size: 28px;
        font-weight: 700;
    }
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #F8F9FA;
    }
    /* Estilos de texto general */
    p, div, span {
        color: #333333 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">Exchange Rate Dashboard</p>', unsafe_allow_html=True)
st.markdown("---")


@st.cache_data(ttl=300)
def load_data():
    conn = get_connection()

    query = """
    SELECT 
        er.id,
        c1.code AS base_currency,
        c2.code AS target_currency,
        er.rate,
        er.timestamp
    FROM exchange_rates er
    JOIN currencies c1 ON er.base_currency_id = c1.id
    JOIN currencies c2 ON er.target_currency_id = c2.id
    ORDER BY er.timestamp DESC;
    """

    df = pd.read_sql(query, conn)
    conn.close()

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


df = load_data()

if df.empty:
    st.warning("No hay datos en la base de datos.")
    st.stop()

st.markdown('<p class="sidebar-header">Filtros</p>', unsafe_allow_html=True)

base_filter = st.sidebar.selectbox(
    "Moneda Base",
    options=df["base_currency"].unique()
)

target_filter = st.sidebar.multiselect(
    "Moneda Destino",
    options=df["target_currency"].unique(),
    default=df["target_currency"].unique()[:5]
)

df_filtered = df[
    (df["base_currency"] == base_filter) &
    (df["target_currency"].isin(target_filter))
]

st.markdown('<p class="section-header">Indicadores Clave</p>', unsafe_allow_html=True)

if df_filtered.empty:
    st.warning("No hay datos con los filtros seleccionados.")
else:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Registros", f"{len(df_filtered):,}")

    with col2:
        latest_timestamp = df_filtered["timestamp"].max()
        if pd.notna(latest_timestamp):
            st.metric("Ultima Actualizacion", latest_timestamp.strftime("%Y-%m-%d %H:%M"))
        else:
            st.metric("Ultima Actualizacion", "N/A")

    with col3:
        avg_rate = df_filtered["rate"].mean()
        if pd.notna(avg_rate):
            st.metric("Tasa Promedio", f"{avg_rate:.4f}")
        else:
            st.metric("Tasa Promedio", "N/A")

st.markdown("---")

if not df_filtered.empty:
    st.markdown('<p class="section-header">Tasas por Moneda</p>', unsafe_allow_html=True)

    latest_rates = (
        df_filtered
        .sort_values("timestamp")
        .groupby("target_currency")
        .tail(1)
        .reset_index()
    )

    if not latest_rates.empty:
        chart_bar = alt.Chart(latest_rates).mark_bar(
            cornerRadiusTopLeft=4,
            cornerRadiusTopRight=4
        ).encode(
            x=alt.X('target_currency', title='Moneda Destino', sort='-y'),
            y=alt.Y('rate', title='Tasa de Cambio'),
            color=alt.Color('rate', scale=alt.Scale(scheme='blues'), legend=None),
            tooltip=['target_currency', 'rate']
        ).properties(
            height=400,
            width=alt.Step(40)
        ).configure_view(
            stroke=None
        )
        st.altair_chart(chart_bar, use_container_width=False)
    else:
        st.info("No hay datos suficientes para mostrar el grafico.")

    st.markdown('<p class="section-header">Evolucion Historica</p>', unsafe_allow_html=True)

    chart_line = alt.Chart(df_filtered).mark_line(
        point=True
    ).encode(
        x=alt.X('timestamp', title='Fecha'),
        y=alt.Y('rate', title='Tasa de Cambio'),
        color=alt.Color('target_currency', legend=alt.Legend(title="Moneda")),
        tooltip=['timestamp', 'target_currency', 'rate']
    ).properties(
        height=400
    ).configure_view(
        stroke=None
    ).interactive()
    st.altair_chart(chart_line, use_container_width=False)
else:
    st.info("Selecciona al menos una moneda destino para ver los graficos.")

st.markdown('<p class="section-header">Datos Detallados</p>', unsafe_allow_html=True)

df_table = df_filtered.sort_values("timestamp", ascending=False)

if df_table.empty:
    st.info("No hay datos para mostrar.")
else:
    st.dataframe(
        df_table,
        use_container_width=True,
        height=350,
        hide_index=True
    )