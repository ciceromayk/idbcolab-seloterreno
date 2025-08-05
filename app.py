import streamlit as st
from db import SessionLocal, engine, Base
from models import Terreno
from utils import calcular_pontuacao, definir_selo
import pandas as pd

# CSS para os cards finais do resumo, igual à imagem
css_estilo = """
<style>
.resumo-container {
    display: flex;
    justify-content: flex-start;
    gap: 21px;
    margin: 30px 0 0 0;
    flex-wrap: wrap;
}
.resumo-box {
    background: #ffe6eb;
    border-radius: 14px;
    box-shadow: 0 1.5px 8px 0 rgba(0,0,0,0.08);
    width: 155px;
    min-height: 125px;
    padding: 16px 6px 13px 6px;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.resumo-box h3 {
    font-size: 1.03rem;
    font-weight: 600;
    color: #39205f;
    margin: 0 0 10px 0;
    text-align: center;
    width: 100%;
}
.valor-grande {
    font-size: 2rem;
    color: #F52B2B;
    font-weight: 700;
    margin: 2px 0 0 0;
}
.valor-grande.sqi {
    color: #184eb8;
}
.selo-categoria {
    font-size: 1.02rem;
    color: #184eb8;
    font-weight: 700;
    margin: 8px 0 0 0;
    letter-spacing: 1.1px;
}
.selo-label {
    font-size: .99rem;
    color: #184eb8;
    font-weight: 500;
    line-height: 1.1;
    margin: 0;
}
@media (max-width: 650px) {
    .resumo-container {flex-direction: column;}
    .resumo-box {width:96vw;}
}
</style>
"""
st.markdown(css_estilo, unsafe_allow_html=True)

# Sidebar, menu, manutenção do banco
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

st.sidebar.markdown("---")
senha_input = st.sidebar.text_input("Digite a senha para limpar o banco", type="password", key="senha_banco")
if st.sidebar.button("Limpar Banco de Dados", use_container_width=True):
    if senha_input == "123456":
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        st.success("Banco de dados limpo com sucesso!")
    else:
        st.error("Senha incorreta. Acesso negado.")

# ==================== NOVO TERRENO ========================
if st.session_state['pagina'] == 'novo':
    st.title("CADASTRO E AVALIAÇÃO DE TERRENO")
    st.write("Preencha os dados do terreno conforme os critérios abaixo:")

    with st.expander("DADOS DO TERRENO", expanded=False):
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

    with st.expander("CRITÉRIOS JURÍDICOS (20%)", expanded=False):
        st.markdown("<p style='font-weight: bold;'>Critérios Jurídicos</p>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            doc_regular = st.slider("Documentação Regular (0 a 5)", 0, 5, 3)
        with col2:
            ausencia_onus = st.slider("Ausência de Ônus (0 a 5)", 0, 5, 3)
        with col3:
            potencial_aprovacao = st.slider("Potencial de Aprovação (0 a 10)", 0, 10, 6)

    with st.expander("CRITÉRIOS FÍSICOS (30%)", expanded=False):
        st.markdown("<p style='font-weight: bold;'>Critérios Físicos</p>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            area_dimensoes = st.slider("Área e Dimensões (0 a 10)", 0, 10, 7)
            topografia = st.slider("Topografia (0 a 5)", 0, 5, 3)
        with col2:
            infraestrutura = st.slider("Infraestrutura Existente (0 a 5)", 0, 5, 3)
            zoneamento = st.slider("Zoneamento (0 a 10)", 0, 10, 7)

    with st.expander("CRITÉRIOS COMERCIAIS (50%)", expanded=False):
        st.markdown(
            "<h4 style='font-weight:bold; text-align:center;'>Critérios Comerciais</h4>",
            unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            localizacao = st.slider("Localização (0 a 15)", 0, 15, 10)
            estimativa_vgv = st.slider("Estimativa de VGV (0 a 15)", 0, 15, 10)
            adequacao_produto = st.slider("Adequação do Produto (0 a 10)", 0, 10, 7)
        with col2:
            demanda_concorrencia = st.slider("Demanda e Concorrência (0 a 10)", 0, 10, 5)

    if st.button("Avaliar Terreno"):
        # Cálculo dos scores
        juridico_total  = doc_regular + ausencia_onus + potencial_aprovacao
        fisico_total    = area_dimensoes + topografia + infraestrutura + zoneamento
        comercial_total = localizacao + estimativa_vgv + demanda_concorrencia + adequacao_produto
        total = juridico_total + fisico_total + comercial_total
        selo = definir_selo(total) # deve retornar 'B (Bom)' ou 'B'

        session = SessionLocal()
        try:
            novo_terreno = Terreno(
                descricao_terreno=descricao_terreno,
                endereco=endereco,
                bairro=bairro,
                area_terreno=area_terreno,
                altura_maxima=altura_maxima,
                lencol_freatico_perm=lencol_perm,
                nivel_lencol=nivel_lencol,
                permite_outorga=permite_outorga,
                responsavel_avaliacao=responsavel_avaliacao,
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
        finally:
            session.close()

        # --------- RESUMO VISUAL FINAL -------------
        st.markdown("---")
        st.subheader("RESUMO DA AVALIAÇÃO")

        texto_selo = definir_selo(total)
        if "(" in texto_selo:
            letra, desc = texto_selo.split(" ",1)
            desc = desc.replace("(","").replace(")","")
        else:
            letra, desc = texto_selo, ""
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
                <div class='selo-categoria'>SQI {letra}</div>
                <p class='selo-label'>{desc}</p>
            </div>
        </div>
        """
        st.markdown(resumo_html, unsafe_allow_html=True)

# ==================== HISTÓRICO ==========================
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
                        "Data": t.data_avaliacao.strftime('%d-%m-%Y'),
                        "Endereço": t.endereco,
                        "Bairro": t.bairro if hasattr(t, "bairro") else "",
                        "Jurídico": t.doc_regular + t.ausencia_onus + t.potencial_aprovacao,
                        "Físico": t.area_dimensoes + t.topografia + t.infraestrutura + t.zoneamento,
                        "Comercial": t.localizacao + t.estimativa_vgv + t.demanda_concorrencia + t.adequacao_produto,
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
