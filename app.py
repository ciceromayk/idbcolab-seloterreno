import streamlit as st
from db import SessionLocal, init_db, engine, Base
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
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("assets/custom.css")

# Inicializa o banco
init_db()
session = SessionLocal()

# Sidebar com logotipo e botões alinhados verticalmente
st.sidebar.image("/workspaces/idbcolab-seloterreno/LOGO IDBCOLAB.png", use_container_width=True)
st.sidebar.header("Menu")
novo_button = st.sidebar.button("Novo Terreno")
historico_button = st.sidebar.button("Histórico")

if novo_button:
    st.session_state['pagina'] = 'novo'
if historico_button:
    st.session_state['pagina'] = 'historico'

if 'pagina' not in st.session_state:
    st.session_state['pagina'] = 'inicio'

st.sidebar.markdown("---")
senha_input = st.sidebar.text_input("Digite a senha para limpar o banco", type="password", key="senha_banco")
botao_limpar = st.sidebar.button("Limpar Banco de Dados")
if botao_limpar:
    if senha_input == "123456":
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        st.success("Banco de dados limpo com sucesso!")
    else:
        st.error("Senha incorreta. Acesso negado.")

# Página de Novo Terreno
if st.session_state['pagina'] == 'novo':
    st.title("Cadastro e Avaliação de Terreno")
    st.write("Preencha os dados do terreno conforme os critérios abaixo:")

    # Macro item: DADOS DO TERRENO (inicia colapsado)
    with st.expander("DADOS DO TERRENO", expanded=False):
        st.markdown("<p style='font-weight: bold;'>Descrição do Terreno</p>", unsafe_allow_html=True)
        descricao_terreno = st.text_area("Descrição do terreno", max_chars=500, key="descricao_terreno").upper()
        endereco = st.text_input("Endereço", key="endereco")
        area_terreno = st.number_input("Área do terreno (m²)", min_value=0.0, step=1.0, key="area_terreno")
        altura_maxima = st.number_input("Altura máxima a construir (metros)", min_value=0.0, step=0.1, key="altura_maxima")
        
        # Lençol freático
        lençol_freatico_perm = st.radio("Lençol freático permite subsolo?", ("Sim", "Não"), key="lençol_freatico_perm")
        if lençol_freatico_perm == "Não":
            nivel_lençol = st.number_input("Nível do lençol freático (metros)", min_value=0.0, step=0.1, key="nivel_lençol")
        else:
            nivel_lençol = None
        
        # Outorga
        permite_outorga = st.radio("Permite outorga?", ("Sim", "Não"), key="permite_outorga")
        
        # Responsável pela avaliação
        responsavel_avaliacao = st.text_input("Responsável pela avaliação", key="responsavel_avaliacao")

    # Critérios Jurídicos (20%)
    with st.expander("CRITÉRIOS JURÍDICOS (20%)", expanded=False):
        st.markdown("<p style='font-weight: bold;'>Critérios Jurídicos</p>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            doc_regular = st.slider("Documentação Regular (0 a 5)", 0, 5, 3)
        with col2:
            ausencia_onus = st.slider("Ausência de Ônus (0 a 5)", 0, 5, 3)
        with col3:
            potencial_aprovacao = st.slider("Potencial de Aprovação (0 a 10)", 0, 10, 6)

    # Critérios Físicos (30%)
    with st.expander("CRITÉRIOS FÍSICOS (30%)", expanded=False):
        st.markdown("<p style='font-weight: bold;'>Critérios Físicos</p>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            area_dimensoes = st.slider("Área e Dimensões (0 a 10)", 0, 10, 7)
            topografia = st.slider("Topografia (0 a 5)", 0, 5, 3)
        with col2:
            infraestrutura = st.slider("Infraestrutura Existente (0 a 5)", 0, 5, 3)
            zoneamento = st.slider("Zoneamento (0 a 10)", 0, 10, 7)

    # Critérios Comerciais (40%) com subitem "Adequação do Produto"
    with st.expander("CRITÉRIOS COMERCIAIS (40%)", expanded=False):
        st.markdown("<p style='font-weight: bold;'>Critérios Comerciais</p>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            localizacao = st.slider("Localização (0 a 15)", 0, 15, 10)
            estimativa_vgv = st.slider("Estimativa de VGV (0 a 15)", 0, 15, 10)
        with col2:
            demanda_concorrencia = st.slider("Demanda e Concorrência (0 a 10)", 0, 10, 5)
        st.markdown("**Adequação do Produto (0 a 10)**")
        adequacao_produto = st.slider("Adequação do Produto (0 a 10)", 0, 10, 7, key="adequacao_comerciais")

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
                selo=selo,
                descricao_terreno=descricao_terreno,
                area_terreno=area_terreno,
                responsavel_avaliacao=responsavel_avaliacao
            )
            session.add(novo_terreno)
            session.commit()
            st.info("Avaliação salva com sucesso!")

# Página de Histórico
elif st.session_state['pagina'] == 'historico':
    st.title("Histórico de Terrenos Avaliados")
    terrenos = session.query(Terreno).all()
    if terrenos:
        selos_disponiveis = list(set([t.selo for t in terrenos]))
        filtro_selo = st.selectbox("Filtrar por Selo", ["Todos"] + selos_disponiveis)
        for t in terrenos:
            if filtro_selo == "Todos" or t.selo == filtro_selo:
                st.markdown(
                    f"<div class='card'>"
                    f"<p><strong>ID:</strong> {t.id}</p>"
                    f"<p><strong>Data:</strong> {t.data_avaliacao.strftime('%Y-%m-%d %H:%M:%S')}</p>"
                    f"<p><strong>Descrição:</strong> {t.descricao_terreno}</p>"
                    f"<p><strong>Área:</strong> {t.area_terreno} m²</p>"
                    f"<p><strong>Responsável:</strong> {t.responsavel_avaliacao}</p>"
                    f"<p><strong>Score:</strong> {t.score}%</p>"
                    f"<p><strong>Selo:</strong> {t.selo}</p>"
                    "</div>",
                    unsafe_allow_html=True
                )
    else:
        st.write("Nenhuma avaliação cadastrada ainda.")
