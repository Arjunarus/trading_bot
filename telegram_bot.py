from telethon import TelegramClient, sync, events
import datetime
import pyautogui
import re
import time

#currentMouseX, currentMouseY = pyautogui.position()# Получаем XY координаты курсора
#print(currentMouseX, currentMouseY)
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

step = 0
summ = '50'

step_summ = {
    2: 100,
    3: 250,
    4: 550,
    5: 1200,
    6: 2500,
    7: 5200
}

def processor(user_mess, mess_date):
    global summ
    global step
    
    result = ''
    try:
        mess_list = user_mess.split()  # разбиваем строку(сообщение) на слова
        if (mess_list[0] in options) and (mess_list[1] in prognosis):
            i = 0
            while i < len(mess_list):
                result += mess_date.strftime('%d-%m-%Y %H:%M') + "\n"
                result += mess_list[i] + "\n"
                result += mess_list[i+1] + "\n"
                result += mess_list[i+3] + "\n\n"
                
                time_str = mess_list[i+3].split('.')  # разбиваем время из сигнала на часы и минуты
                time_hour = int(time_str[0])  # получаем часы
                time_minute = int(time_str[1])  # получаем минуты
                j = 0
                while j < len(options):
                    if mess_list[i] == options[j]:
                        print(mess_list[i])
                        time.sleep(2)
                        pyautogui.click(options_xy[j][0], options_xy[j][1], duration=0.1)
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
                r = 0
                t = 0
                while r != time_minute:
                    r += 5
                    t += 1
                else:
                    pyautogui.click(expiration_minute[t][0], expiration_minute[t][1], duration=0.1)
                time.sleep(2)
                if mess_list[i+1] == prognosis[0]:
                    pyautogui.click(prognosis_up[0], prognosis_up[1], duration=0.1)
                elif mess_list[i+1] == prognosis[1]:
                    pyautogui.click(prognosis_down[0], prognosis_down[1], duration=0.1)
                else:
                    result += 'ошибка: прогноз не распознан' "\n"
                i += 5
                summ = '50'
        else:
            message = user_mess.replace('\n', ' ')
            pattern = r'.*\( *([0-9]*) колен.* *\).*'
            matching = re.match(pattern, message)
            if matching is not None:
                step = int(matchin.group(1))
                summ = step_summ[step]
    except Exception as err:
        result += str(err)
        print('ошибка ', err)
   
    return result

def main():
    # Вставляем api_id и api_hash
    api_id = <INSERT_API_ID>
    api_hash = <INSERT_API_HASH>
    client = TelegramClient(<INSERT_NUMBER>, api_id, api_hash)
    
    @client.on(events.NewMessage(chats='Scrooge Club'))  # создает событие, срабатывающее при появлении нового сообщения
    async def normal_handler(event):
        user_mess = event.message.to_dict()['message']  # текст и сообщения
        mess_date = event.message.to_dict()['date']  # дата сообщения
        log = processor(user_mess, mess_date)
        f.write(log)
        f.flush()
    
    now = datetime.datetime.now()
    f = open(now.strftime('%Y-%m-%d') + '.txt', 'a')
    client.start()
    print('клиент запущен, бот активен')
    client.run_until_disconnected()
    f.close()
    

if __name__ == '__main__':
    main()