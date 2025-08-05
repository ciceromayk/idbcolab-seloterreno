import streamlit as st
from db import SessionLocal, init_db
from models import Terreno
from utils import calcular_pontuacao, definir_selo

# Configuração da página
st.set_page_config(
    page_title="Avaliação de Terrenos - SQI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("assets/custom.css")

# Inicializa o banco de dados
init_db()
session = SessionLocal()

st.sidebar.header("Menu")
opcao = st.sidebar.selectbox("Selecione a opção", ["Novo Terreno", "Histórico de Avaliações"])

if opcao == "Novo Terreno":
    st.title("Cadastro e Avaliação de Terreno")
    st.write("Preencha os dados do terreno conforme os critérios abaixo:")

    # Novo Macro Item: DADOS DO TERRENO
    with st.expander("DADOS DO TERRENO", expanded=True):
        descricao = st.text_input("DESCRIÇÃO DO TERRENO").upper()
        endereco = st.text_input("ENDEREÇO")
        area_terreno = st.number_input("ÁREA DO TERRENO (m²)", min_value=0.0, value=0.0, step=1.0, format="%.2f")
        altura_maxima = st.number_input("ALTURA MÁXIMA A CONSTRUIR EM METROS (m)", min_value=0.0, value=0.0, step=0.1, format="%.2f")
        lenol_freatico_permite = st.radio("LENÇOL FREÁTICO PERMITE SUBSOLO", options=["Sim", "Não"])
        responsavel = st.text_input("RESPONSÁVEL PELA AVALIAÇÃO")

    # Critérios Jurídicos (20%)
    with st.expander("CRITÉRIOS JURÍDICOS (20%)", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            doc_regular = st.slider("Documentação Regular (0 a 5)", 0, 5, 3)
        with col2:
            ausencia_onus = st.slider("Ausência de Ônus (0 a 5)", 0, 5, 3)
        with col3:
            potencial_aprovacao = st.slider("Potencial de Aprovação (0 a 10)", 0, 10, 6)

    # Critérios Físicos (30%)
    with st.expander("CRITÉRIOS FÍSICOS (30%)"):
        col1, col2 = st.columns(2)
        with col1:
            area_dimensoes = st.slider("Área e Dimensões (0 a 10)", 0, 10, 7)
            topografia = st.slider("Topografia (0 a 5)", 0, 5, 3)
        with col2:
            infraestrutura = st.slider("Infraestrutura Existente (0 a 5)", 0, 5, 3)
            zoneamento = st.slider("Zoneamento (0 a 10)", 0, 10, 7)

    # Critérios Comerciais (40%) com subitem Adequação do Produto
    with st.expander("CRITÉRIOS COMERCIAIS (40%)"):
        col1, col2 = st.columns(2)
        with col1:
            localizacao = st.slider("Localização (0 a 15)", 0, 15, 10)
            estimativa_vgv = st.slider("Estimativa de VGV (0 a 15)", 0, 15, 10)
        with col2:
            demanda_concorrencia = st.slider("Demanda e Concorrência (0 a 10)", 0, 10, 5)
            adequacao_produto = st.slider("Adequação do Produto (0 a 10)", 0, 10, 7)

    if st.button("Avaliar Terreno"):
        with st.spinner("Processando avaliação..."):
            total = calcular_pontuacao(
                doc_regular, ausencia_onus, potencial_aprovacao,
                area_dimensoes, topografia, infraestrutura, zoneamento,
                localizacao, estimativa_vgv, demanda_concorrencia,
                adequacao_produto
            )
            selo = definir_selo(total)

            st.success(f"Terreno avaliado com {total}% - {selo}")

            novo_terreno = Terreno(
                # Dados do Terreno
                descricao=descricao,
                endereco=endereco,
                area_terreno=area_terreno,
                altura_maxima=altura_maxima,
                lenol_freatico_permite_subsolo=True if lenol_freatico_permite == "Sim" else False,
                responsavel=responsavel,
                # Critérios Jurídicos
                doc_regular=doc_regular,
                ausencia_onus=ausencia_onus,
                potencial_aprovacao=potencial_aprovacao,
                # Critérios Físicos
                area_dimensoes=area_dimensoes,
                topografia=topografia,
                infraestrutura=infraestrutura,
                zoneamento=zoneamento,
                # Critérios Comerciais
                localizacao=localizacao,
                estimativa_vgv=estimativa_vgv,
                demanda_concorrencia=demanda_concorrencia,
                adequacao_produto=adequacao_produto,
                # Resultado Final
                score=total,
                selo=selo
            )
            session.add(novo_terreno)
            session.commit()
            st.info("Avaliação salva com sucesso!")

elif opcao == "Histórico de Avaliações":
    st.title("Histórico de Terrenos Avaliados")
    terrenos = session.query(Terreno).all()
    if terrenos:
        selos_disponiveis = list(set([t.selo for t in terrenos]))
        filtro_selo = st.selectbox("Filtrar por Selo", ["Todos"] + selos_disponiveis)
        for t in terrenos:
            if filtro_selo == "Todos" or t.selo == filtro_selo:
                st.markdown(
                    f"<div class='card'>\
                     <p>ID: {t.id}</p>\
                     <p>Data: {t.data_avaliacao.strftime('%Y-%m-%d %H:%M:%S')}</p>\
                     <p>Score: {t.score}%</p>\
                     <p><strong>Selo: {t.selo}</strong></p>\
                     </div>",
                    unsafe_allow_html=True
                )
    else:
        st.write("Nenhuma avaliação cadastrada ainda.")
