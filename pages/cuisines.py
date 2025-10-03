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

def filtrar_culinarias(df, culinarias_selecionadas):
    return df[df['cuisines'].isin(culinarias_selecionadas)]

def obter_filtros_sidebar(df1):
    """Modulariza a obtenção dos filtros da sidebar."""
    paises_disponiveis = sorted(df1['country'].unique())
    paises_selecionados = st.sidebar.multiselect(
        'Selecione os países que deseja visualizar',
        options=paises_disponiveis,
        default=paises_disponiveis
    )

    culinarias_disponiveis = sorted(df1['cuisines'].unique())
    culinarias_selecionadas = st.sidebar.multiselect(
        'Selecione os tipos de culinária',
        options=culinarias_disponiveis,
        default=culinarias_disponiveis
    )

    num_culinarias = st.sidebar.slider(
        'Quantidade máxima de tipos de culinária para exibir nos gráficos',
        min_value=1,
        max_value=20,
        value=10,
        step=1
    )

    num_restaurantes = st.sidebar.slider(
        'Quantidade máxima de restaurantes para exibir na tabela',
        min_value=1,
        max_value=20,
        value=10,
        step=1
    )

    return paises_selecionados, culinarias_selecionadas, num_culinarias, num_restaurantes

# =========================
# Módulo: Gráficos e Tabelas
# =========================

def grafico_top_culinarias(df, num_culinarias=10):
    top_culinarias = (
        df.groupby('cuisines')['aggregate_rating']
        .mean()
        .sort_values(ascending=False)
        .head(num_culinarias)
        .reset_index()
    )
    top_culinarias.columns = ['tipo_culinaria', 'nota_media']
    fig = px.bar(
        top_culinarias,
        x='tipo_culinaria',
        y='nota_media',
        labels={'tipo_culinaria': 'Tipo de Culinária', 'nota_media': 'Nota Média'},
        title=f'Top {num_culinarias} Tipos de Culinária por Nota Média'
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

def grafico_piores_culinarias(df, num_culinarias=10):
    piores_culinarias = (
        df.groupby('cuisines')['aggregate_rating']
        .mean()
        .sort_values(ascending=True)
        .head(num_culinarias)
        .reset_index()
    )
    piores_culinarias.columns = ['tipo_culinaria', 'nota_media']
    fig = px.bar(
        piores_culinarias,
        x='tipo_culinaria',
        y='nota_media',
        labels={'tipo_culinaria': 'Tipo de Culinária', 'nota_media': 'Nota Média'},
        title=f'Top {num_culinarias} Piores Tipos de Culinária por Nota Média'
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

def tabela_top_restaurantes(df, num_restaurantes=10):
    top_restaurantes = df.sort_values(by='aggregate_rating', ascending=False).head(num_restaurantes)
    st.dataframe(top_restaurantes[['restaurant_name', 'city', 'country', 'aggregate_rating', 'cuisines']])

def destaques_italianos(df, num_restaurantes=5):
    restaurantes_italianos = df[df['cuisines'].str.contains('italian', case=False, na=False)]
    top_italianos = restaurantes_italianos.sort_values(by='aggregate_rating', ascending=False).head(num_restaurantes).reset_index(drop=True)
    colunas_top = st.columns(num_restaurantes)
    for idx in range(num_restaurantes):
        with colunas_top[idx]:
            if idx < len(top_italianos):
                row = top_italianos.iloc[idx]
                nota = row['aggregate_rating']
                pais = row['country']
                cidade = row['city']
                nome_restaurante = row['restaurant_name'] if 'restaurant_name' in row else row['restaurant id'] if 'restaurant id' in row else ''
                st.metric(label=nome_restaurante, value=f"{nota}")
                st.write(f"**{cidade}, {pais}**")
            else:
                st.empty()

# =========================
# Módulo: Exibição
# =========================

def exibir_destaques_italianos(df_filtrado, num_restaurantes):
    st.markdown("## Melhores restaurantes de comida italiana")
    st.markdown("Abaixo estão os 5 melhores restaurantes de culinária italiana, classificados pela nota:")
    destaques_italianos(df_filtrado, num_restaurantes=5)

def exibir_tabela_top_restaurantes(df_filtrado, num_restaurantes):
    st.markdown("---")
    st.markdown(f"### Top {num_restaurantes} Restaurantes")
    tabela_top_restaurantes(df_filtrado, num_restaurantes=num_restaurantes)
    st.markdown("O restaurante com a maior nota é uma referência em qualidade e sabor.")

def exibir_graficos_culinarias(df_filtrado, num_culinarias):
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        grafico_top_culinarias(df_filtrado, num_culinarias=num_culinarias)
    with col2:
        grafico_piores_culinarias(df_filtrado, num_culinarias=num_culinarias)

# =========================
# Função principal
# =========================

def main():
    # Pipeline de dados
    df1 = pipeline_dados('data/zomato.csv')

    # Filtros na Sidebar
    paises_selecionados, culinarias_selecionadas, num_culinarias, num_restaurantes = obter_filtros_sidebar(df1)

    # Filtragem dos dados
    df_filtrado = filtrar_paises(df1, paises_selecionados)
    df_filtrado = filtrar_culinarias(df_filtrado, culinarias_selecionadas)

    # Exibição
    st.title("Visão Cozinhas")
    exibir_destaques_italianos(df_filtrado, num_restaurantes)
    exibir_tabela_top_restaurantes(df_filtrado, num_restaurantes)
    exibir_graficos_culinarias(df_filtrado, num_culinarias)

if __name__ == "__main__":
    main()