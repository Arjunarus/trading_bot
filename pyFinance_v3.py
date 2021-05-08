from telethon import TelegramClient, sync, events
import datetime
import pyautogui
import time
import re
import pyperclip
import pytz

currentMouseX, currentMouseY = pyautogui.position()# Получаем XY координаты курсора
print(currentMouseX, currentMouseY)
#pyautogui.moveTo(1000, 500, duration=2)

expiration_hour = ((585, 219), (626, 219), (665, 219), (704, 219), (743, 219), (782, 219),
                   (585, 246), (626, 246), (665, 246), (704, 246), (743, 246), (782, 246),
                   (585, 274), (626, 274), (665, 274), (704, 274), (743, 274), (782, 274),
                   (585, 300), (626, 300), (665, 300), (704, 300), (743, 300), (782, 300))

expiration_minute = ((831, 219), (870, 219), (908, 219),
                     (831, 246), (870, 246), (908, 246),
                     (831, 274), (870, 274), (908, 274),
                     (831, 300), (870, 300), (908, 300))

options_xy = ((164, 146), (164, 170), (220, 146), (220, 170), (274, 146), (274, 170), (328, 146),
              (328, 170), (381, 146), (381, 170), (436, 146), (436, 170), (490, 146), (490, 170),
              (543, 146), (543, 170), (598, 146), (598, 170), (652, 146), (652, 170), (708, 146))

options = ('AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADJPY', 'EURAUD',
           'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'GBPAUD', 'GBPCHF',
           'GBPJPY', 'GBPNZD', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY')

prognosis = ('Вверх', 'Вниз')
prognosis_up = (824, 351)
prognosis_down = (944, 351)
investment_money = (851, 156)
expiration_time = (911, 156)
summ_step = {1: 50, 2: 100, 3: 250, 4: 550, 5: 1200, 6: 2500, 7: 5200}
win_lose_xy = (983, 457)
#win_lose_xy = (429, 576)

# Вставляем api_id и api_hash
api_id = <INSERT_API_ID>
api_hash = <INSERT_API_HASH>

client = TelegramClient(<INSERT_NUMBER>, api_id, api_hash)

now = datetime.datetime.now()
f = open(now.strftime('%Y-%m-%d') + '.txt', 'a')

step = 1
summ = '50'

#now_time = datetime.datetime.utcnow()
#print(now_time.strftime('%H:%M'))
#moscow_time = datetime.datetime.now(pytz.timezone('Europe/Moscow'))
#print(moscow_time.strftime('%H:%M'))
#date_data = datetime.datetime(2021, 4, 5, 10, 53)
#print(date_data)
#period = date_data - now_time
#print("{} дней  {} секунд   {} микросекунд".format(period.days, period.seconds, period.microseconds))
#print("Всего: {} секунд".format(period.total_seconds()))

def copy_clipboard(): # копирует в буфер результат сделки
    pyperclip.copy("") # <- Это предотвращает замену последней копии текущей копией null.
    pyautogui.doubleClick(win_lose_xy[0], win_lose_xy[1])
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(1)  # ctrl-c обычно работает очень быстро, но ваша программа может выполняться быстрее
    return pyperclip.paste()

@client.on(events.NewMessage(chats=('Scrooge Club'))) #создает событие, срабатывающее при появлении нового сообщения
async def normal_handler(event):
    global summ
    global step
    user_mess = event.message.to_dict()['message']# текст и сообщения
    mess_date = event.message.to_dict()['date']# дата сообщения
    try:
        mess_list = user_mess.split()# разбиваем строку(сообщение) на слова
        if (mess_list[0] in options) and (mess_list[1] in prognosis): # если в сообщении есть валютная пара и прогноз, то считаем это сигналом
            f.write(mess_date.strftime('%d-%m-%Y %H:%M') + "\n")
            f.write(mess_list[0]+"\n")
            f.write(mess_list[1] + "\n")
            f.write(mess_list[3] + "\n")
            f.write(summ + "\n")
            f.flush()
            time_str = mess_list[3].split('.') # разбиваем время из сигнала на часы и минуты
            time_hour = int(time_str[0]) # получаем часы
            time_minute = int(time_str[1]) # получаем минуты
            j = 0
            while j < len(options): # ищем валютную пару, которая в сигнале
                if mess_list[0] == options[j]:
                    pyautogui.click(options_xy[j][0], options_xy[j][1], duration=0.1)
                    time.sleep(2)
                    break
                j += 1
            pyautogui.doubleClick(investment_money[0], investment_money[1], duration=0.1)
            time.sleep(2)
            pyautogui.write(summ, interval=0.25)
            time.sleep(2)
            pyautogui.click(expiration_time[0], expiration_time[1], duration=0.1)
            time.sleep(2)
            pyautogui.click(expiration_hour[time_hour][0], expiration_hour[time_hour][1], duration=0.1)
            time.sleep(2)
            pyautogui.click(expiration_minute[time_minute//5][0], expiration_minute[time_minute//5][1], duration=0.1)
            time.sleep(2)
            if mess_list[1] == prognosis[0]: # ищем прогноз который в сигнале
                pyautogui.click(prognosis_up[0], prognosis_up[1], duration=0.1)
            elif mess_list[1] == prognosis[1]:
                pyautogui.click(prognosis_down[0], prognosis_down[1], duration=0.1)
            else:
                f.write('ошибка: прогноз не распознан' "\n")
                f.flush()
            now_time = datetime.datetime.utcnow()
            date_data = datetime.datetime(now_time.year, now_time.month, now_time.day, time_hour, time_minute)
            period = date_data - now_time
            f.write('now_time = ' + now_time.strftime('%Y-%m-%d %H:%M') + '\n')
            f.write('date_data = ' + date_data.strftime('%Y-%m-%d %H:%M') + '\n')
            f.write('period = ' + str(period.total_seconds()) + '\n')
            f.flush()
            time.sleep(period.total_seconds() - 10800) # ждем окончания сделки
            result = ''
            k = 0
            while k < 50:
                result = copy_clipboard()
                if result == 'LOSE':
                    summ = int(summ) * 2 + (int(summ) * 10 / 100)
                    summ = str(int(summ)) # делаем summ целым числом и потом строкой
                    f.write('result = ' + result + '\n\n')
                    f.flush()
                    break
                elif result == 'WIN':
                    summ = '50'
                    f.write('result = ' + result + '\n\n')
                    f.flush()
                    break
                time.sleep(5)
                k += 1
    except Exception as err:
        f.write(str(err) + "\n\n")
        f.flush()
        print('ошибка: ', err)

client.start()
print('клиент запущен, бот активен')
client.run_until_disconnected()
f.close()