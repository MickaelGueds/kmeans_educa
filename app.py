import streamlit as st
import pandas as pd
import datetime

# -----------------------------------
# 🔹 Carregar Dados
# -----------------------------------
# Dados médios dos clusters
df_media_clusters = pd.read_csv("medias_clusters_educacao.csv")
# Dados com diagnóstico
df_clusters = pd.read_csv("diagnostico_clusters_educacao.csv")
# Dados detalhados de cada município e cluster
df_municipios = pd.read_csv("municipios_clusters.csv")

# Criar nomes descritivos para os clusters (exemplo - você deve ajustar conforme os resultados reais)
# Estes nomes devem ser personalizados com base nas características identificadas
cluster_nomes = {}

# Preencher dinamicamente os nomes dos clusters com base nos perfis
for index, row in df_clusters.iterrows():
    cluster_id = str(row["cluster"])
    # Extrair o perfil principal (primeiras palavras do texto do perfil)
    perfil_text = row["Perfil"]
    # Usar as primeiras palavras como nome curto
    nome_curto = " ".join(perfil_text.split()[:4]) + "..." if len(perfil_text.split()) > 4 else perfil_text
    cluster_nomes[cluster_id] = nome_curto

# Adicionar coluna com nomes descritivos
df_clusters["Nome do Cluster"] = df_clusters["cluster"].astype(str).map(cluster_nomes)
df_media_clusters["Nome do Cluster"] = df_media_clusters["cluster"].astype(str).map(cluster_nomes)
if "cluster" in df_municipios.columns:
    df_municipios["Nome do Cluster"] = df_municipios["cluster"].astype(str).map(cluster_nomes)

# -----------------------------------
# 🔹 Configuração da Página
# -----------------------------------
st.set_page_config(page_title="Análise Educacional por Clusters", layout="wide")
st.title("📊 Análise Educacional Municipal por Clusters")
st.write("Este dashboard apresenta uma análise dos indicadores educacionais dos municípios utilizando a técnica de K-Means.")

# -----------------------------------
# 🔹 Seção 1 - Variáveis Utilizadas
# -----------------------------------
st.header("📌 Indicadores Utilizados")
st.markdown("""
- **IDHM**: Índice de Desenvolvimento Humano Municipal (2010).
- **IDEB AI - Pública**: Índice de Desenvolvimento da Educação Básica para Anos Iniciais.
- **IDEB Anos Finais - Pública**: Índice de Desenvolvimento da Educação Básica para Anos Finais.
- **Taxa de evasão ensino fund. Anos Iniciais**: Percentual de alunos que deixam a escola nos anos iniciais.
- **Taxa de evasão ensino fund. Anos Finais**: Percentual de alunos que deixam a escola nos anos finais.
- **Taxa de Abandono - Anos Iniciais**: Percentual de alunos que abandonam o ano letivo nos anos iniciais.
- **Taxa de Abandono - Anos Finais**: Percentual de alunos que abandonam o ano letivo nos anos finais.
""")

# -----------------------------------
# 🔹 Seção 2 - Contextualização dos Clusters
# -----------------------------------
st.header("🔍 Perfis Identificados")

# Gerar automaticamente a descrição dos perfis com base nos dados reais
perfis_html = ""
for cluster_id, nome in cluster_nomes.items():
    idx = df_clusters[df_clusters["cluster"].astype(str) == cluster_id].index[0]
    cluster_data = df_clusters.iloc[idx]
    
    # Extrair alguns pontos fortes e fracos para a descrição
    pontos_fortes = cluster_data["Pontos Fortes"].split("\n")
    pontos_fracos = cluster_data["Pontos Fracos"].split("\n")
    
    # Criar descrição resumida
    forte = pontos_fortes[0].replace("- ", "") if pontos_fortes and pontos_fortes[0] != "- Nenhum indicador destaca-se positivamente" else "Sem destaques positivos específicos"
    fraco = pontos_fracos[0].replace("- ", "") if pontos_fracos and pontos_fracos[0] != "- Nenhum indicador destaca-se negativamente" else "Sem desafios específicos"
    
    # Adicionar número legível (começando de 1)
    cluster_num = int(cluster_id) + 1
    
    perfis_html += f"{cluster_num}. **{nome}**: {forte}. {fraco}.\n\n"

st.markdown(perfis_html)

# -----------------------------------
# 🔹 Seção 3 - Média dos Clusters
# -----------------------------------
st.header("📊 Médias dos Indicadores por Cluster")

# Adicionar número do cluster começando de 1 para visualização
df_media_display = df_media_clusters.copy()
df_media_display["Cluster Nº"] = df_media_display["cluster"].astype(int) + 1

# Selecionar e ordenar colunas para visualização
colunas_display = ["Cluster Nº", "Nome do Cluster", "quantidade_municipios"]

# Adicionar colunas de indicadores formatadas
colunas_indicadores = [col for col in df_media_display.columns if col not in ["cluster", "Cluster Nº", "Nome do Cluster", "quantidade_municipios", "perfil"]]
colunas_display.extend(colunas_indicadores)

