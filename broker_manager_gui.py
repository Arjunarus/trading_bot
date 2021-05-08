import datetime
import pygetwindow as gw
import pyautogui
import pyperclip
import pytz
import time

import broker_manager_gui_luzin_config as config

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

def __activate_broker_window():
    name = 'Прозрачный брокер бинарных опционов'
    broker_window_list = gw.getWindowsWithTitle(name)
    if len(broker_window_list) == 0:
        raise RuntimeError('Window "{}" is not found'.format(name))
    broker_window = broker_window_list[0]
    broker_window.activate()
    

def __wait_for_time(time_to_wait):
    msk_tz = pytz.timezone('Europe/Moscow')
    now_hour = datetime.datetime.now(msk_tz).hour
    while now_hour != time_to_wait.hour:
        time.sleep(5)
        now_hour = datetime.datetime.now(msk_tz).hour

    now_minute = datetime.datetime.now(msk_tz).minute
    while now_minute < time_to_wait.minute:
        time.sleep(5)
        now_minute = datetime.datetime.now(msk_tz).minute


def get_deal_result(deal_time):  # возвращает результат сделки
    result = ''
    __wait_for_time(deal_time)

    __activate_broker_window()
    for k in range(50):
        pyperclip.copy("")  # <- Это предотвращает замену последней копии текущей копией null.
        pyautogui.doubleClick(config.WIN_LOSE_XY[0], config.WIN_LOSE_XY[1])
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(1)  # ctrl-c обычно работает очень быстро, но ваша программа может выполняться быстрее
        result = pyperclip.paste()
        if result in ['LOSE', 'WIN']:
            break
        time.sleep(5)
    return result


def make_deal(option, prognosis, summ, deal_time):
    __activate_broker_window()
    pyautogui.click(OPTION_TABLE[option][0], OPTION_TABLE[option][1], duration=0.1)
    time.sleep(2)
    pyautogui.doubleClick(config.INVESTMENT_MONEY[0], config.INVESTMENT_MONEY[1], duration=0.1)
    time.sleep(2)
    pyautogui.write(str(summ), interval=0.25)
    time.sleep(2)
    pyautogui.click(config.EXPIRATION_TIME[0], config.EXPIRATION_TIME[1], duration=0.1)
    time.sleep(2)
    pyautogui.click(EXPIRATION_HOUR[deal_time.hour][0], EXPIRATION_HOUR[deal_time.hour][1], duration=0.1)
    time.sleep(2)
    pyautogui.click(EXPIRATION_MINUTE[deal_time.minute // 5][0], EXPIRATION_MINUTE[deal_time.minute // 5][1], duration=0.1)
    time.sleep(2)
    pyautogui.click(PROGNOSIS_TABLE[prognosis][0], PROGNOSIS_TABLE[prognosis][1], duration=0.1)
