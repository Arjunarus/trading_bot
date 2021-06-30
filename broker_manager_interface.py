from apscheduler.schedulers.background import BackgroundScheduler


# Общий интерфейс брокер менеджера
class BrokerManagerInterface:
    OPTION_LIST = (
        'AUDCAD', 'AUDJPY', 'AUDUSD', 'EURAUD', 'EURCHF', 'EURJPY', 'GBPAUD', 'GBPJPY', 'NZDJPY', 'USDCAD', 'USDJPY',
        'AUDCHF', 'AUDNZD', 'CADJPY', 'EURCAD', 'EURGBP', 'EURUSD', 'GBPCHF', 'GBPNZD', 'NZDUSD', 'USDCHF', 'CADCHF'
    )
    PROGNOSIS_LIST = ('вверх', 'вниз')

    def __init__(self, result_handler):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.is_deal = False
        self.result_handler = result_handler

    def _get_deal_result(self):
        """
        Вызывается по таймеру, получает результат сделки и передает его в result_handler
        """
        raise NotImplemented('Trying to execute abstract method _get_deal_result')

    def make_deal(self, option, prognosis, summ, deal_time):
        """
        Создает сделку в брокере.
        """
        raise NotImplemented('Trying to execute abstract method make_deal')
