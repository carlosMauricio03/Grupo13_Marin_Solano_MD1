import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from etl.db_connection import get_connection

st.set_page_config(
    page_title="Dashboard Exchange Rates",
    page_icon="💱",
    layout="wide"
)

st.title("💱 Dashboard de Tipo de Cambio")
st.markdown("---")

# ==============================
# CONEXIÓN
# ==============================

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

if df.empty:
    st.warning("No hay datos en la base de datos.")
    st.stop()

df["timestamp"] = pd.to_datetime(df["timestamp"])

# ==============================
# SIDEBAR FILTROS
# ==============================

st.sidebar.header("🔎 Filtros")

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

# ==============================
# KPIs
# ==============================

st.subheader("📊 Indicadores")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Registros", len(df_filtered))

with col2:
    latest_timestamp = df_filtered["timestamp"].max()
    st.metric("Última Actualización", latest_timestamp.strftime("%Y-%m-%d %H:%M"))

with col3:
    avg_rate = df_filtered["rate"].mean()
    st.metric("Promedio Rate", f"{avg_rate:.4f}")

st.markdown("---")

# ==============================
# GRÁFICA 1 — Último Rate por Moneda
# ==============================

st.subheader("📈 Última Tasa por Moneda")

latest_rates = (
    df_filtered
    .sort_values("timestamp")
    .groupby("target_currency")
    .tail(1)
)

fig_bar = px.bar(
    latest_rates,
    x="target_currency",
    y="rate",
    color="rate",
    title="Última tasa registrada",
)

st.plotly_chart(fig_bar, use_container_width=True)

# ==============================
# GRÁFICA 2 — Evolución histórica
# ==============================

st.subheader("📉 Evolución Histórica")

fig_line = px.line(
    df_filtered,
    x="timestamp",
    y="rate",
    color="target_currency",
    markers=True,
    title="Evolución del tipo de cambio"
)

st.plotly_chart(fig_line, use_container_width=True)

# ==============================
# TABLA
# ==============================

st.subheader("📋 Datos Detallados")

st.dataframe(
    df_filtered.sort_values("timestamp", ascending=False),
    use_container_width=True,
    )