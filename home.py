import pandas as pd
import numpy as np
import plotly.express as px
import inflection
import streamlit as st
import folium
from streamlit_folium import st_folium

# =========================
# Módulo: Carregamento e Tratamento de Dados
# =========================

def carregar_dados(caminho_arquivo):
    return pd.read_csv(caminho_arquivo)

def mapear_rating_text(df):
    mapeamento_rating = {
        'Excellent': 'Excellent',
        'Very Good': 'Very Good',
        'Good': 'Good',
        'Average': 'Average',
        'Not rated': 'Not rated',
        'Poor': 'Poor',
        'Excelente': 'Excellent',
        'Muito bom': 'Very Good',
        'Muito Bom': 'Very Good',
        'Bardzo dobrze': 'Very Good',
        'Muy Bueno': 'Very Good',
        'Bueno': 'Good',
        'Baik': 'Good',
        'Biasa': 'Average',
        'Skvělá volba': 'Excellent',
        'Velmi dobré': 'Very Good',
        'Harika': 'Excellent',
        'Çok iyi': 'Very Good',
        'Eccellente': 'Excellent',
        'Veľmi dobré': 'Very Good',
        'Buono': 'Good',
        'Bom': 'Good',
        'Skvělé': 'Excellent',
        'Wybitnie': 'Excellent',
        'Sangat Baik': 'Very Good',
        'Terbaik': 'Excellent',
        'İyi': 'Good',
        'Vynikajúce': 'Excellent'
    }
    df['Rating text'] = df['Rating text'].replace(mapeamento_rating)
    return df

def mapear_country_code(df):
    country_code_to_name = {
        1: 'India',
        14: 'Australia',
        30: 'Brazil',
        37: 'Canada',
        94: 'Indonesia',
        148: 'New Zealand',
        162: 'Philippines',
        166: 'Qatar',
        184: 'Singapore',
        189: 'South Africa',
        191: 'Sri Lanka',
        208: 'Turkey',
        214: 'UAE',
        215: 'England',
        216: 'United States'
    }
    df['Country'] = df['Country Code'].map(country_code_to_name)
    return df

def mapear_rating_color(df):
    rating_color = {
        "3F7E00": "darkgreen",
        "5BA829": "green",
        "9ACD32": "lightgreen",
        "CDD614": "orange",
        "FFBA00": "red",
        "CBCBC8": "darkred",
        "FF7800": "darkred",
    }
    df['Rating color name'] = df['Rating color'].map(rating_color)
    return df

def categorizar_preco(df):
    def price_category(price_range):
        if price_range == 1:
            return "cheap"
        elif price_range == 2:
            return "normal"
        elif price_range == 3:
            return "expensive"
        else:
            return "gourmet"
    df['Price Category'] = df['Price range'].apply(price_category)
    return df

def renomear_colunas(dataframe):
    df = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    sem_espacos = lambda x: x.replace(" ", "")
    colunas_antigas = list(df.columns)
    colunas_antigas = list(map(title, colunas_antigas))
    colunas_antigas = list(map(sem_espacos, colunas_antigas))
    colunas_novas = list(map(snakecase, colunas_antigas))
    df.columns = colunas_novas
    return df

def extrair_primeira_culinaria(df):
    df["cuisines"] = df["cuisines"].apply(lambda x: x.split(",")[0] if isinstance(x, str) else x)
    return df

def remover_na_culinarias(df):
    return df.dropna(subset=['cuisines'])

def pipeline_dados(caminho_arquivo):
    df = carregar_dados(caminho_arquivo)
    df = mapear_rating_text(df)
    df = mapear_country_code(df)
    df = mapear_rating_color(df)
    df = categorizar_preco(df)
    df1 = renomear_colunas(df)
    df1 = extrair_primeira_culinaria(df1)
    df1 = remover_na_culinarias(df1)
    return df1

# =========================
# Módulo: Filtros Sidebar
# =========================

def filtro_paises(df):
    if 'country_code' in df.columns:
        if 'country' in df.columns:
            paises = sorted(df['country'].unique())
            paises_selecionados = st.multiselect(
                "Selecione os países:",
                options=paises,
                default=[paises[0]] if paises else []
            )
            df_filtrado = df[df['country'].isin(paises_selecionados)]
        else:
            paises = sorted(df['country_code'].unique())
            paises_selecionados = st.multiselect(
                "Selecione os países (código):",
                options=paises,
                default=[paises[0]] if paises else []
            )
            df_filtrado = df[df['country_code'].isin(paises_selecionados)]
    else:
        df_filtrado = df
    return df_filtrado

