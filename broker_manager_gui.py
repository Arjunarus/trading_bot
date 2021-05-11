import datetime
import logging
import platform
if platform.system() == 'Windows':
    import pygetwindow as gw
else:
    class gw:
        def getWindowsWithTitle(self, _):
            return []

import pyautogui
import pyperclip
import pytz
import time
from apscheduler.schedulers.background import BackgroundScheduler

import broker_manager_gui_luzin_config as config


logger = logging.getLogger('pyFinance')
TRY_COUNT = 3

currentMouseX, currentMouseY = pyautogui.position()  # Получаем XY координаты курсора
print(currentMouseX, currentMouseY)

EXPIRATION_HOUR = [
    (config.EXP_HOUR_FIRST_X + config.TIME_BUTTON_DELTA_X * i, config.EXP_HOUR_FIRST_Y + config.TIME_BUTTON_DELTA_Y * j)
    for j in range(4) for i in range(6)
]

EXPIRATION_MINUTE = [
    (config.EXP_MINUTE_FIRST_X + config.TIME_BUTTON_DELTA_X * i, config.EXP_MINUTE_FIRST_Y + config.TIME_BUTTON_DELTA_Y * j)
    for j in range(4) for i in range(3)
]

OPTION_LIST = (
    'AUDCAD', 'AUDCHF',
    'AUDJPY', 'AUDNZD',
    'AUDUSD', 'CADJPY',
    'EURAUD', 'EURCAD',
    'EURCHF', 'EURGBP',
    'EURJPY', 'EURUSD',
    'GBPAUD', 'GBPCHF',
    'GBPJPY', 'GBPNZD',
    'NZDJPY', 'NZDUSD',
    'USDCAD', 'USDCHF',
    'USDJPY', 'GBPUSD'
)

OPTION_TABLE = dict(zip(
    OPTION_LIST,
    [
        (config.OPTION_FIRST_X + config.OPTION_DELTA_X * i, config.OPTION_FIRST_Y + config.OPTION_DELTA_Y * j)
        for i in range(11) for j in range(2)
    ]
))
OPTION_TABLE['GBPUSD'] = OPTION_TABLE['EURUSD']

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

    if result not in ['LOSE', 'WIN']:
        raise ValueError('Incorrect result of deal: {}'.format(result))
    result_handler(result)


def __get_summ():
    # Does not work
    pyperclip.copy("")
    pyautogui.doubleClick(config.INVESTMENT_MONEY[0], config.INVESTMENT_MONEY[1], duration=0.1)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(1)
    try:
        res = int(pyperclip.paste())
    except:
        res = None
    return res


def __set_summ(summ):
    pyautogui.doubleClick(config.INVESTMENT_MONEY[0], config.INVESTMENT_MONEY[1], duration=0.1)
    time.sleep(1)
    pyautogui.write(str(summ), interval=0.25)


def make_deal(option, prognosis, summ, deal_time, result_handler):
    __activate_broker_window()
    pyautogui.click(OPTION_TABLE[option][0], OPTION_TABLE[option][1], duration=0.1)
    time.sleep(2)

    c_summ = 0
    for k in range(TRY_COUNT):
        __set_summ(summ)
        time.sleep(1)
        # c_summ = __get_summ()
        # time.sleep(2)
        # if c_summ == summ:
            # break

    # if c_summ != summ:
        # raise RuntimeError('Can not set up summ for deal, c_summ={}'.format(c_summ))

    pyautogui.click(config.EXPIRATION_TIME[0], config.EXPIRATION_TIME[1], duration=0.1)
    time.sleep(2)
    pyautogui.click(EXPIRATION_HOUR[deal_time.hour][0], EXPIRATION_HOUR[deal_time.hour][1], duration=0.1)
    time.sleep(2)
    pyautogui.click(EXPIRATION_MINUTE[deal_time.minute // 5][0], EXPIRATION_MINUTE[deal_time.minute // 5][1], duration=0.1)
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
