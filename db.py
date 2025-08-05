from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Configuração do banco de dados
DATABASE_URL = "sqlite:///./terrenos.db"  # Ajuste conforme necessário

# Cria o engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Necessário para SQLite
)

# Cria a sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Inicializa o banco de dados, criando todas as tabelas definidas
    """
    Base.metadata.create_all(bind=engine)
