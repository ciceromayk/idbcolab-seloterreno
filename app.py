import streamlit as st
from db import SessionLocal, engine, Base
from models import Terreno
from utils import calcular_pontuacao, definir_selo
import pandas as pd

# Configuração da página
st.set_page_config(page_title="IDBCOLAB - COMITÊ DE PRODUTO", layout="wide")

# (seu CSS para cards e resumo mantém-se idêntico ao já definido)

# SIDEBAR e lógica de menu (sem alterações)...
st.sidebar.image(
    "https://raw.githubusercontent.com/ciceromayk/idbcolab-referencia/main/LOGO%20IDBCOLAB.png",
    use_container_width=True
)
st.sidebar.markdown("## IDIBRA PARTICIPAÇÕES")
st.sidebar.header("Menu")
if st.sidebar.button("Novo Terreno", use_container_width=True):
    st.session_state['pagina'] = 'novo'
if st.sidebar.button("Histórico", use_container_width=True):
    st.session_state['pagina'] = 'historico'
if 'pagina' not in st.session_state:
    st.session_state['pagina'] = 'inicio'

# Limpar banco (sem alterações)...
st.sidebar.markdown("---")
senha_input = st.sidebar.text_input("Senha para limpar o banco", type="password")
if st.sidebar.button("Limpar Banco de Dados", use_container_width=True):
    if senha_input == "123456":
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        st.success("Banco limpo!")
    else:
        st.error("Senha incorreta.")

# ---- PÁGINA: NOVO TERRENO ------------------------------------------------
if st.session_state['pagina'] == 'novo':
    st.title("CADASTRO E AVALIAÇÃO DE TERRENO")

    # Seus expanders de DADOS, JURÍDICOS, FÍSICOS e COMERCIAIS via st.expander()
    # … mantidos iguais ao seu código, inclusive PESOS ajustados para 20/30/50.

    # Exemplo de sliders (resumido):
    doc_regular        = st.slider("Documentação Regular (0–5)", 0, 5, 3)
    ausencia_onus      = st.slider("Ausência de Ônus (0–5)",          0, 5, 3)
    potencial_aprovacao= st.slider("Potencial de Aprovação (0–10)",    0,10, 6)

    area_dimensoes     = st.slider("Área e Dimensões (0–10)",          0,10, 7)
    topografia         = st.slider("Topografia (0–5)",                 0, 5, 3)
    infraestrutura     = st.slider("Infraestrutura (0–5)",             0, 5, 3)
    zoneamento         = st.slider("Zoneamento (0–10)",                0,10, 7)

    localizacao        = st.slider("Localização (0–15)",               0,15,10)
    estimativa_vgv     = st.slider("Estimativa de VGV (0–15)",         0,15,10)
    demanda_concorrencia = st.slider("Demanda e Concorrência (0–10)",  0,10, 5)
    adequacao_produto  = st.slider("Adequação do Produto (0–10)",      0,10, 7)

    if st.button("Avaliar Terreno"):
        # Calcula totais
        juridico_total  = doc_regular + ausencia_onus + potencial_aprovacao    # até 20
        fisico_total    = area_dimensoes + topografia + infraestrutura + zoneamento  # até 30
        comercial_total = localizacao + estimativa_vgv + demanda_concorrencia + adequacao_produto  # até 50
        total = juridico_total + fisico_total + comercial_total                # até 100
        selo  = definir_selo(total)  # 'A','B','C' ou 'D'

        # Salva TODOS os valores no banco
        session = SessionLocal()
        try:
            novo = Terreno(
                # campos básicos
                descricao_terreno=st.session_state.get('descricao_terreno',''),
                endereco=st.session_state.get('endereco',''),
                bairro=st.session_state.get('bairro',''),
                area_terreno=st.session_state.get('area_terreno',0),
                altura_maxima=st.session_state.get('altura_maxima',0.0),
                lençol_freatico_perm=st.session_state.get('lencol_perm',''),
                nivel_lençol=st.session_state.get('nivel_lencol',None),
                permite_outorga=st.session_state.get('permite_outorga',''),
                responsavel_avaliacao=st.session_state.get('responsavel_avaliacao',''),
                # sub-scores
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
                # totais
                score=total,
                selo=selo
            )
            session.add(novo)
            session.commit()
        finally:
            session.close()

        # Aqui entra seu resumo estilizado (mantido igual ao anterior)…
        st.success(f"Terreno avaliado!  Total = {total}, Selo = SQI {selo}")

# ---- PÁGINA: HISTÓRICO ----------------------------------------------------
elif st.session_state['pagina'] == 'historico':
    st.title("Histórico de Terrenos Avaliados")
    session = SessionLocal()
    try:
        todos = session.query(Terreno).order_by(Terreno.data_avaliacao.desc()).all()
        if not todos:
            st.info("Nenhuma avaliação cadastrada.")
        else:
            registros = []
            for t in todos:
                registros.append({
                    # Data formatada DD-MM-YYYY
                    "Data": t.data_avaliacao.strftime("%d-%m-%Y"),
                    "Endereço": t.endereco,
                    "Bairro": t.bairro or "",
                    # sub-columns
                    "Jurídico": t.doc_regular + t.ausencia_onus + t.potencial_aprovacao,
                    "Físico":   t.area_dimensoes + t.topografia + t.infraestrutura + t.zoneamento,
                    "Comercial":(t.localizacao + t.estimativa_vgv +
                                 t.demanda_concorrencia + t.adequacao_produto),
                    "Score (%)": t.score,
                    "Selo":      f"SQI {t.selo}"
                })
            df = pd.DataFrame(registros)
            # Ordena colunas na ordem desejada
            df = df[["Data","Endereço","Bairro","Jurídico","Físico","Comercial","Score (%)","Selo"]]
            st.dataframe(df, use_container_width=True)
    finally:
        session.close()
