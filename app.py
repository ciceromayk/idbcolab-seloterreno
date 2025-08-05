import streamlit as st
import plotly.graph_objects as go

# ========== CSS para as caixas estilizadas ==========
st.markdown("""
<style>
.resumo {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  margin-top: 30px;
  font-family: Arial, sans-serif;
}
.resumo-box {
  background-color: #ffe6e6;
  border-radius: 10px;
  padding: 20px;
  margin: 10px;
  flex: 1 1 220px;
  max-width: 220px;
  text-align: center;
  box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
}
.resumo-box h4 {
  margin-top: 0;
  margin-bottom: 10px;
}
.valor {
  font-size: 36px;
  font-weight: bold;
  margin: 10px 0;
}
.valor-final {
  font-size: 40px;
  font-weight: bold;
  margin: 10px 0;
  color: #0247fe;
}
.pequeno {
  font-size: 14px;
  margin-top: 5px;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="IDBCOLAB - COMITÊ DE PRODUTO", layout="wide")

st.title("CADASTRO E AVALIAÇÃO DE TERRENO")

# ---- DADOS ----
with st.expander("CRITÉRIOS JURÍDICOS", expanded=False):
    doc_regular = st.slider("Documentação Regular (0 a 5)", 0, 5, 3)
    ausencia_onus = st.slider("Ausência de Ônus (0 a 5)", 0, 5, 3)
    potencial_aprovacao = st.slider("Potencial de Aprovação (0 a 10)", 0, 10, 6)

with st.expander("CRITÉRIOS FÍSICOS", expanded=False):
    area_dimensoes = st.slider("Área e Dimensões (0 a 10)", 0, 10, 7)
    topografia = st.slider("Topografia (0 a 5)", 0, 5, 3)
    infraestrutura = st.slider("Infraestrutura Existente (0 a 5)", 0, 5, 3)
    zoneamento = st.slider("Zoneamento (0 a 10)", 0, 10, 7)

with st.expander("CRITÉRIOS COMERCIAIS", expanded=False):
    localizacao = st.slider("Localização (0 a 15)", 0, 15, 10)
    estimativa_vgv = st.slider("Estimativa de VGV (0 a 15)", 0, 15, 10)
    demanda_concorrencia = st.slider("Demanda e Concorrência (0 a 10)", 0, 10, 5)
    adequacao_produto = st.slider("Adequação do Produto (0 a 10)", 0, 10, 7)

# Button
if st.button("Avaliar Terreno"):

    # --- Calculando Somatórios ---
    juridico_total = doc_regular + ausencia_onus + potencial_aprovacao       # Máximo 20
    fisico_total = area_dimensoes + topografia + infraestrutura + zoneamento # Máximo 30
    comercial_total = localizacao + estimativa_vgv + demanda_concorrencia + adequacao_produto # Máx 50?

    # Se seu "total" for o somatório puro, use abaixo
    nota_final = juridico_total + fisico_total + comercial_total

    # Simulação de selo (coloque sua lógica real!)
    if nota_final >= 70:
        selo = "Selo A (Excelente)"
    elif nota_final >= 50:
        selo = "Selo B (Bom)"
    else:
        selo = "Selo C (Médio)"

    # ---- RESUMO ESTILIZADO ----
    resumo_html = f"""
    <div class='resumo'>
        <div class='resumo-box'>
            <h4>Critérios Jurídicos</h4>
            <div class='valor' style='color:red;'>{juridico_total}</div>
            <div class='pequeno'>Pontuação: 20</div>
        </div>
        <div class='resumo-box'>
            <h4>Critérios Físicos</h4>
            <div class='valor' style='color:red;'>{fisico_total}</div>
            <div class='pequeno'>Pontuação: 30</div>
        </div>
        <div class='resumo-box'>
            <h4>Critérios Comerciais</h4>
            <div class='valor' style='color:red;'>{comercial_total}</div>
            <div class='pequeno'>Pontuação: 50</div>
        </div>
        <div class='resumo-box'>
            <h4>Nota Final</h4>
            <div class='valor-final'>{nota_final}</div>
            <div class='pequeno'>Selo: {selo}</div>
        </div>
    </div>
    """
    st.markdown(resumo_html, unsafe_allow_html=True)

    # --- GRÁFICO RADAR ---
    # Normalizando cada total p/ radar (0 a 100)
    juridico_perc = (juridico_total / 20) * 100
    fisico_perc = (fisico_total / 30) * 100
    comercial_perc = (comercial_total / 50) * 100

    categorias = ['Jurídicos', 'Físicos', 'Comerciais']
    valores = [juridico_perc, fisico_perc, comercial_perc]
    valores += [valores[0]] # Para fechar o radar
    labels = [f"{cat}: {val:.1f}%" for cat, val in zip(categorias, valores[:-1])]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=valores,
        theta=categorias + [categorias[0]],
        fill='toself',
        text=labels + [""],
        mode='lines+markers+text',
        textposition='top center',
        hoverinfo='text'
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
