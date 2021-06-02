# В этом файле предполагается реализовать управление брокером через http протокол,
# в отличие от управления через autogui.

import broker_manager_interface


class BrokerManagerHttp(broker_manager_interface.BrokerManagerInterface):

    def __init__(self):
        raise NotImplemented('broker_manager_http is not implemented!')

    def get_deal_result(self):
        raise NotImplemented('broker_manager_http is not implemented!')

    def make_deal(self, option, prognosis, summ, deal_time):
        raise NotImplemented('broker_manager_http is not implemented!')