def filtro_faixa_preco(df):
    if 'price_category' in df.columns:
        precos = df['price_category'].unique()
        precos_selecionados = st.multiselect(
            "Selecione a faixa de preço:",
            options=sorted(precos),
            default=sorted(precos)
        )
        df_filtrado = df[df['price_category'].isin(precos_selecionados)]
    else:
        df_filtrado = df
    return df_filtrado

def botao_download(df):
    st.markdown("### Baixar dados tratados")
    st.download_button(
        label="Baixar CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name="dados_tratados.csv",
        mime="text/csv"
    )

def aplicar_filtros_sidebar(df1):
    with st.sidebar:
        st.header("Fome Zero")
        st.markdown("O melhor lugar para achar seu restaurante favorito!")
        df_filtrado = filtro_paises(df1)
        df_filtrado = filtro_faixa_preco(df_filtrado)
        botao_download(df_filtrado)
    return df_filtrado

# =========================
# Módulo: Métricas
# =========================

def calcular_metricas(df_filtrado):
    num_restaurantes = df_filtrado['restaurant_id'].nunique() if 'restaurant_id' in df_filtrado.columns else df_filtrado.shape[0]
    num_paises = df_filtrado['country_code'].nunique() if 'country_code' in df_filtrado.columns else 0
    num_cidades = df_filtrado['city'].nunique() if 'city' in df_filtrado.columns else 0
    num_avaliacoes = df_filtrado['votes'].sum() if 'votes' in df_filtrado.columns else 0
    tipos_culinaria = df_filtrado['cuisines'].nunique() if 'cuisines' in df_filtrado.columns else 0
    return num_restaurantes, num_paises, num_cidades, num_avaliacoes, tipos_culinaria

def exibir_metricas(df_filtrado):
    num_restaurantes, num_paises, num_cidades, num_avaliacoes, tipos_culinaria = calcular_metricas(df_filtrado)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(label="Restaurantes cadastrados", value=num_restaurantes)
    with col2:
        st.metric(label="Países cadastrados", value=num_paises)
    with col3:
        st.metric(label="Cidades cadastradas", value=num_cidades)
    with col4:
        st.metric(label="Avaliações feitas", value=num_avaliacoes)
    with col5:
        st.metric(label="Tipos de culinária", value=tipos_culinaria)

# =========================
# Módulo: Mapa
# =========================

def construir_popup(row):
    popup_text = ""
    if 'restaurant_name' in row and pd.notnull(row['restaurant_name']):
        popup_text += f"{row['restaurant_name']}"
    if 'aggregate_rating' in row and pd.notnull(row['aggregate_rating']):
        popup_text += f"<br>Nota: {row['aggregate_rating']}"
    if 'cuisines' in row and pd.notnull(row['cuisines']):
        popup_text += f"<br>Tipo de culinária: {row['cuisines']}"
    return popup_text if popup_text else None

def construir_mapa(df_filtrado):
    latitude_media = df_filtrado['latitude'].mean()
    longitude_media = df_filtrado['longitude'].mean()
    df_mapa = df_filtrado.dropna(subset=['latitude', 'longitude'])
    mapa = folium.Map(location=[latitude_media, longitude_media], zoom_start=2)
    for _, row in df_mapa.iterrows():
        cor = '#' + str(row['rating_color']) if not str(row['rating_color']).startswith('#') else str(row['rating_color'])
        popup_text = construir_popup(row)
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=4,
            popup=folium.Popup(popup_text, max_width=250) if popup_text else None,
            color=cor,
            fill=True,
            fill_color=cor,
            fill_opacity=0.7
        ).add_to(mapa)
    return mapa

def exibir_mapa_restaurantes(df_filtrado):
    exibir_mapa = st.checkbox("Exibir mapa dos restaurantes", value=True)
    if exibir_mapa:
        if 'latitude' in df_filtrado.columns and 'longitude' in df_filtrado.columns and not df_filtrado.empty:
            st.markdown("### Mapa dos restaurantes")
            mapa = construir_mapa(df_filtrado)
            st_folium(mapa, width=700, height=450)
        else:
            st.info("Não há informações de latitude e longitude para exibir o mapa.")

# =========================
# Módulo: Títulos
# =========================

def exibir_titulos():
    st.title("Fome Zero")
    st.markdown("### O melhor lugar para achar seu restaurante favorito!")
    st.markdown("#### Temos as seguintes marcas dentro da plataforma:")

# =========================
# Função principal
# =========================

def main():
    # Pipeline de dados
    df1 = pipeline_dados('data/zomato.csv')
    # Filtros e sidebar
    df_filtrado = aplicar_filtros_sidebar(df1)
    # Títulos
    exibir_titulos()
    # Métricas
    exibir_metricas(df_filtrado)
    st.markdown('---')
    # Mapa
    exibir_mapa_restaurantes(df_filtrado)

if __name__ == "__main__":
    main()
