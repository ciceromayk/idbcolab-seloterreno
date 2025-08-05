import streamlit as st
import pandas as pd
from db import SessionLocal, engine, Base
from models import Terreno
from utils import calcular_pontuacao, definir_selo

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
    margin: 35px 0 0 0;
    padding: 0 8vw;
}
.resumo-box {
    background: #fff0f4;
    border-radius: 18px;
    box-shadow: 0 6px 20px 0 rgba(0,0,0,0.09), 0 1.5px 6px 0 rgba(0,0,0,0.03);
    width: 225px;
    min-height: 200px;
    text-align: center;
    padding: 28px 18px 22px 18px;
    display: flex;
    flex-direction: column;
    align-items: center;
    transition: box-shadow 0.22s, background 0.22s;
}
.resumo-box:hover {
    box-shadow: 0 10px 24px 0 rgba(0,0,0,0.13);
    background: #ffe5ec;
}
.resumo-box h3 {
    font-family: 'Montserrat', Arial, sans-serif;
    font-size: 1.18rem;
    font-weight: 600;
    color: #2d2d47;
    letter-spacing: 0.03em;
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

# Página de cadastro e avaliação
if st.session_state['pagina'] == 'novo':
    st.title("CADASTRO E AVALIAÇÃO DE TERRENO")
    st.write("Preencha os dados do terreno conforme os critérios abaixo:")

    # DADOS DO TERRENO
    with st.expander("DADOS DO TERRENO", expanded=False):
        descricao_terreno = st.text_input("Nome do terreno", max_chars=100).upper()
        endereco = st.text_input("Endereço")
        bairro = st.text_input("Bairro")
        area_terreno = st.number_input("Área do terreno (m²)", min_value=0.0, step=1.0)
        altura_maxima = st.number_input("Altura máxima a construir (m)", min_value=0.0, step=0.1)
        permite_subsolo = st.radio("Lençol freático permite subsolo?", ("Sim", "Não"))
        nivel_lencol = None
        if permite_subsolo == "Não":
            nivel_lencol = st.number_input("Nível do lençol (m)", min_value=0.0, step=0.1)
        permite_outorga = st.radio("Permite outorga?", ("Sim", "Não"))
        responsavel = st.text_input("Responsável pela avaliação")

    # CRITÉRIOS JURÍDICOS (20%)
    with st.expander("CRITÉRIOS JURÍDICOS (20%)", expanded=False):
        doc_regular = st.slider("Documentação Regular (0–5)", 0, 5, 3)
        ausencia_onus = st.slider("Ausência de Ônus (0–5)", 0, 5, 3)
        potencial_aprovacao = st.slider("Potencial de Aprovação (0–10)", 0, 10, 6)

    # CRITÉRIOS FÍSICOS (30%)
    with st.expander("CRITÉRIOS FÍSICOS (30%)", expanded=False):
        area_dim = st.slider("Área e Dimensões (0–10)", 0, 10, 7)
        topografia = st.slider("Topografia (0–5)", 0, 5, 3)
        infraestrutura = st.slider("Infraestrutura Existente (0–5)", 0, 5, 3)
        zoneamento = st.slider("Zoneamento (0–10)", 0, 10, 7)

    # CRITÉRIOS COMERCIAIS (50%)
    with st.expander("CRITÉRIOS COMERCIAIS (50%)", expanded=False):
        st.markdown("<h4 style='text-align:center;'>Critérios Comerciais</h4>", unsafe_allow_html=True)
        localizacao = st.slider("Localização (0–15)", 0, 15, 10)
        estimativa_vgv = st.slider("Estimativa de VGV (0–15)", 0, 15, 10)
        demanda = st.slider("Demanda e Concorrência (0–10)", 0, 10, 5)
        st.markdown("<h5>Adequação do Produto (0–10)</h5>", unsafe_allow_html=True)
        adequacao = st.slider("Adequação do Produto (0–10)", 0, 10, 7)

    # Botão Avaliar
    if st.button("Avaliar Terreno"):
        with st.spinner("Processando avaliação..."):
            # Somatórios e total (máx. 100p)
            juridico_total = doc_regular + ausencia_onus + potencial_aprovacao       # máx 20
            fisico_total = area_dim + topografia + infraestrutura + zoneamento      # máx 30
            comercial_total = localizacao + estimativa_vgv + demanda + adequacao    # máx 50
            total = juridico_total + fisico_total + comercial_total
            selo = definir_selo(total)  # retorna apenas 'A', 'B', 'C' ou 'D'

            # Salvar no banco
            session = SessionLocal()
            try:
                novo = Terreno(
                    descricao_terreno=descricao_terreno,
                    endereco=endereco,
                    bairro=bairro,
                    area_terreno=area_terreno,
                    altura_maxima=altura_maxima,
                    lençol_freatico_perm=permite_subsolo,
                    nivel_lençol=nivel_lencol,
                    permite_outorga=permite_outorga,
                    responsavel_avaliacao=responsavel,
                    score=total,
                    selo=selo
                )
                session.add(novo)
                session.commit()
            finally:
                session.close()

            # Resumo estilizado
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
        if not terrenos:
            st.info("Nenhuma avaliação cadastrada ainda.")
        else:
            selos = sorted({t.selo for t in terrenos})
            filtro = st.selectbox("Filtrar por Selo", ["Todos"] + selos)
            registros = []
            for t in terrenos:
                if filtro == "Todos" or t.selo == filtro:
                    registros.append({
                        "ID": t.id,
                        "Data": t.data_avaliacao.strftime('%Y-%m-%d %H:%M:%S'),
                        "Terreno": t.descricao_terreno,
                        "Bairro": t.bairro,
                        "Endereço": t.endereco,
                        "Área (m²)": t.area_terreno,
                        "Responsável": t.responsavel_avaliacao,
                        "Score (%)": t.score,
                        "Selo": t.selo
                    })
            df = pd.DataFrame(registros)
            st.dataframe(df, use_container_width=True)
    finally:
        session.close()
        
