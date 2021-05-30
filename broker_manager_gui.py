import datetime
import json
import logging
import pyautogui
import pyperclip
import pytz
import time

import geometry_2d
import windows_manager
from broker_manager_interface import BrokerManagerInterface

logger = logging.getLogger('pyFinance')


class BrokerManagerGui(BrokerManagerInterface):
    TRY_COUNT = 10

    def __init__(self, result_handler, config_file):
        super().__init__(result_handler)

        with open(config_file, 'r') as cf:
            self.config = json.load(cf)

        self.exp_hour_buttons = geometry_2d.get_matrix(
            m_size=geometry_2d.Vector(x=6, y=4),
            start=geometry_2d.Vector(**self.config['buttons']['expiration_time']['first_hour']),
            delta=geometry_2d.Vector(**self.config['buttons']['expiration_time']['delta'])
        )

        self.exp_minute_buttons = geometry_2d.get_matrix(
            m_size=geometry_2d.Vector(x=3, y=4),
            start=geometry_2d.Vector(**self.config['buttons']['expiration_time']['first_minute']),
            delta=geometry_2d.Vector(**self.config['buttons']['expiration_time']['delta'])
        )

        self.option_buttons = dict(zip(
            BrokerManagerInterface.OPTION_LIST,
            geometry_2d.get_matrix(
                m_size=geometry_2d.Vector(x=11, y=2),
                start=geometry_2d.Vector(**self.config['buttons']['option']['first']),
                delta=geometry_2d.Vector(**self.config['buttons']['option']['delta'])
            )
        ))

        self.prognosis_table = dict(zip(
            BrokerManagerInterface.PROGNOSIS_LIST,
            [
                geometry_2d.Vector(**self.config['buttons']['prognosis']['call']),
                geometry_2d.Vector(**self.config['buttons']['prognosis']['put'])
            ]
        ))

    def _get_deal_result(self):
        self.is_deal = False

        result = ''
        windows_manager.activate_window('Прозрачный брокер бинарных опционов')
        for k in range(BrokerManagerGui.TRY_COUNT):
            pyperclip.copy("")  # <- Это предотвращает замену последней копии текущей копией null.
            pyautogui.doubleClick(self.config['fields']['result']['x'], self.config['fields']['result']['y'])
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.5)  # ctrl-c обычно работает очень быстро, но ваша программа может выполняться быстрее
            result = pyperclip.paste()
            if result in ['LOSE', 'WIN']:
                break
            time.sleep(5)

        # If result not in ['LOSE', 'WIN'] return as is
        self.result_handler(result)

    def check_deal_summ(self, summ):
        pyperclip.copy("")  # <- Это предотвращает замену последней копии текущей копией null.

        pyautogui.doubleClick(
            self.config['fields']['investment_money']['x'],
            self.config['fields']['investment_money']['y'],
            duration=0.1
        )
        time.sleep(0.5)

        pyautogui.rightClick(
            self.config['fields']['investment_money']['x'],
            self.config['fields']['investment_money']['y'],
            duration=0.1
        )
        time.sleep(0.5)

        pyautogui.click(
            self.config['fields']['copy_summ']['x'],
            self.config['fields']['copy_summ']['y'],
            duration=0.1
        )
        time.sleep(0.5)

        actual_summ = int(pyperclip.paste())
        if actual_summ == summ:
            return True
        else:
            return False

    def check_deal_time(self, chtime):
        pyperclip.copy("")  # <- Это предотвращает замену последней копии текущей копией null.

        pyautogui.doubleClick(
            self.config['fields']['expiration_time']['x'],
            self.config['fields']['expiration_time']['y'],
            duration=0.1
        )
        time.sleep(0.5)

        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.5)  # ctrl-c обычно работает очень быстро, но ваша программа может выполняться быстрее

        actual_time = int(pyperclip.paste())
        if actual_time == chtime:
            return True
        else:
            return False

    def make_deal(self, option, prognosis, summ, deal_time):
        if self.is_deal:
            logger.info('Deal is active now, skip new deal.\n')
            return

        windows_manager.activate_window('Прозрачный брокер бинарных опционов')
        pyautogui.click(self.option_buttons[option].x, self.option_buttons[option].y, duration=0.1)
        time.sleep(2)

        for k in range(self.TRY_COUNT):
            pyautogui.doubleClick(
                self.config['fields']['investment_money']['x'],
                self.config['fields']['investment_money']['y'],
                duration=0.1
            )
            time.sleep(1)
            pyautogui.write(str(summ), interval=0.25)
            time.sleep(0.5)
            if self.check_deal_summ(summ):
                logger.debug('Check deal summ True')
                break
            else:
                logger.debug('Check deal summ attempt №{} - False'.format(k))

        for k in range(self.TRY_COUNT):
            pyautogui.doubleClick(
                self.config['fields']['expiration_time']['x'],
                self.config['fields']['expiration_time']['y'],
                duration=0.1
            )
            time.sleep(1)
            pyautogui.write(str(deal_time), interval=0.25)
            time.sleep(0.5)
            if self.check_deal_time(deal_time):
                logger.debug('Check deal time True')
                break
            else:
                logger.debug('Check deal time attempt №{} - False'.format(k))

        pyautogui.click(self.prognosis_table[prognosis].x, self.prognosis_table[prognosis].y, duration=0.1)
        self.is_deal = True

        finish_datetime = datetime.datetime.now() + datetime.timedelta(minutes=deal_time)
        self.scheduler.add_job(self._get_deal_result, 'date', run_date=finish_datetime)
