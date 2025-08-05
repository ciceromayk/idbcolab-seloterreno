from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime

# Criação da base declarativa
Base = declarative_base()

# Modelo Terreno
class Terreno(Base):
    __tablename__ = 'terrenos'

    id = Column(Integer, primary_key=True, index=True)
    doc_regular = Column(Integer)
    ausencia_onus = Column(Integer)
    potencial_aprovacao = Column(Integer)
    area_dimensoes = Column(Integer)
    topografia = Column(Integer)
    infraestrutura = Column(Integer)
    zoneamento = Column(Integer)
    localizacao = Column(Integer)
    estimativa_vgv = Column(Integer)
    demanda_concorrencia = Column(Integer)
    adequacao_produto = Column(Integer)
    score = Column(Integer)
    selo = Column(String, index=True)
    data_avaliacao = Column(DateTime, default=datetime.utcnow)
    
    # Novos campos adicionados
    descricao_terreno = Column(String)
    endereco = Column(String)
    area_terreno = Column(Float)  # Usando Float para permitir números decimais
    altura_maxima = Column(Float)
    lençol_freatico_perm = Column(String)
    nivel_lençol = Column(Float, nullable=True)
    permite_outorga = Column(String)
    responsavel_avaliacao = Column(String)
