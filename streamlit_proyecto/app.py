import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import settings
import streamlit as st
import pandas as pd
import altair as alt
from config.database import get_connection

st.set_page_config(
    page_title="Proyecto - Analisis de Datos",
    page_icon=None,
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background-color: #FFFFFF;
    }
    .main-title {
        font-size: 36px;
        font-weight: 700;
        color: #0E2F44;
        margin-bottom: 15px;
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
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">Proyecto - Analisis de Datos</p>', unsafe_allow_html=True)
st.markdown("Analisis estadistico, modelos de prediccion y pruebas de hipotesis")
st.markdown("---")


@st.cache_data(ttl=300)
def load_summary_data():
    conn = get_connection()

    daily_avg = pd.read_sql("""
        SELECT * FROM exchange_rate_daily_avg 
        ORDER BY day DESC LIMIT 100
    """, conn)

    volatility = pd.read_sql("""
        SELECT * FROM exchange_rate_volatility 
        ORDER BY day DESC LIMIT 100
    """, conn)

    pct_change = pd.read_sql("""
        SELECT * FROM exchange_rate_pct_change 
        ORDER BY pct_change DESC NULLS LAST
    """, conn)

    spread = pd.read_sql("""
        SELECT * FROM exchange_rate_spread
        ORDER BY day DESC LIMIT 100
    """, conn)

    conn.close()
    return daily_avg, volatility, pct_change, spread


daily_avg, volatility, pct_change, spread = load_summary_data()

if daily_avg.empty:
    st.warning("No hay datos resumidos. Ejecuta primero: python -m etl_proyecto.run")
    st.stop()

st.markdown('<p class="section-header">Indicadores de Rendimiento</p>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_pairs = daily_avg["target_currency"].nunique()
    st.metric("Pares de Monedas", f"{total_pairs}")

with col2:
    avg_rate = daily_avg["avg_rate"].mean()
    st.metric("Tasa Promedio", f"{avg_rate:.4f}" if pd.notna(avg_rate) else "N/A")

with col3:
    avg_vol = volatility["stddev_rate"].mean()
    st.metric("Volatilidad Promedio", f"{avg_vol:.6f}" if pd.notna(avg_vol) else "N/A")

with col4:
    top_change = pct_change["pct_change"].max()
    st.metric("Maxima Variacion %", f"{top_change:.2f}%" if pd.notna(top_change) else "N/A")

st.markdown("---")

st.markdown('<p class="section-header">Analisis de Tendencias</p>', unsafe_allow_html=True)

if not daily_avg.empty:
    currencies = daily_avg["target_currency"].unique().tolist()[:10]
    selected_currencies = st.multiselect(
        "Seleccionar monedas",
        currencies,
        default=currencies[:5]
    )

    if selected_currencies:
        df_chart = daily_avg[daily_avg["target_currency"].isin(selected_currencies)]

        chart = alt.Chart(df_chart).mark_line(point=True).encode(
            x=alt.X('day', title='Fecha'),
            y=alt.Y('avg_rate', title='Tasa Promedio'),
            color=alt.Color('target_currency', legend=alt.Legend(title="Moneda")),
            tooltip=['day', 'target_currency', 'avg_rate']
        ).properties(
            height=400
        ).interactive()

        st.altair_chart(chart, use_container_width=False)

st.markdown("---")

st.markdown('<p class="section-header">Analisis de Volatilidad</p>', unsafe_allow_html=True)

if not volatility.empty:
    vol_chart = alt.Chart(volatility.head(50)).mark_bar().encode(
        x=alt.X('day', title='Fecha'),
        y=alt.Y('stddev_rate', title='Desviacion Estandar'),
        color=alt.Color('target_currency'),
        tooltip=['day', 'target_currency', 'stddev_rate']
    ).properties(
        height=350
    )

    st.altair_chart(vol_chart, use_container_width=False)

st.markdown("---")

st.markdown('<p class="section-header">Variacion Porcentual</p>', unsafe_allow_html=True)

if not pct_change.empty:
    df_pct = pct_change.sort_values('pct_change', ascending=False).head(20)

    chart_pct = alt.Chart(df_pct).mark_bar().encode(
        y=alt.Y('target_currency', sort='-x', title='Moneda'),
        x=alt.X('pct_change', title='Variacion (%)'),
        color=alt.Color('pct_change', scale=alt.Scale(domain=[df_pct['pct_change'].min(), df_pct['pct_change'].max()], scheme='redblue')),
        tooltip=['target_currency', 'current_rate', 'previous_rate', 'pct_change']
    ).properties(
        height=350
    )

    st.altair_chart(chart_pct, use_container_width=False)

st.markdown("---")

st.markdown('<p class="section-header">Resumen de Pruebas Estadisticas</p>', unsafe_allow_html=True)

st.info("""
**Nota:** Para ver el analisis completo de pruebas estadisticas (normalidad, heteroscedasticidad, multicolinealidad) 
y modelos de prediccion, ejecute el notebook en Jupyter:

```bash
docker compose -f docker/docker-compose.yml up jupyter
```

Luego abra: http://localhost:8888 y seleccione el notebook `exchange_analysis.ipynb`

El notebook incluye:
- Pruebas de normalidad (Shapiro-Wilk, Jarque-Bera, D'Agostino, Kolmogorov-Smirnov)
- Pruebas de heteroscedasticidad (Breusch-Pagan, White)
- Analisis de multicolinealidad (VIF)
- Modelos OLS y ARIMA
- Predicciones y clustering
""")

st.markdown("---")

st.markdown('<p class="section-header">Datos Detallados - Tasas Diarias</p>', unsafe_allow_html=True)

if not daily_avg.empty:
    st.dataframe(
        daily_avg.sort_values('day', ascending=False).head(50),
        use_container_width=True,
        height=300,
        hide_index=True
    )