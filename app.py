import streamlit as st
import plotly.graph_objects as go
from db import SessionLocal, init_db, engine, Base
from models import Terreno
from utils import calcular_pontuacao, definir_selo
import pandas as pd

# Configuração da página
st.set_page_config(page_title="IDBCOLAB - COMITÊ DE PRODUTO", layout="wide")

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("assets/custom.css")

# Inicializa o banco
init_db()
session = SessionLocal()

# Sidebar
st.sidebar.image(
    "https://raw.githubusercontent.com/ciceromayk/idbcolab-referencia/main/LOGO%20IDBCOLAB.png",
    use_container_width=True
)
st.sidebar.markdown("## IDIBRA PARTICIPAÇÕES")
st.sidebar.header("Menu")

# Botões de navegação
novo_button = st.sidebar.button("Novo Terreno", use_container_width=True)
historico_button = st.sidebar.button("Histórico", use_container_width=True)

if novo_button:
    st.session_state['pagina'] = 'novo'
if historico_button:
    st.session_state['pagina'] = 'historico'

if 'pagina' not in st.session_state:
    st.session_state['pagina'] = 'inicio'

# Limpar banco
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
    
    # Critérios Comerciais + Adequação do Produto
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
            # Cálculo do score
            total = calcular_pontuacao(
                doc_regular, ausencia_onus, potencial_aprovacao,
                area_dimensoes, topografia, infraestrutura, zoneamento,
                localizacao, estimativa_vgv, demanda_concorrencia,
                adequacao_produto
            )

            # Calcular totais e converter em percentual
            juridico_total = doc_regular + ausencia_onus + potencial_aprovacao
            fisico_total = area_dimensoes + topografia + infraestrutura + zoneamento
            comercial_total = localizacao + estimativa_vgv + demanda_concorrencia + adequacao_produto

            juridico_perc = (juridico_total / 20) * 100
            fisico_perc = (fisico_total / 30) * 100
            comercial_perc = (comercial_total / 40) * 100  # ajustado para 40

            # Definir selo
            selo = definir_selo(total)

            # Salvar avaliação
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
                endereco=endereco,
                bairro=bairro,
                area_terreno=area_terreno,
                altura_maxima=altura_maxima,
                lençol_freatico_perm=lençol_freatico_perm,
                nivel_lençol=nivel_lençol,
                permite_outorga=permite_outorga,
                responsavel_avaliacao=responsavel_avaliacao
            )
            session.add(novo_terreno)
            session.commit()

            # Gerar gráfico radar com labels
            categorias = ['Jurídicos', 'Físicos', 'Comerciais']
            valores = [juridico_perc, fisico_perc, comercial_perc]
            valores_fechar = valores + [valores[0]]  # fecha o radar

            labels = [f"{cat}: {valor:.1f}%" for cat, valor in zip(categorias, valores)]

            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=valores_fechar,
                theta=categorias + [categorias[0]],
                fill='toself',
                text=labels,
                mode='lines+markers+text',
                textposition='top center',
                hoverinfo='text'
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                ),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

# Página de Histórico
elif st.session_state['pagina'] == 'historico':
    st.title("Histórico de Terrenos Avaliados")
    terrenos = session.query(Terreno).order_by(Terreno.score.desc()).all()
    if terrenos:
        selos_disponiveis = list(set([t.selo for t in terrenos]))
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
