import datetime
import logging
import platform
if platform.system() == 'Windows':
    import pygetwindow as gw
else:
    # Workaround for linux system where pygetwindow does not work
    class gw:
        def getWindowsWithTitle(self, _):
            return []

import pyautogui
import pyperclip
import pytz
import time
from apscheduler.schedulers.background import BackgroundScheduler

import broker_manager_gui_nick_config as config


logger = logging.getLogger('pyFinance')
TRY_COUNT = 3


class Vector2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def __get_matrix(m_size, start, delta):
    if type(m_size) is not Vector2D:
        raise ValueError('m_size is not a 2d vector.')
    if type(start) is not Vector2D:
        raise ValueError('start is not a 2d vector.')
    if type(delta) is not Vector2D:
        raise ValueError('delta is not a 2d vector.')

    return [Vector2D(start.x + delta.x * i, start.y + delta.y * j) for j in range(m_size.x) for i in range(m_size.y)]


EXP_HOUR_BUTTONS = __get_matrix(
    m_size=Vector2D(6, 4),
    start=Vector2D(config.EXP_HOUR_FIRST_X, config.EXP_HOUR_FIRST_Y),
    delta=Vector2D(config.TIME_BUTTON_DELTA_X, config.TIME_BUTTON_DELTA_Y)
)

EXP_MINUTE_BUTTONS = __get_matrix(
    m_size=Vector2D(3, 4),
    start=Vector2D(config.EXP_MINUTE_FIRST_X, config.EXP_MINUTE_FIRST_Y),
    delta=Vector2D(config.TIME_BUTTON_DELTA_X, config.TIME_BUTTON_DELTA_Y)
)

OPTION_LIST = (
    'AUDCAD', 'AUDJPY', 'AUDUSD', 'EURAUD', 'EURCHF', 'EURJPY', 'GBPAUD', 'GBPJPY', 'NZDJPY', 'USDCAD', 'USDJPY'
    'AUDCHF', 'AUDNZD', 'CADJPY', 'EURCAD', 'EURGBP', 'EURUSD', 'GBPCHF', 'GBPNZD', 'NZDUSD', 'USDCHF'
)

OPTION_BUTTONS = dict(zip(
    OPTION_LIST,
    __get_matrix(
        m_size=Vector2D(11, 2),
        start=Vector2D(config.OPTION_FIRST_X, config.OPTION_FIRST_Y),
        delta=Vector2D(config.OPTION_DELTA_X, config.OPTION_DELTA_Y)
    )
))

PROGNOSIS_LIST = ('вверх', 'вниз')
PROGNOSIS_TABLE = dict(zip(PROGNOSIS_LIST, [config.PROGNOSIS_UP_XY, config.PROGNOSIS_DOWN_XY]))


shed = BackgroundScheduler()
shed.start()


def __activate_broker_window():
    if platform.system() != 'Windows':
        # Does not work on linux
        return

    name = 'Прозрачный брокер бинарных опционов'
    broker_window_list = gw.getWindowsWithTitle(name)
    if len(broker_window_list) == 0:
        raise RuntimeError('Window "{}" is not found'.format(name))
    broker_window = broker_window_list[0]
    broker_window.activate()


def get_deal_result(result_handler):  # возвращает результат сделки
    result = ''
    __activate_broker_window()
    for k in range(TRY_COUNT):
        pyperclip.copy("")  # <- Это предотвращает замену последней копии текущей копией null.
        pyautogui.doubleClick(config.WIN_LOSE_XY[0], config.WIN_LOSE_XY[1])
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(1)  # ctrl-c обычно работает очень быстро, но ваша программа может выполняться быстрее
        result = pyperclip.paste()
        if result in ['LOSE', 'WIN']:
            break
        time.sleep(5)

    # If result not in ['LOSE', 'WIN'] return as is
    result_handler(result)


def __get_summ():
    # Does not work
    pyperclip.copy("")
    pyautogui.doubleClick(config.INVESTMENT_MONEY[0], config.INVESTMENT_MONEY[1], duration=0.1)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(1)
    try:
        res = int(pyperclip.paste())
    except Exception:
        res = None
    return res


def __set_summ(summ):
    pyautogui.doubleClick(config.INVESTMENT_MONEY[0], config.INVESTMENT_MONEY[1], duration=0.1)
    time.sleep(1)
    pyautogui.write(str(summ), interval=0.25)


def make_deal(option, prognosis, summ, deal_time, result_handler):
    __activate_broker_window()
    pyautogui.click(OPTION_BUTTONS[option].x, OPTION_BUTTONS[option].y, duration=0.1)
    time.sleep(2)

    for k in range(TRY_COUNT):
        __set_summ(summ)
        time.sleep(1)

    pyautogui.click(config.EXPIRATION_TIME[0], config.EXPIRATION_TIME[1], duration=0.1)
    time.sleep(2)
    pyautogui.click(EXP_HOUR_BUTTONS[deal_time.hour].x, EXP_HOUR_BUTTONS[deal_time.hour].y, duration=0.1)
    time.sleep(2)
    pyautogui.click(EXP_MINUTE_BUTTONS[deal_time.minute // 5].x, EXP_MINUTE_BUTTONS[deal_time.minute // 5].y, duration=0.1)
    time.sleep(2)
    pyautogui.click(PROGNOSIS_TABLE[prognosis][0], PROGNOSIS_TABLE[prognosis][1], duration=0.1)

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

    shed.add_job(get_deal_result, 'date', run_date=finish_datetime, args=[result_handler])
