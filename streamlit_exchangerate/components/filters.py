import streamlit as st


def render_sidebar_filters(df):
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

    return base_filter, target_filter
