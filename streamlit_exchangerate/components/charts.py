import streamlit as st
import plotly.express as px


def render_bar_chart(data):
    latest_rates = (
        data
        .sort_values("timestamp")
        .groupby("target_currency")
        .tail(1)
    )

    fig = px.bar(
        latest_rates,
        x="target_currency",
        y="rate",
        color="rate",
        title="Última tasa registrada",
    )

    st.plotly_chart(fig, use_container_width=True)


def render_line_chart(data):
    fig = px.line(
        data,
        x="timestamp",
        y="rate",
        color="target_currency",
        markers=True,
        title="Evolución del tipo de cambio"
    )

    st.plotly_chart(fig, use_container_width=True)
