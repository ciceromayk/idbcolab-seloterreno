from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime

# Base declarativa
Base = declarative_base()

class Terreno(Base):
    __tablename__ = 'terrenos'

    # PK
    id = Column(Integer, primary_key=True, index=True)

    # Dados cadastrais
    descricao_terreno      = Column(String, nullable=False)
    endereco               = Column(String, nullable=False)
    bairro                 = Column(String, nullable=True)
    area_terreno           = Column(Float,  nullable=False)
    altura_maxima          = Column(Float,  nullable=False)
    lencol_freatico_perm   = Column(String, nullable=False)   # sem acento
    nivel_lencol           = Column(Float,  nullable=True)    # sem acento
    permite_outorga        = Column(String, nullable=False)
    responsavel_avaliacao  = Column(String, nullable=False)

    # Sub-pontuações (Jurídicos)
    doc_regular            = Column(Integer, nullable=False)
    ausencia_onus          = Column(Integer, nullable=False)
    potencial_aprovacao    = Column(Integer, nullable=False)

    # Sub-pontuações (Físicos)
    area_dimensoes         = Column(Integer, nullable=False)
    topografia             = Column(Integer, nullable=False)
    infraestrutura         = Column(Integer, nullable=False)
    zoneamento             = Column(Integer, nullable=False)

    # Sub-pontuações (Comerciais)
    localizacao            = Column(Integer, nullable=False)
    estimativa_vgv         = Column(Integer, nullable=False)
    demanda_concorrencia   = Column(Integer, nullable=False)
    adequacao_produto      = Column(Integer, nullable=False)

    # Totais e selo
    score                  = Column(Integer, nullable=False)
    selo                   = Column(String,  nullable=False, index=True)
    data_avaliacao         = Column(DateTime, default=datetime.utcnow, nullable=False)
