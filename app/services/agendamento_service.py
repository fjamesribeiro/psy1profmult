from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from fastapi import HTTPException
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from app import models, schemas
from app.utils.timezone_utils import TimezoneUtils


class AgendamentoService:
    DURACAO_SLOT_MIN = 60
    TZ_OFFSET = "-03:00"

    @staticmethod
    def _get_horarios_profissional(db: Session, profissional_id: int) -> Dict:
        """Busca os horários de trabalho do profissional"""
        profissional = db.query(models.Profissional).filter(
            models.Profissional.id == profissional_id,
            models.Profissional.ativo == True
        ).first()

        if not profissional:
            raise HTTPException(status_code=404, detail="Profissional não encontrado ou inativo")

        # Converte as chaves do JSON de string para int
        horarios = {}
        for dia_str, janelas in profissional.dias_trabalho.items():
            horarios[int(dia_str)] = [(inicio, fim) for inicio, fim in janelas]

        return horarios

    @staticmethod
    def _get_duracao_profissional(db: Session, profissional_id: int) -> int:
        """Busca a duração padrão de consulta do profissional"""
        profissional = db.query(models.Profissional).filter(
            models.Profissional.id == profissional_id
        ).first()

        if not profissional:
            return AgendamentoService.DURACAO_SLOT_MIN

        return profissional.duracao_padrao_minutos or AgendamentoService.DURACAO_SLOT_MIN

    @staticmethod
    def create_agendamento(db: Session, profissional_id: int,
                           agendamento: schemas.AgendamentoCreate) -> models.Agendamento:
        # Verifica se profissional existe e está ativo
        profissional = db.query(models.Profissional).filter(
            models.Profissional.id == profissional_id,
            models.Profissional.ativo == True
        ).first()
        if not profissional:
            raise HTTPException(status_code=404, detail="Profissional não encontrado ou inativo")

        # Verifica se cliente existe e pertence ao profissional
        cliente = db.query(models.Cliente).filter(
            models.Cliente.id == agendamento.cliente_id,
            models.Cliente.profissional_id == profissional_id
        ).first()
        if not cliente:
            raise HTTPException(status_code=400, detail="Cliente não encontrado ou não pertence ao profissional")

        # Valida se data_fim é posterior a data_inicio
        if agendamento.data_fim and agendamento.data_fim <= agendamento.data_inicio:
            raise HTTPException(status_code=400, detail="Data fim deve ser posterior à data início")

        try:
            # Cria o agendamento incluindo o profissional_id
            agendamento_data = agendamento.model_dump()
            agendamento_data['profissional_id'] = profissional_id

            db_agendamento = models.Agendamento(**agendamento_data)
            db.add(db_agendamento)
            db.commit()
            db.refresh(db_agendamento)
            return db_agendamento
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Evento ID já existe")

    @staticmethod
    def get_agendamentos(db: Session, profissional_id: int, skip: int = 0, limit: int = 100) -> List[
        models.Agendamento]:
        return db.query(models.Agendamento).filter(
            models.Agendamento.profissional_id == profissional_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_agendamento_by_id(db: Session, profissional_id: int, agendamento_id: int) -> models.Agendamento:
        agendamento = db.query(models.Agendamento).filter(
            models.Agendamento.id == agendamento_id,
            models.Agendamento.profissional_id == profissional_id
        ).first()
        if not agendamento:
            raise HTTPException(status_code=404, detail="Agendamento não encontrado")
        return agendamento

    @staticmethod
    def get_agendamentos_by_data(db: Session, profissional_id: int, data: str) -> List[models.Agendamento]:
        try:
            data_obj = datetime.strptime(data, "%Y-%m-%d").date()
            return db.query(models.Agendamento).filter(
                models.Agendamento.profissional_id == profissional_id,
                func.date(models.Agendamento.data_inicio) == data_obj
            ).all()
        except ValueError:
            raise HTTPException(status_code=400, detail="Data deve estar no formato yyyy-mm-dd")

    @staticmethod
    def get_agendamentos_by_cliente(db: Session, profissional_id: int, cliente_id: int) -> List[models.Agendamento]:
        # Verifica se cliente existe e pertence ao profissional
        cliente = db.query(models.Cliente).filter(
            models.Cliente.id == cliente_id,
            models.Cliente.profissional_id == profissional_id
        ).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")

        return db.query(models.Agendamento).filter(
            models.Agendamento.cliente_id == cliente_id,
            models.Agendamento.profissional_id == profissional_id
        ).all()

    @staticmethod
    def update_agendamento(db: Session, profissional_id: int, agendamento_id: int,
                           agendamento: schemas.AgendamentoUpdate) -> models.Agendamento:
        db_agendamento = AgendamentoService.get_agendamento_by_id(db, profissional_id, agendamento_id)

        update_data = agendamento.model_dump(exclude_unset=True)

        # Valida cliente_id se estiver sendo alterado
        if "cliente_id" in update_data:
            cliente = db.query(models.Cliente).filter(
                models.Cliente.id == update_data["cliente_id"],
                models.Cliente.profissional_id == profissional_id
            ).first()
            if not cliente:
                raise HTTPException(status_code=400, detail="Cliente não encontrado")

        # Valida datas se estiverem sendo alteradas
        data_inicio = update_data.get("data_inicio", db_agendamento.data_inicio)
        data_fim = update_data.get("data_fim", db_agendamento.data_fim)
        if data_fim and data_fim <= data_inicio:
            raise HTTPException(status_code=400, detail="Data fim deve ser posterior à data início")

        # Aplica as alterações
        for key, value in update_data.items():
            setattr(db_agendamento, key, value)

        try:
            db.commit()
            db.refresh(db_agendamento)
            return db_agendamento
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Evento ID já existe")

    @staticmethod
    def cancel_agendamento(db: Session, profissional_id: int, agendamento_id: int) -> models.Agendamento:
        db_agendamento = AgendamentoService.get_agendamento_by_id(db, profissional_id, agendamento_id)

        if db_agendamento.status == "canceled":
            raise HTTPException(status_code=400, detail="Agendamento já cancelado")

        db_agendamento.status = "canceled"
        db_agendamento.canceled_at = datetime.utcnow()
        db.commit()
        db.refresh(db_agendamento)
        return db_agendamento

    @staticmethod
    def delete_agendamento(db: Session, profissional_id: int, agendamento_id: int):
        db_agendamento = AgendamentoService.get_agendamento_by_id(db, profissional_id, agendamento_id)
        db.delete(db_agendamento)
        db.commit()

    # === MÉTODOS PARA SLOTS LIVRES ===

    @staticmethod
    def _parse_time(time_str: str) -> Tuple[int, int]:
        """Converte 'HH:MM' para (horas, minutos)"""
        h, m = map(int, time_str.split(':'))
        return h, m

    @staticmethod
    def _create_datetime_with_tz(date_str: str, time_str: str) -> datetime:
        """Cria datetime com timezone padrão do sistema"""
        h, m = AgendamentoService._parse_time(time_str)
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        return TimezoneUtils.create_datetime(
            date_obj.year, date_obj.month, date_obj.day, h, m
        )

    @staticmethod
    def _slots_overlap(slot1: Dict, slot2: Dict) -> bool:
        """Verifica se dois slots se sobrepõem"""
        return slot1['inicio'] < slot2['fim'] and slot1['fim'] > slot2['inicio']

    @staticmethod
    def _gerar_slots_do_dia(data: str, horarios: Dict, duracao_min: int) -> List[Dict]:
        """Gera todos os slots possíveis do dia baseado nos horários de funcionamento"""
        try:
            data_obj = datetime.strptime(data, "%Y-%m-%d").date()
        except ValueError:
            return []

        # Dia da semana (1=segunda, 7=domingo)
        weekday = data_obj.weekday() + 1

        janelas = horarios.get(weekday, [])
        if not janelas:
            return []

        slots = []
        duracao_delta = timedelta(minutes=duracao_min)

        for inicio_str, fim_str in janelas:
            inicio_dt = AgendamentoService._create_datetime_with_tz(data, inicio_str)
            fim_dt = AgendamentoService._create_datetime_with_tz(data, fim_str)

            slot_inicio = inicio_dt
            while slot_inicio + duracao_delta <= fim_dt:
                slot_fim = slot_inicio + duracao_delta
                slots.append({
                    'inicio': slot_inicio,
                    'fim': slot_fim
                })
                slot_inicio = slot_fim

        return slots

    @staticmethod
    def _filtrar_slots_ocupados(slots_todos: List[Dict], agendamentos_ocupados: List[Dict]) -> List[Dict]:
        """Remove slots que se sobrepõem com agendamentos existentes"""
        slots_livres = []

        for slot in slots_todos:
            ocupado = False
            for agendamento in agendamentos_ocupados:
                if AgendamentoService._slots_overlap(slot, agendamento):
                    ocupado = True
                    break

            if not ocupado:
                slots_livres.append(slot)

        return slots_livres

    @staticmethod
    def _filtrar_slots_passados(slots: List[Dict]) -> List[Dict]:
        """Remove slots que já passaram"""
        agora = TimezoneUtils.now()
        return [slot for slot in slots if slot['inicio'] >= agora]

    @staticmethod
    def get_slots_livres(db: Session, profissional_id: int, data: str) -> Dict:
        """Retorna slots livres para uma data específica de um profissional"""
        try:
            # Valida formato da data
            data_obj = datetime.strptime(data, "%Y-%m-%d").date()
            hoje = TimezoneUtils.now().date()

            # Não permite datas passadas
            if data_obj < hoje:
                return {
                    "data": data,
                    "slots_disponiveis": [],
                    "total_slots": {"gerados": 0, "livres": 0}
                }

            # Busca horários e duração do profissional
            horarios = AgendamentoService._get_horarios_profissional(db, profissional_id)
            duracao = AgendamentoService._get_duracao_profissional(db, profissional_id)

            # Gera todos os slots possíveis do dia
            slots_todos = AgendamentoService._gerar_slots_do_dia(data, horarios, duracao)

            # Busca agendamentos ocupados do dia
            inicio_dia = TimezoneUtils.start_of_day(data)
            fim_dia = TimezoneUtils.end_of_day(data)

            agendamentos_db = db.query(models.Agendamento).filter(
                models.Agendamento.profissional_id == profissional_id,
                models.Agendamento.data_inicio >= inicio_dia,
                models.Agendamento.data_inicio <= fim_dia,
                models.Agendamento.status != 'canceled'
            ).all()

            # Converte agendamentos para formato de slots ocupados
            agendamentos_ocupados = []
            for ag in agendamentos_db:
                if ag.data_inicio and ag.data_fim:
                    inicio = TimezoneUtils.to_brasilia(ag.data_inicio)
                    fim = TimezoneUtils.to_brasilia(ag.data_fim)
                    agendamentos_ocupados.append({
                        'inicio': inicio,
                        'fim': fim
                    })

            # Filtra slots ocupados
            slots_livres = AgendamentoService._filtrar_slots_ocupados(slots_todos, agendamentos_ocupados)

            # Remove slots que já passaram (se for hoje)
            if data_obj == hoje:
                slots_livres = AgendamentoService._filtrar_slots_passados(slots_livres)

            # Formata resposta
            slots_formatados = []
            for slot in slots_livres:
                slots_formatados.append({
                    "inicio": slot['inicio'].isoformat(),
                    "fim": slot['fim'].isoformat()
                })

            return {
                "data": data,
                "slots_disponiveis": slots_formatados,
                "total_slots": {
                    "gerados": len(slots_todos),
                    "livres": len(slots_livres)
                }
            }

        except ValueError:
            raise HTTPException(status_code=400, detail="Data deve estar no formato YYYY-MM-DD")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

    @staticmethod
    def is_horario_livre(db: Session, profissional_id: int, data: str) -> bool:
        """Verifica se um horário específico está disponível para agendamento"""
        try:
            # Parse do input e cálculo do slot de tempo
            horario_inicio = TimezoneUtils.ajusta_to_brasilia(data)

            # Busca duração do profissional
            duracao_min = AgendamentoService._get_duracao_profissional(db, profissional_id)
            duracao = timedelta(minutes=duracao_min)
            horario_fim = horario_inicio + duracao

            # Valida se o horário não está no passado
            if horario_inicio < TimezoneUtils.now():
                return False

            # Valida se o horário está dentro do expediente do profissional
            dia_semana = horario_inicio.weekday() + 1
            horarios = AgendamentoService._get_horarios_profissional(db, profissional_id)
            janelas_expediente = horarios.get(dia_semana, [])

            if not janelas_expediente:
                return False

            dentro_do_expediente = False
            data_str = horario_inicio.strftime("%Y-%m-%d")
            for inicio_exp_str, fim_exp_str in janelas_expediente:
                inicio_exp = AgendamentoService._create_datetime_with_tz(data_str, inicio_exp_str)
                fim_exp = AgendamentoService._create_datetime_with_tz(data_str, fim_exp_str)

                if inicio_exp <= horario_inicio and horario_fim <= fim_exp:
                    dentro_do_expediente = True
                    break

            if not dentro_do_expediente:
                return False

            # Valida se não existe agendamento conflitante
            conflito = db.query(models.Agendamento).filter(
                models.Agendamento.profissional_id == profissional_id,
                models.Agendamento.status != 'canceled',
                models.Agendamento.data_inicio < horario_fim,
                models.Agendamento.data_fim > horario_inicio
            ).first()

            if conflito:
                return False

            return True

        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Data deve estar no formato ISO 8601")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

    @staticmethod
    def proximo_estado(db: Session, estado_atual: str,  profissional_id: int) -> str:
        """Retorna o próximo estado na sequência do fluxo de agendamento"""
        profissional = db.query(models.Profissional).filter(
            models.Profissional.id == profissional_id
        ).first()

        atende_online = profissional.atende_online

        transicoes = {
            # Fluxo de Agendamento
            'AGENDAR_INICIO': 'AGENDAR_AGUARDANDO_DATA',
            'AGENDAR_AGUARDANDO_DATA': {
                True : 'AGENDAR_AGUARDANDO_CONFIRMACAO_ONLINE',
                False : 'AGENDAR_AGUARDANDO_CONFIRMACAO'
            },
            'AGENDAR_AGUARDANDO_CONFIRMACAO_ONLINE': 'AGENDAR_CONFIRMANDO_ONLINE',
            'AGENDAR_CONFIRMANDO_ONLINE' : 'AGENDAR_AGUARDANDO_CONFIRMACAO',
            'AGENDAR_AGUARDANDO_CONFIRMACAO': 'INICIO',

            # Fluxo de Reagendamento
            'REAGENDAR_LISTANDO': 'REAGENDAR_AGUARDANDO_ESCOLHA',
            'REAGENDAR_AGUARDANDO_ESCOLHA': 'REAGENDAR_AGUARDANDO_DATA',
            'REAGENDAR_AGUARDANDO_DATA': {
                True: 'REAGENDAR_AGUARDANDO_CONFIRMACAO_ONLINE',
                False: 'REAGENDAR_AGUARDANDO_CONFIRMACAO'
            },
            'REAGENDAR_AGUARDANDO_CONFIRMACAO_ONLINE': 'REAGENDAR_CONFIRMANDO_ONLINE',
            'REAGENDAR_CONFIRMANDO_ONLINE' : 'REAGENDAR_AGUARDANDO_CONFIRMACAO',
            'REAGENDAR_AGUARDANDO_CONFIRMACAO': 'INICIO',

            # Fluxo de Cancelamento
            'CANCELAR_LISTANDO': 'CANCELAR_AGUARDANDO_ESCOLHA',
            'CANCELAR_AGUARDANDO_ESCOLHA': 'CANCELAR_AGUARDANDO_CONFIRMACAO',
            'CANCELAR_AGUARDANDO_CONFIRMACAO': 'INICIO',
        }

        var_estado_atual = estado_atual.strip().upper()
        transicao = transicoes.get(var_estado_atual)

        # Se for um dicionário com condição, avalia e retorna o estado apropriado
        if isinstance(transicao, dict):
            return transicao[atende_online]

        # Se for um estado simples, retorna direto
        return transicao