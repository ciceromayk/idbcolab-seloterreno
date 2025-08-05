import streamlit as st
from db import SessionLocal, engine, Base
from models import Terreno
from utils import calcular_pontuacao, definir_selo
import pandas as pd

# Configuração da página
st.set_page_config(page_title="IDBCOLAB - COMITÊ DE PRODUTO", layout="wide")

# CSS estilizado para o resumo (incluindo centralização dos títulos)
css_estilo = """
<style>
.resumo-container {
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
    margin-top: 30px;
    font-family: Arial, sans-serif;
}
.resumo-box {
    background-color: #ffe6e6;
    padding: 20px;
    border-radius: 10px;
    width: 220px;
    text-align: center;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.resumo-box h3 {
    margin-top: 0;
    margin-bottom: 10px;
    text-align: center;
    width: 100%;
}
.valor-grande {
    font-size: 36px;
    font-weight: bold;
    margin: 10px 0;
}
.selo-categoria {
    font-size: 32px;
    font-weight: bold;
    color: #032BF4;
    margin-top: 8px;
}
</style>
"""

st.markdown(css_estilo, unsafe_allow_html=True)

# Setup do seu app
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
botao_limpar = st.sidebar.button("Limpar Banco de Dados", use_container_width=True)
if botao_limpar:
    if senha_input == "123456":
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        st.success("Banco de dados limpo com sucesso!")
    else:
        st.error("Senha incorreta. Acesso negado.")

