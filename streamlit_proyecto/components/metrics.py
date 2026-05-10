import streamlit as st


def render_kpis(daily_avg, volatility, pct_change):
    st.subheader("📊 Indicadores Clave")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_pairs = daily_avg["target_currency"].nunique() if not daily_avg.empty else 0
        st.metric("Pares de Monedas", total_pairs)

    with col2:
        avg_rate = daily_avg["avg_rate"].mean() if not daily_avg.empty else 0
        st.metric("Tasa Promedio Global", f"{avg_rate:.4f}")

    with col3:
        avg_volatility = volatility["stddev_rate"].mean() if not volatility.empty else 0
        st.metric("Volatilidad Promedio", f"{avg_volatility:.6f}")

    with col4:
        top_change = pct_change["pct_change"].max() if not pct_change.empty else 0
        st.metric("Máxima Variación %", f"{top_change:.2f}%")
