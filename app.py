import streamlit as st
import textwrap
from db import SessionLocal, engine, Base
from models import Terreno
from utils import calcular_pontuacao, definir_selo
import pandas as pd

# Layout largo
st.set_page_config(layout="wide")

css_estilo = """
<style>
.resumo-avaliacao-box {
    background: linear-gradient(100deg, #f8fafc 80%, #e9e0fa 100%);
    border-radius: 22px;
    box-shadow: 0 4px 32px 0 rgba(30,41,59,.07);
    padding: 32px 26px 22px 26px;
    margin: 32px 0 32px 0;
}
.resumo-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(155px, 1fr));
    gap: 26px;
    justify-content: center;
    margin-bottom: 26px;
}
.resumo-col {
    background: white;
    border-radius: 16px;
    box-shadow: 0 2px 12px #4a007166;
    padding: 18px 10px 15px 10px;
    display: flex;
    flex-direction: column;
    align-items: center;
    min-height: 150px;
    transition: box-shadow .2s;
}
.resumo-col:hover {
    box-shadow: 0 6px 28px #4a007150;
}
.resumo-col .icon {
    font-size: 2.1rem;
    margin-bottom: 5px;
    opacity: .85;
}
.resumo-col h4 {
    font-weight: 900;
    color: #5535aa;
    font-size: 1.19rem;
    margin-bottom: 8px;
    letter-spacing: 1px;
    text-align:center;
    text-transform: uppercase;
}
.valor-card {
    font-size: 2.38rem;
    font-weight: 900;
    line-height: 1;
    margin: 10px 0;
    color: #f52b2b;
}
.valor-card.sqi, .selo-categoria { color: #1d5cf7; }
.valor-pequeno { font-size: 1.06rem; color:#837aa7; font-weight: 400;}
.selo-categoria {
    font-size: 2.05rem;
    font-weight: 900;
    margin-top: 14px;
    letter-spacing: 1.1px;
    text-transform: uppercase;
}
.selo-label {
    font-size: 1.01rem;
    color: #39205f;
    margin-top:2px;
    font-weight: 500;
    opacity: 0.70;
    display: none;
}
.progress-bar-bg{
    width:100%; background:#f3eded; border-radius:9px; height:26px; margin:15px 0 7px 0;
}
.progress-bar-inner{
    background:linear-gradient(90deg,#74fabd 0%,#2376f8 100%);
    height:26px; border-radius:9px;
    text-align:right; color:#fff; font-weight:700; padding-right:13px;
    font-size:1.13rem; transition:width .7s;
    box-shadow: 0 2px 8px #42268e20;
    display:flex; align-items:center; justify-content:flex-end;
}
.classificacao-legenda{
    display:flex;
    justify-content:space-between;
    font-size:0.92rem;
    color:#a386e7;
    margin:0 12px 0 12px;
    opacity:.85
}
@media (max-width: 900px){
    .resumo-grid{ grid-template-columns: repeat(2, minmax(140px, 1fr)); }
}
@media (max-width: 600px){
    .resumo-avaliacao-box{padding:10px 4px;}
    .resumo-grid{ grid-template-columns: 1fr; gap:16px;}
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
            nivel_lencol = 0.0  # CORRIGIDO: garante nunca ser None.
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
        with col2:
            demanda_concorrencia = st.slider("Demanda e Concorrência (0 a 10)", 0, 10, 5)
            adequacao_produto = st.slider("Adequação do Produto (0 a 10)", 0, 10, 7)

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

        texto_selo = definir_selo(total)
        if "(" in texto_selo:
            letra, _ = texto_selo.split(" ",1)
        else:
            letra = texto_selo
        letra_selo = letra
        selo_html = f"<div class='selo-categoria'>SELO {letra_selo}</div>" if total < 60 else f"<div class='selo-categoria'>SELO {letra_selo} SQI</div>"
        titulo_html = "<h3 style='font-weight:900; text-align:center; color:#183366; margin-bottom:28px;'>AVALIAÇÃO DO TERRENO</h3>"
        perc = min(int(float(total)/100*100), 100)

        resumo_html = f"""{titulo_html}
        <div class="resumo-avaliacao-box">
        <div class="resumo-grid">
        <div class="resumo-col">
        <span class="icon">⚖️</span>
        <h4>JURÍDICO</h4>
        <div class="valor-card">{juridico_total}%</div>
        <div class="valor-pequeno">até 20%</div>
        </div>
        <div class="resumo-col">
        <span class="icon">🏗️</span>
        <h4>FÍSICO</h4>
        <div class="valor-card">{fisico_total}%</div>
        <div class="valor-pequeno">até 30%</div>
        </div>
        <div class="resumo-col">
        <span class="icon">💰</span>
        <h4>COMERCIAL</h4>
        <div class="valor-card">{comercial_total}%</div>
        <div class="valor-pequeno">até 50%</div>
        </div>
        <div class="resumo-col" style="background:linear-gradient(120deg,#eaf6ff 80%,#dbe0ff 100%)">
        <span class="icon">🏆</span>
        <h4 style="color:#15388a">PONTUAÇÃO SQI</h4>
        <div class="valor-card sqi">{total}%</div>
        {selo_html}
        <div class="selo-label"></div>
        </div>
        </div>
        <div class="progress-bar-bg" style="margin-bottom:2px;">
        <div class="progress-bar-inner" style="width:{perc}%">{perc}%</div>
        </div>
        <div class="classificacao-legenda" style="margin-top:6px;">
        <span>D (Regular)</span>
        <span>C (Médio)</span>
        <span>B (Bom)</span>
        <span>A (Excelente)</span>
        </div>
        </div>"""

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
