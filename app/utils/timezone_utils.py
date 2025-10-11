from datetime import datetime, timezone, timedelta
import pytz

class TimezoneUtils:
    # Timezone padrão do sistema (Brasília)
    BRASILIA_TZ = timezone(timedelta(hours=-3))
    
    @classmethod
    def now(cls) -> datetime:
        """Retorna datetime atual no timezone de Brasília"""
        return datetime.now(cls.BRASILIA_TZ)
    
    @classmethod
    def to_brasilia(cls, dt: datetime) -> datetime:
        """Converte datetime para timezone de Brasília"""
        if dt.tzinfo is None:
            # Se não tem timezone, assume que é UTC
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(cls.BRASILIA_TZ)

    @classmethod
    def ajusta_to_brasilia(cls, dt: str) -> datetime:
        """Recebe a data e ajusta ao datetime para timezone de Brasília"""
        date_format = "%Y-%m-%d %H"
        naive_datetime = datetime.strptime(dt, date_format)
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        datetime_brasilia = brasilia_tz.localize(naive_datetime)
        return datetime_brasilia

    @classmethod
    def to_utc(cls, dt: datetime) -> datetime:
        """Converte datetime para UTC"""
        if dt.tzinfo is None:
            # Se não tem timezone, assume que é Brasília
            dt = dt.replace(tzinfo=cls.BRASILIA_TZ)
        return dt.astimezone(timezone.utc)
    
    @classmethod
    def parse_date_string(cls, date_str: str, format_str: str = "%Y-%m-%d") -> datetime:
        """Parse string para datetime com timezone de Brasília"""
        dt = datetime.strptime(date_str, format_str)
        return dt.replace(tzinfo=cls.BRASILIA_TZ)
    
    @classmethod
    def parse_datetime_string(cls, datetime_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
        """Parse string para datetime com timezone de Brasília"""
        dt = datetime.strptime(datetime_str, format_str)
        return dt.replace(tzinfo=cls.BRASILIA_TZ)
    
    @classmethod
    def create_datetime(cls, year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0) -> datetime:
        """Cria datetime com timezone de Brasília"""
        return datetime(year, month, day, hour, minute, second, tzinfo=cls.BRASILIA_TZ)
    
    @classmethod
    def format_datetime(cls, dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S %z") -> str:
        """Formata datetime sempre mostrando timezone"""
        dt_brasilia = cls.to_brasilia(dt)
        return dt_brasilia.strftime(format_str)
    
    @classmethod
    def start_of_day(cls, date_obj) -> datetime:
        """Retorna início do dia (00:00:00) no timezone de Brasília"""
        if isinstance(date_obj, str):
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d").date()
        elif isinstance(date_obj, datetime):
            date_obj = date_obj.date()
        
        return datetime.combine(date_obj, datetime.min.time()).replace(tzinfo=cls.BRASILIA_TZ)
    
    @classmethod
    def end_of_day(cls, date_obj) -> datetime:
        """Retorna fim do dia (23:59:59) no timezone de Brasília"""
        if isinstance(date_obj, str):
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d").date()
        elif isinstance(date_obj, datetime):
            date_obj = date_obj.date()
        
        return datetime.combine(date_obj, datetime.max.time().replace(microsecond=0)).replace(tzinfo=cls.BRASILIA_TZ)