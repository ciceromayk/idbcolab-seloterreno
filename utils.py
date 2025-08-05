def calcular_pontuacao(doc_regular, ausencia_onus, potencial_aprovacao,
                       area_dimensoes, topografia, infraestrutura, zoneamento,
                       localizacao, estimativa_vgv, demanda_concorrencia,
                       adequacao_produto):
    """Calcula a pontuação total com base nos critérios."""
    total = (
        (doc_regular + ausencia_onus + potencial_aprovacao) +
        (area_dimensoes + topografia + infraestrutura + zoneamento) +
        (localizacao + estimativa_vgv + demanda_concorrencia) +
        (adequacao_produto)
    )
    return total

def definir_selo(total):
    """Define o selo de qualidade com base na pontuação."""
    if total >= 80:
        return "SQI A (Excelente)"
    elif total >= 60:
        return "SQI B (Bom)"
    elif total >= 40:
        return "SQI C (Médio)"
    else:
        return "SQI D (Atenção)"