# Página de Novo Terreno
if st.session_state['pagina'] == 'novo':
    st.title("CADASTRO E AVALIAÇÃO DE TERRENO")
    st.write("Preencha os dados do terreno conforme os critérios abaixo:")

    with st.expander("DADOS DO TERRENO", expanded=False):
        st.markdown("<p style='font-weight: bold;'>Nome do terreno</p>", unsafe_allow_html=True)
        descricao_terreno = st.text_input("Nome do terreno", max_chars=100, key="descricao_terreno").upper()
        endereco = st.text_input("Endereço", key="endereco")
        bairro = st.text_input("Bairro", key="bairro")
        area_terreno = st.number_input("Área do terreno (m²)", min_value=0.0, step=1.0, key="area_terreno")
        altura_maxima = st.number_input("Altura máxima a construir (metros)", min_value=0.0, step=0.1, key="altura_maxima")

        lençol_freatico_perm = st.radio("Lençol freático permite subsolo?", ("Sim", "Não"), key="lençol_freatico_perm")
        if lençol_freatico_perm == "Não":
            nivel_lençol = st.number_input("Nível do lençol freático (metros)", min_value=0.0, step=0.1, key="nivel_lençol")
        else:
            nivel_lençol = None

        permite_outorga = st.radio("Permite outorga?", ("Sim", "Não"), key="permite_outorga")
        responsavel_avaliacao = st.text_input("Responsável pela avaliação", key="responsavel_avaliacao")

    # Critérios Jurídicos
    with st.expander("CRITÉRIOS JURÍDICOS (20%)", expanded=False):
        st.markdown("<p style='font-weight: bold;'>Critérios Jurídicos</p>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            doc_regular = st.slider("Documentação Regular (0 a 5)", 0, 5, 3)
        with col2:
            ausencia_onus = st.slider("Ausência de Ônus (0 a 5)", 0, 5, 3)
        with col3:
            potencial_aprovacao = st.slider("Potencial de Aprovação (0 a 10)", 0, 10, 6)

    # Critérios Físicos
    with st.expander("CRITÉRIOS FÍSICOS (30%)", expanded=False):
        st.markdown("<p style='font-weight: bold;'>Critérios Físicos</p>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            area_dimensoes = st.slider("Área e Dimensões (0 a 10)", 0, 10, 7)
            topografia = st.slider("Topografia (0 a 5)", 0, 5, 3)
        with col2:
            infraestrutura = st.slider("Infraestrutura Existente (0 a 5)", 0, 5, 3)
            zoneamento = st.slider("Zoneamento (0 a 10)", 0, 10, 7)

    # Critérios comerciais + adequação do produto (agora com 50% do score!)
    with st.expander("CRITÉRIOS COMERCIAIS (50%)", expanded=False):
        st.markdown("<h4 style='font-weight: bold; text-align:center;'>Critérios Comerciais</h4>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            localizacao = st.slider("Localização (0 a 15)", 0, 15, 10)
            estimativa_vgv = st.slider("Estimativa de VGV (0 a 15)", 0, 15, 10)
        with col2:
            demanda_concorrencia = st.slider("Demanda e Concorrência (0 a 10)", 0, 10, 5)
        st.markdown("<h5 style='margin-bottom:2px;'>Adequação do Produto (0 a 10)</h5>", unsafe_allow_html=True)
        adequacao_produto = st.slider("Adequação do Produto (0 a 10)", 0, 10, 7, key="adequacao_comerciais")

    if st.button("Avaliar Terreno"):
        with st.spinner("Processando avaliação..."):
            # AJUSTE DE PESOS
            juridico_total = doc_regular + ausencia_onus + potencial_aprovacao      # Máx 20 pontos
            fisico_total = area_dimensoes + topografia + infraestrutura + zoneamento  # Máx 30 pontos
            comercial_total = localizacao + estimativa_vgv + demanda_concorrencia + adequacao_produto  # Máx 50 pontos

            total = juridico_total + fisico_total + comercial_total     # Máx 100 pontos

            # Selo categoria
            selo = definir_selo(total)

            # Salvar avaliação no banco
            session = SessionLocal()
            try:
                novo_terreno = Terreno(
                    descricao_terreno=descricao_terreno,
                    endereco=endereco,
                    bairro=bairro,
                    area_terreno=area_terreno,
                    altura_maxima=altura_maxima,
                    lençol_freatico_perm=lençol_freatico_perm,
                    nivel_lençol=nivel_lençol,
                    permite_outorga=permite_outorga,
                    responsavel_avaliacao=responsavel_avaliacao,
                    score=total,
                    selo=selo
                    # Adicione outros campos obrigatórios do seu modelo Terreno se necessário
                )
                session.add(novo_terreno)
                session.commit()
            finally:
                session.close()

            # Exibir o resultado com estilo
            st.markdown("---")
            st.subheader("RESUMO DA AVALIAÇÃO")

            resumo_html = f"""
            <div class='resumo-container'>
                <div class='resumo-box'>
                    <h3>Critérios Jurídicos</h3>
                    <div class='valor-grande' style='color:red;'>{juridico_total}</div>
                </div>
                <div class='resumo-box'>
                    <h3>Critérios Físicos</h3>
                    <div class='valor-grande' style='color:red;'>{fisico_total}</div>
                </div>
                <div class='resumo-box'>
                    <h3>Critérios Comerciais</h3>
                    <div class='valor-grande' style='color:red;'>{comercial_total}</div>
                </div>
                <div class='resumo-box'>
                    <h3>PONTUAÇÃO SELO SQI</h3>
                    <div class='valor-grande' style='color:blue;'>{total}</div>
                    <div class='selo-categoria'>SELO CATEGORIA: {selo}</div>
                </div>
            </div>
            """
            st.markdown(resumo_html, unsafe_allow_html=True)


# Página de Histórico
elif st.session_state['pagina'] == 'historico':
    st.title("Histórico de Terrenos Avaliados")
    session = SessionLocal()
    try:
        terrenos = session.query(Terreno).order_by(Terreno.score.desc()).all()
        if terrenos:
            selos_disponiveis = list(set([t.selo for t in terrenos]))
            filtro_selo = st.selectbox("Filtrar por Selo", ["Todos"] + selos_disponiveis)

            dados = []
            for t in terrenos:
                if filtro_selo == "Todos" or t.selo == filtro_selo:
                    dados.append({
                        "ID": t.id,
                        "Data": t.data_avaliacao.strftime('%Y-%m-%d %H:%M:%S') if hasattr(t, 'data_avaliacao') else "",
                        "Nome do Terreno": t.descricao_terreno,
                        "Bairro": t.bairro if hasattr(t, "bairro") else "",
                        "Endereço": t.endereco,
                        "Área (m²)": t.area_terreno,
                        "Responsável": t.responsavel_avaliacao,
                        "Score (%)": t.score,
                        "Selo": t.selo
                    })
            if dados:
                df = pd.DataFrame(dados)
                st.dataframe(df, use_container_width=True)
            else:
                st.write("Nenhuma avaliação cadastrada ainda para este filtro.")
        else:
            st.write("Nenhuma avaliação cadastrada ainda.")
    finally:
        session.close()
