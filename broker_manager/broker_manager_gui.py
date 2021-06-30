import datetime
import json
import logging
import os.path

import pyautogui
import pyperclip
import time

import geometry_2d
import windows_manager
from broker_manager.broker_manager_interface import BrokerManagerInterface

logger = logging.getLogger('pyFinance')


class BrokerManagerGui(BrokerManagerInterface):
    TRY_COUNT = 5

    def __init__(self, config_file):
        with open(os.path.join(os.path.dirname(__file__), config_file), 'r') as cf:
            self.config = json.load(cf)

        self.option_buttons = dict(zip(
            BrokerManagerInterface.OPTION_LIST,
            geometry_2d.get_matrix(
                m_size={'x': 11, 'y': 2},
                start=self.config['buttons']['option']['first'],
                delta=self.config['buttons']['option']['delta']
            )
        ))
        self.option_buttons['CADCHF'] = self.option_buttons['CADJPY']

        self.prognosis_table = dict(zip(
            BrokerManagerInterface.PROGNOSIS_LIST,
            [
                self.config['buttons']['prognosis']['call'],
                self.config['buttons']['prognosis']['put']
            ]
        ))

        self.current_option = None
        try:
            windows_manager.activate_window('Прозрачный брокер бинарных опционов')
            self.__select_option('EURUSD')
        except RuntimeError:
            pass

    def __set_field(self, field, value):
        pyautogui.doubleClick(**self.config['fields'][field], duration=0.1)
        time.sleep(0.5)
        pyautogui.write(str(value), interval=0.25)
        time.sleep(0.5)

    def __get_field(self, field, use_mouse=False):
        pyperclip.copy("")  # <- Это предотвращает замену последней копии текущей копией null.

        pyautogui.doubleClick(**self.config['fields'][field], duration=0.1)
        time.sleep(0.5)

        if use_mouse:
            pyautogui.rightClick(**self.config['fields'][field], duration=0.1)
            time.sleep(0.5)
            pyautogui.moveRel(**self.config['context_menu']['copy'], duration=0.1)
            pyautogui.leftClick()
        else:
            # ctrl-c обычно работает очень быстро, но ваша программа может выполняться быстрее
            pyautogui.hotkey('ctrl', 'c')

        time.sleep(0.5)
        return pyperclip.paste()

    def __select_option(self, option):
        if self.current_option == option:
            return True

        screenshot_region = (
            self.option_buttons[option]['x'] - 5,
            self.option_buttons[option]['y'] - 5,
            self.option_buttons[option]['x'] + 5,
            self.option_buttons[option]['y'] + 5
        )

        screenshot_1 = pyautogui.screenshot(region=screenshot_region)
        for k in range(BrokerManagerGui.TRY_COUNT):
            pyautogui.leftClick(**self.option_buttons[option], duration=0.1)
            time.sleep(3)

            screenshot_2 = pyautogui.screenshot(region=screenshot_region)
            if screenshot_1 != screenshot_2:
                logger.debug('Select option {}: SUCCESS'.format(option))
                self.current_option = option
                return True

            logger.debug('Select option {} attempt №{}: FAIL'.format(k, option))

        raise RuntimeError('Can not select option {}'.format(option))

    def get_deal_result(self):
        windows_manager.activate_window('Прозрачный брокер бинарных опционов')
        pyautogui.doubleClick(**self.config['buttons']['opened'], duration=0.1)
        time.sleep(5)

        result = ''
        for k in range(BrokerManagerGui.TRY_COUNT):
            result = self.__get_field('result')
            if result in ['LOSE', 'WIN']:
                break
            time.sleep(5)

        # If result not in ['LOSE', 'WIN'] return as is
        return result

    def make_deal(self, option, prognosis, summ, finish_time):
        windows_manager.activate_window('Прозрачный брокер бинарных опционов')
        self.__select_option(option)
        time.sleep(2)

        real_summ = None
        for k in range(self.TRY_COUNT):
            self.__set_field('investment_money', summ)
            real_summ = self.__get_field('investment_money')
            if real_summ == summ:
                break

        if real_summ != summ:
            raise RuntimeError('Error setting up summ')

        interval = None
        real_interval = None
        for k in range(self.TRY_COUNT):
            interval = int((finish_time - datetime.datetime.now()).total_seconds / 60)
            self.__set_field('expiration_time', interval)
            real_interval = self.__get_field('expiration_time')
            if real_interval == interval:
                break

        if real_interval != interval:
            raise RuntimeError('Error setting up expiration time interval')

        time.sleep(2)
        pyautogui.click(**self.prognosis_table[prognosis], duration=0.1)
        real_finish_time = datetime.datetime.now() + datetime.timedelta(minutes=interval)
        return real_finish_time
