import streamlit as st
import pandas as pd
from db import SessionLocal, engine, Base
from models import Terreno
from utils import calcular_pontuacao, definir_selo

# Configuração da página e criação do banco de dados (caso não exista)
st.set_page_config(layout="wide")
Base.metadata.create_all(bind=engine)

css_personalizado = """
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
.streamlit-expanderHeader {
    font-size: 1.375rem !important;  /* 2pt maior */
    font-weight: bold !important;
}
</style>
"""
st.markdown(css_personalizado, unsafe_allow_html=True)

# Sidebar, menu e manutenção do banco
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
        col_area, col_altura = st.columns(2)
        with col_area:
            area_terreno = st.number_input("Área do terreno (m²)", min_value=0.0, step=1.0, key="area_terreno")
        with col_altura:
            altura_maxima = st.number_input("Altura máxima a construir (metros)", min_value=0.0, step=0.1, key="altura_maxima")
        lencol_perm = st.radio("Lençol freático permite subsolo?", ("Sim", "Não"), key="lencol_perm")
        if lencol_perm == "Não":
            nivel_lencol = st.number_input("Nível do lençol freático (metros)", min_value=0.0, step=0.1, key="nivel_lencol")
        else:
            nivel_lencol = 0.0
        permite_outorga = st.radio("Permite outorga?", ("Sim", "Não"), key="permite_outorga")
        responsavel_avaliacao = st.text_input("Responsável pela avaliação", key="responsavel_avaliacao")

    with st.expander("CRITÉRIOS JURÍDICOS (20%)", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("Documentação Regular (0 a 5):")
            doc_regular = st.slider("", 0, 5, 3, key="doc_regular")
        with col2:
            st.markdown("Ausência de Ônus (0 a 5):")
            ausencia_onus = st.slider("", 0, 5, 3, key="ausencia_onus")
        with col3:
            st.markdown("Potencial de Aprovação (0 a 10):")
            potencial_aprovacao = st.slider("", 0, 10, 6, key="potencial_aprovacao")

    with st.expander("CRITÉRIOS FÍSICOS (30%)", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("Área e Dimensões (0 a 10):")
            area_dimensoes = st.slider("", 0, 10, 7, key="area_dimensoes")
            st.markdown("Topografia (0 a 5):")
            topografia = st.slider("", 0, 5, 3, key="topografia")
        with col2:
            st.markdown("Infraestrutura Existente (0 a 5):")
            infraestrutura = st.slider("", 0, 5, 3, key="infraestrutura")
            st.markdown("Zoneamento (0 a 10):")
            zoneamento = st.slider("", 0, 10, 7, key="zoneamento")

    with st.expander("CRITÉRIOS COMERCIAIS (50%)", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("Localização (0 a 15):")
            localizacao = st.slider("", 0, 15, 10, key="localizacao")
            st.markdown("Estimativa de VGV (0 a 15):")
            estimativa_vgv = st.slider("", 0, 15, 10, key="estimativa_vgv")
        with col2:
            st.markdown("Demanda e Concorrência (0 a 10):")
            demanda_concorrencia = st.slider("", 0, 10, 5, key="demanda_concorrencia")
            st.markdown("Adequação do Produto (0 a 10):")
            adequacao_produto = st.slider("", 0, 10, 7, key="adequacao_produto")

    if st.button("Avaliar Terreno"):
        juridico_total  = doc_regular + ausencia_onus + potencial_aprovacao
        fisico_total    = area_dimensoes + topografia + infraestrutura + zoneamento
        comercial_total = localizacao + estimativa_vgv + demanda_concorrencia + adequacao_produto
        total = juridico_total + fisico_total + comercial_total
        selo = definir_selo(total)  # Retorna "A (Excelente)" ou só "A"

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
        letra_selo = texto_selo[4]  # Certo: só "A", "B", etc.
        selo_html = f"<div class='selo-categoria'>SELO {letra_selo}</div>"
        titulo_html = "<h3 style='font-weight:900; text-align:center; color:#183366; margin-bottom:28px;'>AVALIAÇÃO DO TERRENO</h3>"
        perc = min(int(float(total)), 100)

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
</div>
"""
        st.markdown(resumo_html, unsafe_allow_html=True)

# ==================== HISTÓRICO ==========================
elif st.session_state['pagina'] == 'historico':
    st.title("HISTÓRICO DE TERRENOS AVALIADOS")  # Título em caixa alta

    session = SessionLocal()
    try:
        terrenos = session.query(Terreno).order_by(Terreno.score.desc()).all()
        if terrenos:
            # Lista dinâmica dos selos disponíveis
            selos_disponiveis = sorted(list(set([t.selo for t in terrenos])))
            col_filtros = st.columns([1, 2])
            with col_filtros[0]:
                filtro_selo = st.selectbox("Filtrar por Selo", ["Todos"] + selos_disponiveis, key="filtro_selo")
            with col_filtros[1]:
                filtro_nome = st.text_input("Filtrar por Nome do Terreno", "", key="filtro_nome").strip().upper()

            dados = []
            for t in terrenos:
                # Filtro pelo selo
                passa_selo = filtro_selo == "Todos" or t.selo == filtro_selo
                # Filtro pelo nome do terreno (busca por substring, ignorando diferenças de maiúsculas/minúsculas)
                passa_nome = filtro_nome in (t.descricao_terreno or "").upper()
                if passa_selo and passa_nome:
                    dados.append({
                        "Nome do Terreno": t.descricao_terreno,
                        "Bairro": t.bairro if hasattr(t, "bairro") else "",
                        "Área do Terreno (m²)": t.area_terreno if hasattr(t, "area_terreno") else "",
                        "Altura Máxima (m)": t.altura_maxima if hasattr(t, "altura_maxima") else "",
                        "Jurídico": t.doc_regular + t.ausencia_onus + t.potencial_aprovacao,
                        "Físico": t.area_dimensoes + t.topografia + t.infraestrutura + t.zoneamento,
                        "Comercial": t.localizacao + t.estimativa_vgv + t.demanda_concorrencia + t.adequacao_produto,
                        "Score (%)": t.score,
                        "Selo": t.selo,
                        "Data": t.data_avaliacao.strftime('%d-%m-%Y'),
                    })
            if dados:
                cols_ordem = [
                    "Nome do Terreno", "Bairro", "Área do Terreno (m²)", "Altura Máxima (m)",
                    "Jurídico", "Físico", "Comercial", "Score (%)", "Selo", "Data"
                ]
                df = pd.DataFrame(dados)[cols_ordem]
                st.dataframe(df, use_container_width=True)
            else:
                st.write("Nenhuma avaliação cadastrada ainda para este filtro.")
        else:
            st.write("Nenhuma avaliação cadastrada ainda.")
    finally:
        session.close()
