from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Terreno(Base):
    __tablename__ = "terrenos"
    
    id = Column(Integer, primary_key=True, index=True)
    data_avaliacao = Column(DateTime, default=datetime.utcnow)
    
    # Dados do Terreno
    descricao = Column(String)  # Descrição do terreno
    endereco = Column(String)    # Endereço do terreno
    area_terreno = Column(Float) # Área do terreno em m²
    altura_maxima = Column(Float) # Altura máxima a construir em metros
    lenol_freatico_permite_subsolo = Column(Boolean) # Permite subsolo? (Sim/Não)
    responsavel = Column(String)  # Responsável pela avaliação
    
    # Critérios Jurídicos (20%)
    doc_regular = Column(Integer)        # Documentação Regular
    ausencia_onus = Column(Integer)      # Ausência de Ônus
    potencial_aprovacao = Column(Integer) # Potencial de Aprovação
    
    # Critérios Físicos (30%)
    area_dimensoes = Column(Integer)     # Área e Dimensões
    topografia = Column(Integer)          # Topografia
    infraestrutura = Column(Integer)      # Infraestrutura Existente
    zoneamento = Column(Integer)          # Zoneamento
    
    # Critérios Comerciais (40%)
    localizacao = Column(Integer)         # Localização
    estimativa_vgv = Column(Integer)      # Estimativa de VGV
    demanda_concorrencia = Column(Integer) # Demanda e Concorrência
    adequacao_produto = Column(Integer)   # Adequação do Produto
    
    # Resultado Final
    score = Column(Integer)                # Pontuação final
    selo = Column(String)                  # Selo de Qualidade (SQI A, B, C, D)
