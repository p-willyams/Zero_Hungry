import pandas as pd
import numpy as np
import plotly.express as px
import inflection
import streamlit as st

# ------------------- Funções de processamento de dados -------------------

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

# ------------------- Funções de filtro -------------------

def filtrar_paises(df, paises_selecionados):
    return df[df['country'].isin(paises_selecionados)]

# ------------------- Funções de gráficos -------------------

def grafico_top_cidades_restaurantes(df, num_cidades):
    restaurantes_por_cidade = (
        df.groupby(['city', 'country'])
        .size()
        .reset_index(name='numero_de_restaurantes')
        .sort_values(by='numero_de_restaurantes', ascending=False)
        .head(num_cidades)
        .rename(columns={'city': 'cidade', 'country': 'pais'})
    )
    fig = px.bar(
        restaurantes_por_cidade,
        x='cidade',
        y='numero_de_restaurantes',
        color='pais',
        labels={'cidade': 'Cidade', 'numero_de_restaurantes': 'Número de Restaurantes', 'pais': 'País'},
        title=f'Top {num_cidades} cidades com mais restaurantes'
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

def grafico_cidades_nota_alta(df, num_cidades):
    top_cidades_alta = (
        df[df['aggregate_rating'] > 4]
        .groupby(['city', 'country'])
        .size()
        .reset_index(name='numero_de_restaurantes')
        .sort_values(by='numero_de_restaurantes', ascending=False)
        .head(num_cidades)
        .rename(columns={'city': 'cidade', 'country': 'pais'})
        .reset_index(drop=True)
    )
    fig = px.bar(
        top_cidades_alta,
        x='cidade',
        y='numero_de_restaurantes',
        color='pais',
        labels={'cidade': 'Cidade', 'numero_de_restaurantes': 'Número de Restaurantes', 'pais': 'País'},
        title=f'Cidades com mais restaurantes com nota > 4 (top {num_cidades})'
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

def grafico_cidades_nota_baixa(df, num_cidades):
    top_cidades_baixa = (
        df[df['aggregate_rating'] < 2.5]
        .groupby(['city', 'country'])
        .size()
        .reset_index(name='numero_de_restaurantes')
        .sort_values(by='numero_de_restaurantes', ascending=False)
        .head(num_cidades)
        .rename(columns={'city': 'cidade', 'country': 'pais'})
        .reset_index(drop=True)
    )
    fig = px.bar(
        top_cidades_baixa,
        x='cidade',
        y='numero_de_restaurantes',
        color='pais',
        labels={'cidade': 'Cidade', 'numero_de_restaurantes': 'Número de Restaurantes', 'pais': 'País'},
        title=f'Cidades com mais restaurantes com nota < 2.5 (top {num_cidades})'
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

def grafico_cidades_mais_culinarias(df, num_cidades):
    top_cidades_culinarias = (
        df.groupby(['city', 'country'])['cuisines']
        .nunique()
        .reset_index(name='tipos_culinarios_distintos')
        .sort_values(by='tipos_culinarios_distintos', ascending=False)
        .head(num_cidades)
        .rename(columns={'city': 'cidade', 'country': 'pais'})
        .reset_index(drop=True)
    )
    fig = px.bar(
        top_cidades_culinarias,
        x='cidade',
        y='tipos_culinarios_distintos',
        color='pais',
        labels={'cidade': 'Cidade', 'tipos_culinarios_distintos': 'Tipos Culinários Distintos', 'pais': 'País'},
        title=f'Top {num_cidades} cidades com mais tipos culinários distintos (cores por país)'
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

# ------------------- Função principal -------------------

def main():
    # Pipeline de dados
    df1 = pipeline_dados('data/zomato.csv')

    # Filtros na Sidebar
    paises_disponiveis = sorted(df1['country'].unique())
    paises_selecionados = st.sidebar.multiselect(
        'Selecione os países',
        options=paises_disponiveis,
        default=paises_disponiveis
    )

    num_cidades = st.sidebar.slider(
        'Quantidade máxima de cidades para exibir nos gráficos',
        min_value=1,
        max_value=20,
        value=10,
        step=1
    )

    # Filtragem dos dados
    df_filtrado = filtrar_paises(df1, paises_selecionados)

    st.title("Visão Cidades")

    # Primeira linha: Top cidades com mais restaurantes
    linha1 = st.columns(1)
    with linha1[0]:
        grafico_top_cidades_restaurantes(df_filtrado, num_cidades)

    # Segunda linha: 2 colunas
    st.markdown('---')
    linha2 = st.columns(2)
    with linha2[0]:
        grafico_cidades_nota_alta(df_filtrado, num_cidades)
    with linha2[1]:
        grafico_cidades_nota_baixa(df_filtrado, num_cidades)

    # Terceira linha: 1 coluna
    st.markdown('---')
    linha3 = st.columns(1)
    with linha3[0]:
        grafico_cidades_mais_culinarias(df_filtrado, num_cidades)

if __name__ == "__main__":
    main()
