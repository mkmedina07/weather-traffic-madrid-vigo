import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.weather import obtener_clima
from utils.traffic import obtener_trafico
from utils.database import (
    crear_base_de_datos,
    obtener_climas_recientes,
    obtener_climas_por_rango,
    obtener_traficos_recientes,
    obtener_traficos_por_rango,
    guardar_registros,
)
from utils.ml_utils import (
    aggregate_by_year_and_month,
    train_congestion_model,
    predict_congestion,
)
from pathlib import Path
from scripts.predict_remaining_2026 import predict_remaining_2026

st.set_page_config(
    page_title="Clima y Tráfico",
    layout="wide"
)

st.title("🌦️ Clima y 🚗 Tráfico")

crear_base_de_datos()

ciudades = ["Madrid", "Vigo"]

st.session_state.setdefault("datos_guardados", False)

with st.sidebar:
    st.header("Controles")
    if st.button("Actualizar y guardar datos"):
        registros = []
        for ciudad in ciudades:
            clima = obtener_clima(ciudad)
            trafico = obtener_trafico(ciudad)
            registros.append({"clima": clima, "trafico": trafico})
        guardar_registros(registros)
        st.session_state.datos_guardados = True
        st.success("Datos actuales guardados en la base de datos.")

    st.write("Usa este botón para refrescar los datos y guardarlos en la base de datos SQLite local.")

if st.session_state.datos_guardados:
    st.info("Los datos se han guardado recientemente.")

col1, col2 = st.columns(2)

for idx, ciudad in enumerate(ciudades):
    clima = obtener_clima(ciudad)
    trafico = obtener_trafico(ciudad)
    container = col1 if idx == 0 else col2
    with container:
        st.subheader(ciudad)
        if clima.get("error"):
            st.error(clima["error"])
            continue
        st.metric("Temperatura", f"{clima['temperatura']} °C")
        st.markdown(f"**Condición:** {clima['descripcion'].capitalize()}")
        st.markdown(f"**Humedad:** {clima['humedad']} %")
        st.markdown(f"**Viento:** {clima['viento']} m/s")
        st.markdown(f"**Precipitación:** {clima.get('precipitation', 0)} mm")
        st.markdown(f"**Tráfico:** {trafico['nivel']} ({trafico['congestion']} %)")
        st.info(trafico["mensaje"])

st.markdown("---")

st.header("Histórico de datos")

climas = obtener_climas_recientes(limit=10)
traficos = obtener_traficos_recientes(limit=10)

if climas:
    st.subheader("Últimos registros de clima")
    st.dataframe(pd.DataFrame(climas).rename(columns={
        "created_at": "Fecha",
        "ciudad": "Ciudad",
        "temperatura": "Temp (°C)",
        "descripcion": "Condición",
        "humedad": "Humedad",
        "viento": "Viento (m/s)",
        "precipitation": "Precipitación (mm)"
    }))
else:
    st.write("No hay registros de clima guardados todavía.")

if traficos:
    st.subheader("Últimos registros de tráfico")
    st.dataframe(pd.DataFrame(traficos).rename(columns={
        "created_at": "Fecha",
        "ciudad": "Ciudad",
        "nivel": "Nivel",
        "congestion": "Congestión (%)"
    }))
else:
    st.write("No hay registros de tráfico guardados todavía.")

st.markdown("---")

st.header("Relación clima-tráfico")

def cargar_relacion_clima_trafico(years: int = 2):
    end = datetime.utcnow()
    start = end - timedelta(days=365 * years)
    climas = pd.DataFrame(obtener_climas_por_rango(start.isoformat(), end.isoformat()))
    traficos = pd.DataFrame(obtener_traficos_por_rango(start.isoformat(), end.isoformat()))
    if climas.empty or traficos.empty:
        return None
    climas["created_at"] = pd.to_datetime(climas["created_at"], errors="coerce").dt.round("s")
    traficos["created_at"] = pd.to_datetime(traficos["created_at"], errors="coerce").dt.round("s")
    climas = climas.dropna(subset=["created_at"])
    traficos = traficos.dropna(subset=["created_at"])
    return pd.merge(climas, traficos, on=["ciudad", "created_at"], how="inner")

relacion_df = cargar_relacion_clima_trafico(2)
if relacion_df is None or relacion_df.empty:
    st.write("No hay datos históricos suficientes para mostrar la relación clima-tráfico.")
