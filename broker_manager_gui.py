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
    TRY_COUNT = 3

    def __init__(self, result_handler, config_file):
        super().__init__(result_handler)

        with open(config_file, 'r') as cf:
            self.config = json.load(cf)

        self.exp_hour_buttons = geometry_2d.get_matrix(
            m_size=geometry_2d.Vector({'x': 6, 'y': 4}),
            start=geometry_2d.Vector(self.config['buttons']['expiration_time']['first_hour']),
            delta=geometry_2d.Vector(self.config['buttons']['expiration_time']['delta'])
        )

        self.exp_minute_buttons = geometry_2d.get_matrix(
            m_size=geometry_2d.Vector({'x': 3, 'y': 4}),
            start=geometry_2d.Vector(self.config['buttons']['expiration_time']['first_minute']),
            delta=geometry_2d.Vector(self.config['buttons']['expiration_time']['delta'])
        )

        self.option_buttons = dict(zip(
            BrokerManagerInterface.OPTION_LIST,
            geometry_2d.get_matrix(
                m_size=geometry_2d.Vector({'x': 11, 'y': 2}),
                start=geometry_2d.Vector(self.config['buttons']['option']['first']),
                delta=geometry_2d.Vector(self.config['buttons']['option']['delta'])
            )
        ))

        self.prognosis_table = dict(zip(
            BrokerManagerInterface.PROGNOSIS_LIST,
            [
                geometry_2d.Vector(self.config['buttons']['prognosis']['call']),
                geometry_2d.Vector(self.config['buttons']['prognosis']['put'])
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
            time.sleep(1)  # ctrl-c обычно работает очень быстро, но ваша программа может выполняться быстрее
            result = pyperclip.paste()
            if result in ['LOSE', 'WIN']:
                break
            time.sleep(5)

        # If result not in ['LOSE', 'WIN'] return as is
        self.result_handler(result)

    def make_deal(self, option, prognosis, summ, deal_time):
        if self.is_deal:
            logger.info('Deal is active now, skip new deal.')
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
            time.sleep(1)

        pyautogui.click(
            self.config['fields']['expiration_time']['x'],
            self.config['fields']['expiration_time']['y'],
            duration=0.1
        )
        time.sleep(2)
        pyautogui.click(self.exp_hour_buttons[deal_time.hour].x, self.exp_hour_buttons[deal_time.hour].y, duration=0.1)
        time.sleep(2)
        pyautogui.click(
            self.exp_minute_buttons[deal_time.minute // 5].x,
            self.exp_minute_buttons[deal_time.minute // 5].y,
            duration=0.1
        )
        time.sleep(2)
        pyautogui.click(self.prognosis_table[prognosis].x, self.prognosis_table[prognosis].y, duration=0.1)
        self.is_deal = True

        # Set up timer on finish job
        msk_tz = pytz.timezone('Europe/Moscow')
        now_date = datetime.datetime.now(msk_tz)
        finish_datetime = msk_tz.localize(
            datetime.datetime(
                now_date.year,
                now_date.month,
                now_date.day,
                deal_time.hour,
                deal_time.minute
            )
        )
        if deal_time.hour in [0, 1]:
            finish_datetime += datetime.timedelta(days=1)
        finish_datetime = finish_datetime.astimezone()

        logger.debug("finish_datetime={}".format(finish_datetime))

        self.scheduler.add_job(self._get_deal_result, 'date', run_date=finish_datetime)
