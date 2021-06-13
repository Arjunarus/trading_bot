import datetime
import json
import logging
import pyautogui
import pyperclip
import pytz
import time
import geometry_2d
import windows_manager
import errors
from broker_manager_interface import BrokerManagerInterface


logger = logging.getLogger('pyFinance')


class BrokerManagerGui(BrokerManagerInterface):
    TRY_COUNT = 5

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
            result = self.get_field(self.config['fields']['result'])
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

    def click_option(self, option):
        screenshot_1 = pyautogui.screenshot(region=(option.x - 5, option.y - 5, option.x + 5, option.y + 5))
        for k in range(BrokerManagerGui.TRY_COUNT):
            pyautogui.click(option.x, option.y, duration=0.1)
            time.sleep(3)
            screenshot_2 = pyautogui.screenshot(region=(option.x - 5, option.y - 5, option.x + 5, option.y + 5))
            if screenshot_1 != screenshot_2:
                logger.debug('Check option button - True')
                return True
            logger.debug('Check option button attempt №{} - False'.format(k))
        return False

    def make_deal(self, option, prognosis, summ, deal_time):
        if self.is_deal:
            logger.info('Deal is active now, skip new deal.\n')
            return

        windows_manager.activate_window('Прозрачный брокер бинарных опционов')
        if not self.click_option(self.option_buttons[option]):
            raise errors.ClickoptionError('invalid option selection')

        for k in range(BrokerManagerGui.TRY_COUNT):
            self.set_field('investment_money', summ)
            if self.get_field('investment_money', use_mouse=True) == str(summ):
                logger.debug('Check deal summ - True')
                break
            logger.debug('Check deal summ attempt №{} - False'.format(k))
            # при всех неудачных попытках ничего не делаем
            if k == (BrokerManagerGui.TRY_COUNT - 1):
                raise errors.ValueSummError('invalid summ input')

        for k in range(BrokerManagerGui.TRY_COUNT):
            self.set_field('expiration_time', deal_time)
            if self.get_field('expiration_time') == str(deal_time):
                logger.debug('Check deal time - True')
                break
            logger.debug('Check deal time attempt №{} - False'.format(k))
            # при всех неудачных попытках ничего не делаем
            if k == (BrokerManagerGui.TRY_COUNT - 1):
                raise errors.ValueTimeError('invalid time input')

        pyautogui.click(self.prognosis_table[prognosis].x, self.prognosis_table[prognosis].y, duration=0.1)
        self.is_deal = True

        finish_datetime = datetime.datetime.now() + datetime.timedelta(minutes=deal_time)
        self.scheduler.add_job(self._get_deal_result, 'date', run_date=finish_datetime)
