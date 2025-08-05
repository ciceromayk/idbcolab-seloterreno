from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Terreno(Base):
    __tablename__ = "terrenos"
    
    id = Column(Integer, primary_key=True, index=True)
    data_avaliacao = Column(DateTime, default=datetime.utcnow)
    # Critérios Jurídicos
    doc_regular = Column(Integer)
    ausencia_onus = Column(Integer)
    potencial_aprovacao = Column(Integer)
    # Critérios Físicos
    area_dimensoes = Column(Integer)
    topografia = Column(Integer)
    infraestrutura = Column(Integer)
    zoneamento = Column(Integer)
    # Critérios Comerciais
    localizacao = Column(Integer)
    estimativa_vgv = Column(Integer)
    demanda_concorrencia = Column(Integer)
    # Alinhamento com o Produto
    adequacao_produto = Column(Integer)
    # Resultado final
    score = Column(Integer)  # Nota final (0 a 100)
    selo = Column(String)    # SQI A, SQI B, etc.
