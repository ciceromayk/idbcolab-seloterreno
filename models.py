from sqlalchemy import Column, Integer, String, Float, DateTime, LargeBinary, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Terreno(Base):
    __tablename__ = "terrenos"
    
    id = Column(Integer, primary_key=True, index=True)
    data_avaliacao = Column(DateTime, default=datetime.utcnow)
    
    # Dados do Terreno
    descricao = Column(String)
    endereco = Column(String)
    street_view_img = Column(LargeBinary)  # Armazena a imagem em formato binário
    area_terreno = Column(Float)
    altura_maxima = Column(Float)
    lenol_freatico_permite_subsolo = Column(Boolean)
    responsavel = Column(String)
    
    # Critérios Jurídicos (20%)
    doc_regular = Column(Integer)
    ausencia_onus = Column(Integer)
    potencial_aprovacao = Column(Integer)
    
    # Critérios Físicos (30%)
    area_dimensoes = Column(Integer)
    topografia = Column(Integer)
    infraestrutura = Column(Integer)
    zoneamento = Column(Integer)
    
    # Critérios Comerciais (40%)
    localizacao = Column(Integer)
    estimativa_vgv = Column(Integer)
    demanda_concorrencia = Column(Integer)
    adequacao_produto = Column(Integer)
    
    # Resultado Final
    score = Column(Integer)
    selo = Column(String)
