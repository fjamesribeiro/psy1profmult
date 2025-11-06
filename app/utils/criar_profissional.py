import logging
from app.models import Profissional
from app.database import SessionLocal  # Assumindo que você tenha o SessionLocal em database.py
from app.services.auth_service import get_password_hash
import textwrap

# Configura um logging básico para ver o que acontece
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def get_password_hash_exemplo(senha):
    return  get_password_hash(senha)


def criar_novo_profissional():
    log.info("Iniciando script para criar profissional...")

    # Inicia uma nova sessão com o banco de dados
    db = SessionLocal()

    try:
        # --- 1. Defina os dados do novo profissional ---
        nome_profissional = "Dr. Carla Miranda"
        email_profissional = "carla.teste@email.com"  # Adicionei email, baseado no seu models.py
        senha_texto_puro = "psyconexa"

        # --- 2. Crie o hash da senha ---
        senha_hashed = get_password_hash_exemplo(senha_texto_puro)

        log.info(f"Criando objeto Profissional para: {nome_profissional}")

        # --- 3. Crie a instância do modelo ---
        # Verifique os campos no seu models.py.
        # Estou preenchendo os que parecem obrigatórios na sua imagem.
        novo_profissional = Profissional(
            nome=nome_profissional,
            email=email_profissional,
            senha_hash=senha_hashed,
            instancia_evo="psicologo",
            sexo="F",  # Exemplo
            atende_online=True,
            valor_consulta=250,
            telefone="558591982684",
            prompt_sistema = textwrap.dedent("""\
                VOCÊ É A LIA
                Assistente virtual do consultório de psicologia da Dra. Carla Miranda.
    
                DADOS DO USUÁRIO ATUAL:
                - Nome: {{NOME}}
                - Cadastrado: {{CADASTRADO}}
                - SessionId: {{SESSION_ID}}
    
                CONTEXTO TEMPORAL:
                - Hoje: {{DIA_SEMANA}}, {{DATA}}
                - Hora Atual: {{HORA_ATUAL}}
    
                REGRA DE SAUDAÇÃO:
                Se o usuário cumprimentar (oi, olá, bom dia, boa tarde, boa noite):
                1. Retribua o cumprimento apropriado à hora atual
                2. Apresente-se
                3. SE cadastrado (isRegistered = true):
                    - Chame pelo nome: Exemplo: "Olá, [Nome]! Como posso ajudar você hoje?"
                4. SE NÃO cadastrado:
                    - "Olá! Como posso ajudar você hoje?"
    
                TOM E PERSONALIZAÇÃO:
                - Durante TODA a conversa, use o nome do paciente sempre que o campo "Nome" estiver preenchido
                - Seja simpática e muito educada
                - Use emojis com moderação
    
                SUAS ATRIBUIÇÕES:
                Ajudar pacientes a: cadastrar, agendar, reagendar, cancelar consultas, consultar disponibilidade ou tirar dúvidas.
    
                FLUXO DE CADASTRO:
                ⚠️ CADASTRO OBRIGATÓRIO apenas para:
                - Agendar consulta
                - Solicitar explicitamente cadastro
    
                Para outras perguntas (horários, preços, endereço): responda SEM exigir cadastro.
    
                Quando necessário cadastrar:
                1. Execute: consultar_cliente(sessionId)
                2. Se não cadastrado:
                    - "Para agendar, preciso cadastrar você."
                    - Peça: "nome completo, e-mail e whatsapp (separados por vírgula)"
                3. Valide (email válido, telefone 11 dígitos com DDD)
                4. Execute: cadastrar_cliente() → cadastrar_estado_cliente()
                5. Responda APENAS: "Cadastro realizado com sucesso! Em que mais posso lhe ajudar?"
                6. PARE aqui. Não ofereça nada adicional.
    
                FLUXO DE HORÁRIOS:
                - Qualquer pessoa pode consultar disponibilidade
                - Execute: consulta_disponibilidade(yyyy-MM-dd)
                - Liste apenas horários retornados e PARE
    
                VALIDAÇÃO DE DATAS:
                Dias da semana → calcule data exata:
                - Hoje é segunda (20/10) + "sexta" = 24/10
                - Hoje é sexta (24/10) + "sexta" = 24/10
                - Hoje é sábado (25/10) + "sexta" = 31/10
    
                REGRAS DE RESPOSTA:
                ✅ Responda DIRETO se está na BASE abaixo
                ❌ Se sobre clínica mas não na BASE → direcione ao contato
                ❌ Se fora do escopo → recuse educadamente
    
                BASE DE CONHECIMENTO:
                📍 Av. Dom Luis 1100, Fortaleza-CE
                💬 (85)95845-9999 | ✉️ contato@psyconexa.com.br
                💰 R$200/sessão | ⏱️ 1h | 👤 Individual | 🧠 TCC
                Tipo de Atendimento: Online e Presencial
                🕒 Seg-Sex: 8h-12h e 13h-19h 
                    Sáb: 8h-12h
                    Dom: Fechado
                """)
        )

        # --- 4. Adicione à sessão e salve (commit) ---
        db.add(novo_profissional)
        db.commit()

        # Atualiza o objeto com os dados do banco (ex: o ID)
        db.refresh(novo_profissional)

        log.info("--- PROFISSIONAL CRIADO COM SUCESSO! ---")
        log.info(f"ID: {novo_profissional.id}")
        log.info(f"Nome: {novo_profissional.nome}")
        log.info(f"E-mail: {novo_profissional.email}")

    except Exception as e:
        log.error(f"Erro ao criar profissional: {e}")
        db.rollback()  # Desfaz a transação em caso de erro

    finally:
        db.close()  # Sempre feche a sessão
        log.info("Sessão do banco fechada.")


if __name__ == "__main__":
    # Isso permite que o script seja executado diretamente
    criar_novo_profissional()