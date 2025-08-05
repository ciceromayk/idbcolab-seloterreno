import streamlit as st
from db import SessionLocal, init_db
from models import Terreno

# Inicializa o banco de dados
init_db()
session = SessionLocal()

st.title("Avaliação de Terrenos - SQI")
st.sidebar.header("Menu")
opcao = st.sidebar.selectbox("Selecione a opção", ["Novo Terreno", "Histórico de Avaliações"])

if opcao == "Novo Terreno":
    st.header("Cadastro e Avaliação de Terreno")
    st.write("Preencha os dados do terreno conforme os critérios abaixo:")

    st.subheader("Critérios Jurídicos (20% do peso)")
    doc_regular = st.slider("Documentação Regular (0 a 5)", 0, 5, 3)
    ausencia_onus = st.slider("Ausência de Ônus (0 a 5)", 0, 5, 3)
    potencial_aprovacao = st.slider("Potencial de Aprovação (0 a 10)", 0, 10, 6)

    st.subheader("Critérios Físicos (30% do peso)")
    area_dimensoes = st.slider("Área e Dimensões (0 a 10)", 0, 10, 7)
    topografia = st.slider("Topografia (0 a 5)", 0, 5, 3)
    infraestrutura = st.slider("Infraestrutura Existente (0 a 5)", 0, 5, 3)
    zoneamento = st.slider("Zoneamento (0 a 10)", 0, 10, 7)

    st.subheader("Critérios Comerciais (40% do peso)")
    localizacao = st.slider("Localização (0 a 15)", 0, 15, 10)
    estimativa_vgv = st.slider("Estimativa de VGV (0 a 15)", 0, 15, 10)
    demanda_concorrencia = st.slider("Demanda e Concorrência (0 a 10)", 0, 10, 5)

    st.subheader("Alinhamento com o Produto (10% do peso)")
    adequacao_produto = st.slider("Adequação do Produto (0 a 10)", 0, 10, 7)

    if st.button("Avaliar Terreno"):
        # Cálculo da pontuação total (máximo = 100)
        total = (
            (doc_regular + ausencia_onus + potencial_aprovacao) +
            (area_dimensoes + topografia + infraestrutura + zoneamento) +
            (localizacao + estimativa_vgv + demanda_concorrencia) +
            (adequacao_produto)
        )
        
        # Definição do selo com base no score
        if total >= 80:
            selo = "SQI A (Excelente)"
        elif total >= 60:
            selo = "SQI B (Bom)"
        elif total >= 40:
            selo = "SQI C (Médio)"
        else:
            selo = "SQI D (Atenção)"
        
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
        for t in terrenos:
            st.write(f"ID: {t.id} | Data: {t.data_avaliacao.strftime('%Y-%m-%d %H:%M:%S')} | Score: {t.score}% | Selo: {t.selo}")
    else:
        st.write("Nenhuma avaliação cadastrada ainda.")
