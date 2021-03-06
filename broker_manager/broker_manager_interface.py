# Общий интерфейс брокер менеджера
class BrokerManagerInterface:
    OPTION_LIST = (
        'AUDCAD', 'AUDJPY', 'AUDUSD', 'EURAUD', 'EURCHF', 'EURJPY', 'GBPAUD', 'GBPJPY', 'NZDJPY', 'USDCAD', 'USDJPY',
        'AUDCHF', 'AUDNZD', 'CADJPY', 'EURCAD', 'EURGBP', 'EURUSD', 'GBPCHF', 'GBPNZD', 'NZDUSD', 'USDCHF'
    )
    PROGNOSIS_LIST = ('вверх', 'вниз')

    def get_deal_result(self):
        """
        Получает результат сделки
        """
        raise NotImplemented('Trying to execute abstract method get_deal_result')

    def make_deal(self, option, prognosis, summ, deal_time):
        """
        Создает сделку в брокере.
        """
        raise NotImplemented('Trying to execute abstract method make_deal')
