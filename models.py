from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime

Base = declarative_base()

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
    descricao_terreno = Column(String)
    endereco = Column(String)
    bairro = Column(String)
    area_terreno = Column(Float)
    altura_maxima = Column(Float)
    lencol_freatico_perm = Column(String)
    nivel_lencol = Column(Float, nullable=True)
    permite_outorga = Column(String)
    responsavel_avaliacao = Column(String)
