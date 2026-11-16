import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="CryptoPulse Analytics", page_icon="📈", layout="wide")

st.title("📈 CryptoPulse Analytics: Panel de Control del Mercado DeFi")
st.markdown("Aplicació interactiva desenvolupada per a l'anàlisi del mercat de criptomonedes i actius digitals.")

@st.cache_data
def load_data():
    df = pd.read_csv("crypto_historical_prices.csv", index_col=0, parse_dates=True)
    return df

def load_vol():
    df = pd.read_csv("crypto_historical_volume.csv", index_col=0, parse_dates=True)
    return df

df = load_data()
df_vol = load_vol()

st.sidebar.header("🔍 Filtres i Selecció de Variables")

# Variable 1: Selecció d'actius (Criptomonedes)
available_tickers = list(df.columns)
selected_tickers = st.sidebar.multiselect(
    "1. Selecciona les criptomonedes:", 
    options=available_tickers, 
    default=available_tickers[:3] if len(available_tickers) >= 3 else available_tickers
)

# Variable 2: Rang de dates
min_date = df.index.min().date()
max_date = df.index.max().date()
start_date, end_date = st.sidebar.date_input(
    "2. Selecciona el rang de dates:", 
    value=[min_date, max_date], 
    min_value=min_date, 
    max_value=max_date
)

# Variable 3: Tipus de visualització o escala de preus
price_scale = st.sidebar.selectbox(
    "3. Selecciona l'escala de visualització:", 
    options=["Preu absolut (USD)", "Normalitzat (Base 100)"]
)

# Variable 4: Llindar de preu mínim (Slider)
min_price_slider = st.sidebar.slider(
    "4. Filtre de preu mínim de tancament (USD):", 
    min_value=0.0, 
    max_value=float(df.max().max()), 
    value=0.0
)

# aplica filtro de fechas
mask = (df.index >= pd.to_datetime(start_date)) & (df.index <= pd.to_datetime(end_date))
df_filtered = df.loc[mask, selected_tickers]

mask = (df_vol.index >= pd.to_datetime(start_date)) & (df_vol.index <= pd.to_datetime(end_date))
df_vol_filtered = df_vol.loc[mask, selected_tickers]


if selected_tickers:
    df_filtered = df_filtered.loc[:, (df_filtered >= min_price_slider).any()]


# aplica filtro de criptomonedas
if df_filtered.empty or not selected_tickers:
    st.warning("⚠️ Si us plau, selecciona almenys una criptomoneda i ajusta els filtres per mostrar dades.")
    st.stop()


# genera resumen estadistico
st.subheader("📊 Resum Estadístic de les Dades Seleccionades")
col1, col2, col3 = st.columns(3)

with col1:
    latest_price = df_filtered.iloc[-1].mean()
    st.metric(label="Mitjana de Preus Actuals", value=f"${latest_price:,.2f}")

with col2:
    max_val = df_filtered.max().max()
    st.metric(label="Preu Màxim del Període", value=f"${max_val:,.2f}")

with col3:
    total_records = len(df_filtered)
    st.metric(label="Registres Analitzats (Dies)", value=total_records)

st.markdown("---")

col_g1, col_g2 = st.columns(2)


# genera gráficos
with col_g1:
    st.markdown("### 📉 1. Gràfic de Línies: Evolució Temporal")
    st.markdown("Evolució històrica dels preus de tancament per als actius seleccionats.")
    
    # Gràfic de línies
    if price_scale == "Normalitzat (Base 100)":
        df_plot = (df_filtered / df_filtered.iloc[0]) * 100
        st.line_chart(df_plot)
    else:
        st.line_chart(df_filtered)

with col_g2:
    st.markdown("### 📊 2. Gràfic de Barres (Agrupació)")
    st.markdown("Mitjana de volum agrupada per actiu durant el període seleccionat.")
    
    mean_prices = df_vol_filtered.mean()
    st.bar_chart(mean_prices, color="#ff4b4b")


col_g3, col_g4 = st.columns(2)


# genera gráficos
with col_g3:
    # Gràfic de Pastel
    st.markdown("### 🥧 3. Gràfic de Pastís: Distribució del Volum Total")
    fig, ax = plt.subplots(figsize=(8, 4))
    mean_prices.plot(kind='pie', autopct='%1.1f%%', ax=ax, startangle=90, cmap='Set3')
    ax.set_ylabel('')
    ax.set_title("Distribució percentual de la capitalització/volum mitjà", fontsize=12)
    st.pyplot(fig)

# st.markdown("---")

with col_g4:
    st.markdown("### 🔬 4. Gràfic Estadístic: Matriu de Correlació (Heatmap)")
    st.markdown("Anàlisi de la relació estadística i correlació de preus entre les criptomonedes seleccionades.")

    fig_heat, ax_heat = plt.subplots(figsize=(10, 5))
    correlation_matrix = df_filtered.corr()
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=.5, ax=ax_heat)
    ax_heat.set_title("Mapa de calor de correlació entre actius", fontsize=14)
    st.pyplot(fig_heat)