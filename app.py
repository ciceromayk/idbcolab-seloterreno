import streamlit as st
from db import SessionLocal, init_db
from models import Terreno
from utils import calcular_pontuacao, definir_selo  # Importa as funções auxiliares

# Inicializa o banco de dados
init_db()
session = SessionLocal()

st.title("Avaliação de Terrenos - SQI")
st.sidebar.header("Menu")
opcao = st.sidebar.selectbox("Selecione a opção", ["Novo Terreno", "Histórico de Avaliações"])

if opcao == "Novo Terreno":
    st.header("Cadastro e Avaliação de Terreno")
    st.write("Preencha os dados do terreno conforme os critérios abaixo:")

    with st.container():  # Usando containers para organizar os campos
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Critérios Jurídicos (20%)")
            doc_regular = st.slider("Documentação Regular (0 a 5)", 0, 5, 3)
            ausencia_onus = st.slider("Ausência de Ônus (0 a 5)", 0, 5, 3)
            potencial_aprovacao = st.slider("Potencial de Aprovação (0 a 10)", 0, 10, 6)
        with col2:
            st.subheader("Critérios Físicos (30%)")
            area_dimensoes = st.slider("Área e Dimensões (0 a 10)", 0, 10, 7)
            topografia = st.slider("Topografia (0 a 5)", 0, 5, 3)
            infraestrutura = st.slider("Infraestrutura Existente (0 a 5)", 0, 5, 3)

    with st.container():
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Critérios Comerciais (40%)")
            localizacao = st.slider("Localização (0 a 15)", 0, 15, 10)
            estimativa_vgv = st.slider("Estimativa de VGV (0 a 15)", 0, 15, 10)
        with col4:
            zoneamento = st.slider("Zoneamento (0 a 10)", 0, 10, 7)
            demanda_concorrencia = st.slider("Demanda e Concorrência (0 a 10)", 0, 10, 5)


    st.subheader("Alinhamento com o Produto (10%)")
    adequacao_produto = st.slider("Adequação do Produto (0 a 10)", 0, 10, 7)

    if st.button("Avaliar Terreno"):
        # Calcula a pontuação total usando a função auxiliar
        total = calcular_pontuacao(doc_regular, ausencia_onus, potencial_aprovacao,
                                  area_dimensoes, topografia, infraestrutura, zoneamento,
                                  localizacao, estimativa_vgv, demanda_concorrencia,
                                  adequacao_produto)

        # Define o selo usando a função auxiliar
        selo = definir_selo(total)

        st.success(f"Terreno avaliado com {total}% - {selo}")

        # Salva a avaliação no banco de dados
        novo_terreno = Terreno(
            doc_regular=doc_regular,
            ausencia_onus=ausencia_onus,
            potencial_aprovacao=potencial_aprovacao,
            area_dimensoes=area_dimensoes,
            topografia=topografia,
            infraestrutura=infraestrutura,
            zoneamento=zoneamento,
            localizacao=localizacao,
            estimativa_vgv=estimativa_vgv,
            demanda_concorrencia=demanda_concorrencia,
            adequacao_produto=adequacao_produto,
            score=total,
            selo=selo
        )
        session.add(novo_terreno)
        session.commit()
        st.info("Avaliação salva com sucesso!")

elif opcao == "Histórico de Avaliações":
    st.header("Histórico de Terrenos Avaliados")
    terrenos = session.query(Terreno).all()
    if terrenos:
        # Adiciona opções de filtro (exemplo: por selo)
        selos_disponiveis = list(set([t.selo for t in terrenos]))
        filtro_selo = st.selectbox("Filtrar por Selo", ["Todos"] + selos_disponiveis)

        for t in terrenos:
            if filtro_selo == "Todos" or t.selo == filtro_selo:
                st.write(f"ID: {t.id} | Data: {t.data_avaliacao.strftime('%Y-%m-%d %H:%M:%S')} | Score: {t.score}% | Selo: {t.selo}")
    else:
        st.write("Nenhuma avaliação cadastrada ainda.")
