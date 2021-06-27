import datetime
import json
import logging
import pyautogui
import pyperclip
import time

import geometry_2d
import windows_manager
from broker_manager_interface import BrokerManagerInterface

logger = logging.getLogger('pyFinance')


def repeater(action):
    def repeat_action(*args, **kvargs):
        tries = 5
        for k in range(tries):
            if action(*args, **kvargs):
                logger.debug('Check {} - True'.format(action.__name__))
                return
            logger.debug('Check {} - False'.format(action.__name__))
        # при всех неудачных попытках кидаем исключение об ошибке
        raise RuntimeError('{} setting error'.format(action.__name__))
    return repeat_action


class BrokerManagerGui(BrokerManagerInterface):
    TRY_COUNT = 5

    def __init__(self, result_handler, config_file):
        super().__init__(result_handler)

        with open(config_file, 'r') as cf:
            self.config = json.load(cf)

        self.interval_deal_time = None

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

        # Устанавливаем начальный опцион
        self.current_option = None
        try:
            self.click_option('EURUSD')
        except:
            pass
        self.option_buttons['CADCHF'] = self.option_buttons['CADJPY']

    def _get_deal_result(self):
        self.is_deal = False

        result = ''
        windows_manager.activate_window('Прозрачный брокер бинарных опционов')

        # открываем графу сделок "открытые"
        pyautogui.doubleClick(
            self.config['buttons']['opened']['x'],
            self.config['buttons']['opened']['y'],
            duration=0.1
        )
        time.sleep(5)

        for k in range(BrokerManagerGui.TRY_COUNT):
            result = self.get_field('result')
            if result in ['LOSE', 'WIN']:
                break
            time.sleep(5)

        # If result not in ['LOSE', 'WIN'] return as is
        self.result_handler(result)

    def set_field(self, field, value):
        pyautogui.doubleClick(
            self.config['fields'][field]['x'],
            self.config['fields'][field]['y'],
            duration=0.1
        )
        time.sleep(0.5)
        pyautogui.write(str(value), interval=0.25)
        time.sleep(0.5)

    def get_field(self, field, use_mouse=False):
        pyperclip.copy("")  # <- Это предотвращает замену последней копии текущей копией null.

        pyautogui.doubleClick(
            self.config['fields'][field]['x'],
            self.config['fields'][field]['y'],
            duration=0.1
        )
        time.sleep(0.5)

        if use_mouse:
            pyautogui.rightClick(
                self.config['fields'][field]['x'],
                self.config['fields'][field]['y'],
                duration=0.1
            )
            time.sleep(0.5)

            pyautogui.click(
                self.config['fields'][field]['x'] + self.config['context_menu']['copy']['x'],
                self.config['fields'][field]['y'] + self.config['context_menu']['copy']['y'],
                duration=0.1
            )
        else:
            # ctrl-c обычно работает очень быстро, но ваша программа может выполняться быстрее
            pyautogui.hotkey('ctrl', 'c')

        time.sleep(0.5)
        return pyperclip.paste()

    def try_set_field(self, field, value, use_mouse=False):
        self.set_field(field, value)
        return self.get_field(field, use_mouse) == str(value)

    def set_expiration_time(self, finish_datetime):
        self.interval_deal_time = int((finish_datetime - datetime.datetime.now()).total_seconds() // 60)
        return self.try_set_field('expiration_time', self.interval_deal_time)

    def click_option(self, option):
        def click_option_button(point, screenshot):
            pyautogui.click(point.x, point.y, duration=0.1)
            time.sleep(3)
            screenshot_new = pyautogui.screenshot(region=(point.x - 5, point.y - 5, point.x + 5, point.y + 5))
            if screenshot == screenshot_new:
                return False
            self.current_option = option
            return True

        if self.current_option == option:
            return

        point = self.option_buttons[option]
        screenshot = pyautogui.screenshot(region=(point.x - 5, point.y - 5, point.x + 5, point.y + 5))

        repeater(click_option_button)(point, screenshot)


    def make_deal(self, option, prognosis, summ, deal_time):
        if self.is_deal:
            logger.info('Deal is active now, skip new deal.\n')
            return

        windows_manager.activate_window('Прозрачный брокер бинарных опционов')

        finish_datetime = datetime.datetime.now() + datetime.timedelta(minutes=deal_time)

        self.click_option(option)
        repeater(self.try_set_field)('investment_money', summ, use_mouse=True)
        repeater(self.set_expiration_time)(finish_datetime)

        pyautogui.click(self.prognosis_table[prognosis].x, self.prognosis_table[prognosis].y, duration=0.1)
        self.is_deal = True

        finish_datetime = datetime.datetime.now() + datetime.timedelta(minutes=self.interval_deal_time)
        self.scheduler.add_job(self._get_deal_result, 'date', run_date=finish_datetime)
