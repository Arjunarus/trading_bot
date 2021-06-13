class Error(Exception):
    """Базовый класс для других исключений"""
    pass

class ClickoptionError(Error):
    """Вызывается. когда все проверки выбора опциона прошли неудачно"""
    pass

class ValueSummError(Error):
    """Вызывается, когда введена неверная сумма сделки"""
    pass

class ValueTimeError(Error):
    """Вызывается, когда введено неверное время сделки"""
    pass
