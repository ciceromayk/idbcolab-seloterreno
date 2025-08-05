import streamlit as st
import plotly.graph_objects as go
from db import SessionLocal, init_db, engine, Base
from models import Terreno
from utils import calcular_pontuacao, definir_selo
import pandas as pd

# Configuração da página
st.set_page_config(page_title="IDBCOLAB - COMITÊ DE PRODUTO", layout="wide")

# CSS aprimorado para cards modernos
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

        lencol_perm = st.radio("Lençol freático permite subsolo?", ("Sim", "Não"), key="lencol_perm")
        if lencol_perm == "Não":
            nivel_lencol = st.number_input("Nível do lençol freático (metros)", min_value=0.0, step=0.1, key="nivel_lencol")
        else:
            nivel_lencol = None

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

    # Critérios Comerciais (com Adequação do Produto como subitem) – agora 50%
    with st.expander("CRITÉRIOS COMERCIAIS (50%)", expanded=False):
        st.markdown(
            "<h4 style='font-weight:bold; text-align:center;'>Critérios Comerciais</h4>",
            unsafe_allow_html=True
        )
        col1, col2 = st.columns(2)
        with col1:
            localizacao = st.slider("Localização (0 a 15)", 0, 15, 10)
            estimativa_vgv = st.slider("Estimativa de VGV (0 a 15)", 0, 15, 10)
        with col2:
            demanda_concorrencia = st.slider("Demanda e Concorrência (0 a 10)", 0, 10, 5)
        st.markdown(
            "<h5 style='margin-top:12px;'>Adequação do Produto (0 a 10)</h5>",
            unsafe_allow_html=True
        )
        adequacao_produto = st.slider("Adequação do Produto (0 a 10)", 0, 10, 7)

    if st.button("Avaliar Terreno"):
        with st.spinner("Processando avaliação..."):
            # Cálculo e soma dos subitens
            total = calcular_pontuacao(
                doc_regular, ausencia_onus, potencial_aprovacao,
                area_dimensoes, topografia, infraestrutura, zoneamento,
                localizacao, estimativa_vgv, demanda_concorrencia,
                adequacao_produto
            )

            juridico_total = doc_regular + ausencia_onus + potencial_aprovacao
            fisico_total = area_dimensoes + topografia + infraestrutura + zoneamento
            comercial_total = localizacao + estimativa_vgv + demanda_concorrencia + adequacao_produto

            selo = definir_selo(total)

            # Salvar avaliação
            session = SessionLocal()
            try:
                novo_terreno = Terreno(
                    descricao_terreno=descricao_terreno,
                    endereco=endereco,
                    bairro=bairro,
                    area_terreno=area_terreno,
                    altura_maxima=altura_maxima,
                    lençol_freatico_perm=lencol_perm,
                    nivel_lençol=nivel_lencol,
                    permite_outorga=permite_outorga,
                    responsavel_avaliacao=responsavel_avaliacao,
                    score=total,
                    selo=selo
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
                    <h3>Critérios<br>Jurídicos</h3>
                    <div class='valor-grande'>{juridico_total}</div>
                </div>
                <div class='resumo-box'>
                    <h3>Critérios<br>Físicos</h3>
                    <div class='valor-grande'>{fisico_total}</div>
                </div>
                <div class='resumo-box'>
                    <h3>Critérios<br>Comerciais</h3>
                    <div class='valor-grande'>{comercial_total}</div>
                </div>
                <div class='resumo-box'>
                    <h3>Pontuação<br>SELO SQI</h3>
                    <div class='valor-grande sqi'>{total}</div>
                    <div class='selo-categoria'>SQI {selo}</div>
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
            selos_disponiveis = sorted({t.selo for t in terrenos})
            filtro_selo = st.selectbox("Filtrar por Selo", ["Todos"] + selos_disponiveis)

            dados = []
            for t in terrenos:
                if filtro_selo == "Todos" or t.selo == filtro_selo:
                    dados.append({
                        "ID": t.id,
                        "Data": t.data_avaliacao.strftime('%Y-%m-%d %H:%M:%S'),
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
