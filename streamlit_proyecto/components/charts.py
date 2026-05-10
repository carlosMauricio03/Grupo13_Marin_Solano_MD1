import streamlit as st
import plotly.express as px


def render_trend_chart(daily_avg):
    st.subheader("📈 Tendencia de Tasas Promedio")

    if daily_avg.empty:
        st.info("Sin datos de tendencia.")
        return

    fig = px.line(
        daily_avg,
        x="day",
        y="avg_rate",
        color="target_currency",
        title="Evolución de tasa promedio diaria"
    )

    st.plotly_chart(fig, use_container_width=True)


def render_volatility_chart(volatility):
    st.subheader("📉 Volatilidad por Par")

    if volatility.empty:
        st.info("Sin datos de volatilidad.")
        return

    fig = px.bar(
        volatility,
        x="day",
        y="stddev_rate",
        color="target_currency",
        title="Volatilidad diaria (desviación estándar)",
        barmode="group"
    )

    st.plotly_chart(fig, use_container_width=True)