else:
    relacion_df["precipitation"] = relacion_df["precipitation"].fillna(0)
    metrics = relacion_df[["congestion", "temperatura", "humedad", "viento", "precipitation"]].apply(pd.to_numeric, errors="coerce")
    corr = metrics.corr()["congestion"].drop(labels=["congestion"]).round(3)

    st.subheader("Correlación con congestión")
    corr_display = corr.reset_index()
    corr_display.columns = ["Variable", "Correlación"]
    st.dataframe(corr_display)

    st.subheader("Congestión media por condición meteorológica")
    promedio_desc = relacion_df.groupby("descripcion")["congestion"].mean().round(2).sort_values(ascending=False)
    st.bar_chart(promedio_desc)

    yearly, monthly = aggregate_by_year_and_month(relacion_df)
    
    # Format yearly statistics
    yearly_display = yearly.copy()
    yearly_display["avg_temp"] = yearly_display["avg_temp"].round(2)
    yearly_display["avg_precip"] = yearly_display["avg_precip"].round(4)
    yearly_display["avg_wind"] = yearly_display["avg_wind"].round(2)
    yearly_display["avg_humidity"] = yearly_display["avg_humidity"].round(2)
    yearly_display["avg_congestion"] = yearly_display["avg_congestion"].round(2)
    
    st.subheader("Estadísticas por año")
    st.dataframe(yearly_display.rename(columns={
        "ciudad": "Ciudad",
        "year": "Año",
        "avg_temp": "Temp media (°C)",
        "avg_precip": "Precip media (mm)",
        "avg_wind": "Viento medio (m/s)",
        "avg_humidity": "Humedad media (%)",
        "avg_congestion": "Congestión media"
    }))

    # Format monthly statistics
    monthly_display = monthly.copy()
    monthly_display["avg_temp"] = monthly_display["avg_temp"].round(2)
    monthly_display["avg_precip"] = monthly_display["avg_precip"].round(4)
    monthly_display["avg_wind"] = monthly_display["avg_wind"].round(2)
    monthly_display["avg_humidity"] = monthly_display["avg_humidity"].round(2)
    monthly_display["avg_congestion"] = monthly_display["avg_congestion"].round(2)
    
    st.subheader("Estadísticas por mes (agregado)")
    st.dataframe(monthly_display.rename(columns={
        "ciudad": "Ciudad",
        "month": "Mes",
        "avg_temp": "Temp media (°C)",
        "avg_precip": "Precip media (mm)",
        "avg_wind": "Viento medio (m/s)",
        "avg_humidity": "Humedad media (%)",
        "avg_congestion": "Congestión media"
    }))

    st.subheader("Resumen rápido")
    st.markdown(
        f"- Viento tiene correlación positiva con congestión: **{corr.loc['viento']}**.\n"
        f"- Temperatura muestra un efecto pequeño: **{corr.loc['temperatura']}**.\n"
        f"- Humedad tiene correlación negativa débil: **{corr.loc['humedad']}**.\n"
        f"- Precipitación también está relacionada con congestión: **{corr.loc['precipitation']}**."
    )

    st.subheader("Modelo de predicción de congestión")
    model, model_metrics, feature_importances = train_congestion_model(relacion_df)
    if model is None:
        st.write("No hay datos suficientes para entrenar el modelo.")
    else:
        st.markdown("**Métricas del modelo**")
        st.write(model_metrics)
        st.markdown("**Importancias de variables**")
        st.write(feature_importances)

        st.markdown("**Predicción de congestión con clima de entrada**")
        col_a, col_b = st.columns(2)
        with col_a:
            temp_input = st.number_input("Temperatura (°C)", value=20.0, format="%.1f")
            humidity_input = st.number_input("Humedad (%)", value=50.0, format="%.1f")
        with col_b:
            wind_input = st.number_input("Viento (m/s)", value=3.0, format="%.1f")
            precip_input = st.number_input("Precipitación (mm)", value=0.0, format="%.1f")

        if st.button("Predecir congestión"):
            prediction = predict_congestion(model, temp_input, humidity_input, wind_input, precip_input)
            st.success(f"Predicción de congestión: {prediction:.1f} %")

    with st.expander("Ver muestra de datos históricos"):
        st.dataframe(relacion_df[["created_at", "ciudad", "descripcion", "temperatura", "humedad", "viento", "precipitation", "congestion"]].tail(20))

    st.markdown("---")
    st.header("Predicciones para el resto de 2026")
    pred_path = Path("db/predictions_2026_remaining.csv")
    if st.button("Generar predicciones 2026 restantes"):
        try:
            df_preds = predict_remaining_2026(pred_path)
            st.success(f"Predicciones generadas y guardadas en {pred_path}")
            st.dataframe(df_preds)
            # interactive plotly chart
            try:
                df_plot = df_preds.copy()
                df_plot['month'] = df_plot['month'].astype(int)
                import plotly.express as px
                fig = px.bar(
                    df_plot,
                    x='month',
                    y='pred_congestion',
                    color='ciudad',
                    barmode='group',
                    labels={'pred_congestion': 'Predicción congestión (%)', 'month': 'Mes', 'ciudad': 'Ciudad'},
                    title='Predicción de congestión (meses restantes 2026)'
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception:
                pass

            # download button
            try:
                csv_bytes = pred_path.read_bytes()
                st.download_button("Descargar CSV", data=csv_bytes, file_name=pred_path.name, mime="text/csv")
            except Exception:
                pass

            # show static chart if exists
            fig_path = pred_path.with_suffix('.png')
            if fig_path.exists():
                st.image(str(fig_path), caption="Predicción congestión (meses restantes 2026)", use_column_width=True)
        except Exception as e:
            st.error(f"Error generando predicciones: {e}")
    else:
        if pred_path.exists():
            st.subheader("Predicciones guardadas")
            df_saved = pd.read_csv(pred_path)
            st.dataframe(df_saved)
            # interactive plot
            try:
                df_plot = df_saved.copy()
                df_plot['month'] = df_plot['month'].astype(int)
                import plotly.express as px
                fig = px.bar(
                    df_plot,
                    x='month',
                    y='pred_congestion',
                    color='ciudad',
                    barmode='group',
                    labels={'pred_congestion': 'Predicción congestión (%)', 'month': 'Mes', 'ciudad': 'Ciudad'},
                    title='Predicción de congestión (meses restantes 2026)'
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception:
                pass

            try:
                csv_bytes = pred_path.read_bytes()
                st.download_button("Descargar CSV", data=csv_bytes, file_name=pred_path.name, mime="text/csv")
            except Exception:
                pass
            fig_path = pred_path.with_suffix('.png')
            if fig_path.exists():
                st.image(str(fig_path), caption="Predicción congestión (meses restantes 2026)", use_column_width=True)
        else:
            st.info("No hay predicciones guardadas. Pulsa 'Generar predicciones 2026 restantes' para crearlas.")
