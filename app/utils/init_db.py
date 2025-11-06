# Importa o engine e a Base do seu módulo database
# Pelo seu screenshot, eles estão em app/database.py
# Importa TODOS os seus modelos para que eles sejam registrados no metadata da Base
# Pela imagem, você tem 'Profissional' e 'Cliente'.
# Adicione qualquer outro modelo que você tenha.
# Se você tiver mais modelos em outros arquivos (ex: agendamentos.py),
# importe-os aqui também para que o SQLAlchemy saiba deles.

from app.database import engine, Base
from app.models import Agendamento, EstadoConversa, Cliente, Profissional

print("Iniciando a criação das tabelas no banco de dados...")

try:
    # Cria todas as tabelas (definidas em Base.metadata) no banco de dados
    # Isso irá checar quais tabelas não existem e criá-las.
    Base.metadata.create_all(bind=engine)

    print("Tabelas criadas com sucesso!")

except Exception as e:
    print(f"Ocorreu um erro ao criar as tabelas: {e}")