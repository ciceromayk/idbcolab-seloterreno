import streamlit as st
import plotly.graph_objects as go
from db import SessionLocal, engine, Base
from models import Terreno
from utils import calcular_pontuacao, definir_selo
import pandas as pd

# Configuração da página
st.set_page_config(page_title="IDBCOLAB - COMITÊ DE PRODUTO", layout="wide")

# CSS aprimorado para cards modernos (mantido do seu código)
css_estilo = """
<style>
.resumo-container {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 32px;
    margin: 35px 0 0;
    padding: 0 8vw;
}
.resumo-box {
    background: #fff0f4;
    border-radius: 18px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.09), 0 1.5px 6px rgba(0,0,0,0.03);
    width: 225px;
    min-height: 200px;
    padding: 28px 18px 22px;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    transition: box-shadow .22s, background .22s;
}
.resumo-box:hover {
    box-shadow: 0 10px 24px rgba(0,0,0,0.13);
    background: #ffe5ec;
}
.resumo-box h3 {
    font-family: 'Montserrat', Arial, sans-serif;
    font-size: 1.2rem;
    font-weight: 600;
    color: #2d2d47;
    margin: 0 0 16px;
    line-height: 1.2;
}
.valor-grande {
    font-size: 2.7rem;
    color: #F52B2B;
    font-weight: 700;
    margin: 12px 0 2px;
    font-family: 'Montserrat', Arial, sans-serif;
}
.valor-grande.sqi {
    color: #184eb8;
    margin-bottom: 12px;
}
.selo-categoria {
    font-size: 1.44rem;
    color: #184eb8;
    font-family: 'Montserrat', Arial, sans-serif;
    font-weight: 700;
    margin: 0;
    letter-spacing: 1.5px;
}
@media (max-width: 800px) {
    .resumo-container {
        flex-direction: column;
        align-items: center;
        padding: 0;
        gap: 22px;
    }
    .resumo-box {
        width: 95vw;
        min-width: 0;
    }
}
</style>
"""
st.markdown(css_estilo, unsafe_allow_html=True)

# Sidebar
st.sidebar.image(
    "https://raw.githubusercontent.com/ciceromayk/idbcolab-referencia/main/LOGO%20IDBCOLAB.png",
    use_container_width=True
)
st.sidebar.markdown("## IDIBRA PARTICIPAÇÕES")
st.sidebar.header("Menu")
novo_button = st.sidebar.button("Novo Terreno", use_container_width=True)
historico_button = st.sidebar.button("Histórico", use_container_width=True)
if novo_button:
    st.session_state['pagina'] = 'novo'
if historico_button:
    st.session_state['pagina'] = 'historico'
if 'pagina' not in st.session_state:
    st.session_state['pagina'] = 'inicio'

# Limpeza do banco
st.sidebar.markdown("---")
senha_input = st.sidebar.text_input("Digite a senha para limpar o banco", type="password", key="senha_banco")
if st.sidebar.button("Limpar Banco de Dados", use_container_width=True):
    if senha_input == "123456":
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        st.success("Banco limpo com sucesso!")
    else:
        st.error("Senha incorreta.")

# Página de Novo Terreno
if st.session_state['pagina'] == 'novo':
    st.title("CADASTRO E AVALIAÇÃO DE TERRENO")
    # --**[seu código de cadastro + avaliação mantido sem alterações]**--

    if st.button("Avaliar Terreno"):
        # --**[cálculo, salvamento e resumo estilizado mantidos tal como já estão]**--
        pass

# Página de Histórico
elif st.session_state['pagina'] == 'historico':
    st.title("Histórico de Terrenos Avaliados")
    session = SessionLocal()
    try:
        terrenos = session.query(Terreno).order_by(Terreno.score.desc()).all()

        if not terrenos:
            st.info("Nenhuma avaliação cadastrada ainda.")
        else:
            # Monta lista de registros com as colunas solicitadas:
            registros = []
            for t in terrenos:
                # Recalcula sub-totais a partir dos campos do modelo:
                juridico = (
                    t.doc_regular
                    + t.ausencia_onus
                    + t.potencial_aprovacao
                )
                fisico = (
                    t.area_dimensoes
                    + t.topografia
                    + t.infraestrutura
                    + t.zoneamento
                )
                comercial = (
                    t.localizacao
                    + t.estimativa_vgv
                    + t.demanda_concorrencia
                    + t.adequacao_produto
                )
                registros.append({
                    "Data": t.data_avaliacao.strftime("%d-%m-%Y"),
                    "Endereço": t.endereco,
                    "Bairro": t.bairro if hasattr(t, "bairro") else "",
                    "Jurídico": juridico,
                    "Físico": fisico,
                    "Comercial": comercial,
                    "Score (%)": t.score,
                    "Selo": t.selo
                })

            df = pd.DataFrame(registros)
            st.dataframe(df, use_container_width=True)

    finally:
        session.close()