# Renomear colunas para melhor visualização
column_rename = {
    "quantidade_municipios": "Nº Municípios",
    "IDHM": "IDHM",
    "IDEB Anos Iniciais": "IDEB AI",
    "IDEB Anos Finais": "IDEB AF",
    "Taxa de Evasão AI": "Evasão AI (%)",
    "Taxa de Evasão AF": "Evasão AF (%)",
    "Taxa de Abandono AI": "Abandono AI (%)",
    "Taxa de Abandono AF": "Abandono AF (%)"
}

df_media_display = df_media_display[colunas_display].rename(columns=column_rename)
st.dataframe(df_media_display, use_container_width=True)

# -----------------------------------
# 🔹 Seção 4 - Mapa Interativo
# -----------------------------------
st.header("🗺️ Mapa Interativo dos Clusters")

# Obter a data atual para tentar vários formatos de nome de arquivo
data_atual = datetime.datetime.now()
possiveis_datas = [
    data_atual.strftime("%Y%m%d"),  # Hoje
    (data_atual - datetime.timedelta(days=1)).strftime("%Y%m%d")  # Ontem
]

mapa_encontrado = False
for data_str in possiveis_datas:
    try:
        arquivo_mapa = f"mapa_interativo_5clusters_educacao_{data_str}.html"
        with open(arquivo_mapa, "r", encoding="utf-8") as file:
            html_mapa = file.read()
        st.components.v1.html(html_mapa, height=600)
        mapa_encontrado = True
        break
    except FileNotFoundError:
        continue

if not mapa_encontrado:
    st.error("Arquivo do mapa interativo não encontrado. Verifique se o arquivo foi gerado corretamente.")
    st.info("Tente executar o script de geração do mapa antes de usar o dashboard.")

# -----------------------------------
# 🔹 Seção 5 - Diagnóstico dos Clusters
# -----------------------------------
st.header("📋 Diagnóstico dos Clusters")

# Preparar DataFrame para exibição
df_diagnostico_display = df_clusters.copy()
df_diagnostico_display["Cluster Nº"] = df_diagnostico_display["cluster"].astype(int) + 1
colunas_diagnostico = ["Cluster Nº", "Nome do Cluster", "Pontos Fortes", "Pontos Fracos", "Recomendações"]
st.dataframe(df_diagnostico_display[colunas_diagnostico], use_container_width=True)

# -----------------------------------
# 🔹 Seção 6 - Distribuição dos Municípios
# -----------------------------------
st.header("📊 Distribuição dos Municípios por Cluster")

# Contar municípios por cluster
if "cluster" in df_municipios.columns:
    # Criar DataFrame para contagem
    df_contagem = df_municipios["cluster"].astype(str).value_counts().reset_index()
    df_contagem.columns = ["Cluster", "Quantidade de Municípios"]
    
    # Adicionar número legível do cluster (começando de 1)
    df_contagem["Cluster Nº"] = df_contagem["Cluster"].astype(int) + 1
    
    # Adicionar nome do cluster
    df_contagem["Nome do Cluster"] = df_contagem["Cluster"].map(cluster_nomes)
    
    # Reorganizar colunas
    df_contagem = df_contagem[["Cluster Nº", "Nome do Cluster", "Quantidade de Municípios"]]
    
    # Exibir a contagem
    col1, col2 = st.columns([2, 3])
    with col1:
        st.dataframe(df_contagem, use_container_width=True)
    
    with col2:
        chart_data = df_contagem.set_index("Nome do Cluster")
        st.bar_chart(chart_data["Quantidade de Municípios"])

# -----------------------------------
# 🔹 Seção 7 - Dados Detalhados (Expansível)
# -----------------------------------
with st.expander("🔍 Ver Dados Completos por Município"):
    # Adicionar campo de busca
    search = st.text_input("Buscar município:")
    
    # Preparar DataFrame para exibição
    df_display = df_municipios.copy()
    if "cluster" in df_display.columns:
        df_display["Cluster Nº"] = df_display["cluster"].astype(int) + 1
    
    # Filtrar dados se houver busca
    if search:
        filtered_df = df_display[df_display["Município"].str.contains(search, case=False)]
    else:
        filtered_df = df_display
    
    # Exibir dados
    st.dataframe(filtered_df, use_container_width=True)

# -----------------------------------
# 🔹 Seção 8 - Metodologia
# -----------------------------------
with st.expander("📓 Metodologia"):
    st.markdown("""
    ### Processamento dos Dados
    
    1. **Pré-processamento**: 
       - Remoção de valores ausentes e tratamento de valores problemáticos ("#VALUE!")
       - Transformação logarítmica para corrigir assimetria
       - Padronização usando StandardScaler
    
    2. **Clustering**:
       - Algoritmo K-Means com 5 clusters
       - Número ideal de clusters determinado pelo método do cotovelo e silhueta
       - Validação por PCA (Análise de Componentes Principais)
    
    3. **Interpretação**:
       - Análise das médias dos indicadores por cluster
       - Diagnóstico de pontos fortes e fracos
       - Elaboração de recomendações específicas para cada perfil de município
    """)

# -----------------------------------
# 🔹 Rodapé
# -----------------------------------
st.markdown("---")

st.caption("Diretoria de Monitoramento de Políticas Públicas - DMP")