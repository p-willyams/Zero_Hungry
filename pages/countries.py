import pandas as pd
import numpy as np
import plotly.express as px
import inflection
import streamlit as st

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
# Módulo: Filtros
# =========================

def filtrar_paises(df, paises_selecionados):
    return df[df['country'].isin(paises_selecionados)]

def obter_filtros_sidebar(df):
    paises_disponiveis = sorted(df['country'].unique())
    paises_selecionados = st.sidebar.multiselect(
        'Selecione os países que deseja visualizar',
        options=paises_disponiveis,
        default=paises_disponiveis
    )
    num_paises = st.sidebar.slider(
        'Quantidade máxima de países para exibir nos gráficos',
        min_value=0,
        max_value=20,
        value=min(10, len(paises_disponiveis)),
        step=1
    )
    return paises_selecionados, num_paises

# =========================
# Módulo: Gráficos
# =========================

def grafico_cidades_por_pais(df, num_paises):
    if 'country' in df.columns and 'city' in df.columns:
        cidades_por_pais = df.groupby('country')['city'].nunique().sort_values(ascending=False)
        if num_paises > 0:
            cidades_por_pais = cidades_por_pais.head(num_paises)
        fig = px.bar(
            cidades_por_pais.reset_index(),
            x='country',
            y='city',
            title='Número de cidades registradas por país',
            labels={'country': 'País', 'city': 'Número de cidades'}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Colunas 'country' ou 'city' não encontradas nos dados processados.")

def grafico_paises_mais_restaurantes(df, num_paises):
    paises_mais_restaurantes = df.groupby('country')['restaurant_id'].nunique().reset_index()
    paises_mais_restaurantes.columns = ['País', 'Número de restaurantes']
    paises_mais_restaurantes = paises_mais_restaurantes.sort_values(by='Número de restaurantes', ascending=False)
    if num_paises > 0:
        paises_mais_restaurantes = paises_mais_restaurantes.head(num_paises)
    fig = px.bar(
        paises_mais_restaurantes,
        x='País',
        y='Número de restaurantes',
        title='Número de restaurantes registrados por país'
    )
    st.plotly_chart(fig, use_container_width=True)

def grafico_media_avaliacoes_por_pais(df, num_paises):
    media_avaliacoes_por_pais = df.groupby('country')['votes'].mean().reset_index()
    media_avaliacoes_por_pais = media_avaliacoes_por_pais.sort_values(by='votes', ascending=False)
    if num_paises > 0:
        media_avaliacoes_por_pais = media_avaliacoes_por_pais.head(num_paises)
    fig = px.bar(
        media_avaliacoes_por_pais,
        x='country',
        y='votes',
        labels={'country': 'País', 'votes': 'Média de Avaliações'},
        title='Média de avaliações por restaurante em cada país'
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

def grafico_media_notas_por_pais(df, num_paises):
    if 'country' in df.columns and 'aggregate_rating' in df.columns:
        media_notas_por_pais = df.groupby('country')['aggregate_rating'].mean().reset_index()
        media_notas_por_pais_ordenado = media_notas_por_pais.sort_values(by='aggregate_rating', ascending=False)
        if num_paises > 0:
            media_notas_por_pais_ordenado = media_notas_por_pais_ordenado.head(num_paises)
        fig = px.bar(
            media_notas_por_pais_ordenado,
            x='country',
            y='aggregate_rating',
            labels={'country': 'País', 'aggregate_rating': 'Média das Notas'},
            title='Média das notas médias por restaurante em cada país'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Colunas 'country' ou 'aggregate_rating' não encontradas nos dados processados.")

# =========================
# Módulo: Layout da Página
# =========================

def exibir_titulo():
    st.title("Visão Países")

def exibir_grafico_cidades(df, num_paises):
    linha1 = st.columns(1)
    with linha1[0]:
        grafico_cidades_por_pais(df, num_paises)

def exibir_grafico_restaurantes(df, num_paises):
    linha2 = st.columns(1)
    with linha2[0]:
        grafico_paises_mais_restaurantes(df, num_paises)

def exibir_graficos_metricas(df, num_paises):
    linha3 = st.columns(2)
    with linha3[0]:
        grafico_media_avaliacoes_por_pais(df, num_paises)
    with linha3[1]:
        grafico_media_notas_por_pais(df, num_paises)

# =========================
# Módulo: Função Principal
# =========================

def main():
    # Carrega e trata os dados
    df1 = pipeline_dados('data/zomato.csv')

    # Filtros na sidebar
    paises_selecionados, num_paises = obter_filtros_sidebar(df1)

    # Filtra o dataframe de acordo com os países selecionados
    df1_filtrado = filtrar_paises(df1, paises_selecionados)

    # Layout da página
    exibir_titulo()
    exibir_grafico_cidades(df1_filtrado, num_paises)
    st.markdown('---')
    exibir_grafico_restaurantes(df1_filtrado, num_paises)
    st.markdown('---')
    exibir_graficos_metricas(df1_filtrado, num_paises)

if __name__ == "__main__":
    main()
