import streamlit as st
import pandas as pd
import plotly.express as px
from config.database import get_connection


@st.cache_data(ttl=300)
def load_ml_predictions():
    conn = get_connection()

    try:
        df = pd.read_sql("""
            SELECT * FROM exchange_rate_predictions 
            ORDER BY prediction_date DESC
        """, conn)
    except Exception:
        df = pd.DataFrame()

    conn.close()
    return df


@st.cache_data(ttl=300)
def load_clusters():
    conn = get_connection()

    try:
        df = pd.read_sql("""
            SELECT * FROM exchange_rate_clusters
        """, conn)
    except Exception:
        df = pd.DataFrame()

    conn.close()
    return df


def render_ml_section():
    st.subheader("🧠 Resultados de Machine Learning")

    predictions = load_ml_predictions()
    clusters = load_clusters()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Predicciones de tasas**")

        if not predictions.empty:
            fig = px.line(
                predictions,
                x="prediction_date",
                y="predicted_rate",
                color="target_currency",
                title="Predicciones del modelo"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay predicciones disponibles. Entrena un modelo y guarda resultados en `exchange_rate_predictions`.")

    with col2:
        st.markdown("**Clustering de monedas**")

        if not clusters.empty:
            fig = px.scatter(
                clusters,
                x="feature_1",
                y="feature_2",
                color="cluster",
                title="Agrupamiento de monedas"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay clusters disponibles. Ejecuta el notebook de clustering y guarda en `exchange_rate_clusters`.")
