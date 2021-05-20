import datetime
import logging
import pyautogui
import pyperclip
import pytz
import time

import windows_manager
from broker_manager_interface import BrokerManagerInterface
import broker_manager_gui_nick_config as config


logger = logging.getLogger('pyFinance')


class Vector2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def get_matrix(m_size, start, delta):
    if type(m_size) is not Vector2D:
        raise ValueError('m_size is not a 2d vector.')
    if type(start) is not Vector2D:
        raise ValueError('start is not a 2d vector.')
    if type(delta) is not Vector2D:
        raise ValueError('delta is not a 2d vector.')

    return [Vector2D(start.x + delta.x * i, start.y + delta.y * j) for j in range(m_size.x) for i in range(m_size.y)]


class BrokerManagerGui(BrokerManagerInterface):
    EXP_HOUR_BUTTONS = get_matrix(
        m_size=Vector2D(6, 4),
        start=Vector2D(config.EXP_HOUR_FIRST_X, config.EXP_HOUR_FIRST_Y),
        delta=Vector2D(config.TIME_BUTTON_DELTA_X, config.TIME_BUTTON_DELTA_Y)
    )

    EXP_MINUTE_BUTTONS = get_matrix(
        m_size=Vector2D(3, 4),
        start=Vector2D(config.EXP_MINUTE_FIRST_X, config.EXP_MINUTE_FIRST_Y),
        delta=Vector2D(config.TIME_BUTTON_DELTA_X, config.TIME_BUTTON_DELTA_Y)
    )

    OPTION_BUTTONS = dict(zip(
        BrokerManagerInterface.OPTION_LIST,
        get_matrix(
            m_size=Vector2D(11, 2),
            start=Vector2D(config.OPTION_FIRST_X, config.OPTION_FIRST_Y),
            delta=Vector2D(config.OPTION_DELTA_X, config.OPTION_DELTA_Y)
        )
    ))

    PROGNOSIS_TABLE = dict(zip(BrokerManagerInterface.PROGNOSIS_LIST, [config.PROGNOSIS_UP_XY, config.PROGNOSIS_DOWN_XY]))
    TRY_COUNT = 3

    def _get_deal_result(self):
        self.is_deal = False

        result = ''
        windows_manager.activate_window('Прозрачный брокер бинарных опционов')
        for k in range(BrokerManagerGui.TRY_COUNT):
            pyperclip.copy("")  # <- Это предотвращает замену последней копии текущей копией null.
            pyautogui.doubleClick(config.WIN_LOSE_XY[0], config.WIN_LOSE_XY[1])
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
        pyautogui.click(BrokerManagerGui.OPTION_BUTTONS[option].x, BrokerManagerGui.OPTION_BUTTONS[option].y, duration=0.1)
        time.sleep(2)

        for k in range(BrokerManagerGui.TRY_COUNT):
            pyautogui.doubleClick(config.INVESTMENT_MONEY[0], config.INVESTMENT_MONEY[1], duration=0.1)
            time.sleep(1)
            pyautogui.write(str(summ), interval=0.25)
            time.sleep(1)

        pyautogui.click(config.EXPIRATION_TIME[0], config.EXPIRATION_TIME[1], duration=0.1)
        time.sleep(2)
        pyautogui.click(BrokerManagerGui.EXP_HOUR_BUTTONS[deal_time.hour].x, BrokerManagerGui.EXP_HOUR_BUTTONS[deal_time.hour].y, duration=0.1)
        time.sleep(2)
        pyautogui.click(BrokerManagerGui.EXP_MINUTE_BUTTONS[deal_time.minute // 5].x, BrokerManagerGui.EXP_MINUTE_BUTTONS[deal_time.minute // 5].y, duration=0.1)
        time.sleep(2)
        pyautogui.click(BrokerManagerGui.PROGNOSIS_TABLE[prognosis][0], BrokerManagerGui.PROGNOSIS_TABLE[prognosis][1], duration=0.1)
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

        self.scheduler.add_job(self._get_deal_result, 'date', run_date=finish_datetime, args=[self])
