from telethon import TelegramClient, events
import datetime
import logging
import os
import re
import sys
import traceback

import broker_manager_gui as broker_manager

SAVE_STATE_FILE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'session.sav')

# Initial values
step = 1
init_summ = 50
is_deal = False

# Prepare logger
logger = logging.getLogger('pyFinance')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(datetime.datetime.now().strftime('%Y-%m-%d.log'))
formatter = logging.Formatter('%(asctime)s %(message)s')
fh.setFormatter(formatter)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(fh)
logger.addHandler(ch)

# Prepare telethon logger
telethon_logger = logging.getLogger('telethon')
tfh = logging.FileHandler(datetime.datetime.now().strftime('%Y-%m-%d_telethon.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
tfh.setFormatter(formatter)
telethon_logger.setLevel(logging.DEBUG)
telethon_logger.addHandler(tfh)


def get_summ(st):
    return int(init_summ * (2.2 ** (st - 1)))


def parse_signal(signal_text):
    signal_lines = signal_text.split('\n')
    if len(signal_lines) < 2:
        # Ожидаем как минимум 2 строки, иначе это не сигнал
        return None

    option = signal_lines[0][:6]
    if option not in broker_manager.OPTION_LIST:
        logger.info('Unknown option: {}. Skip.'.format(option))
        return None
    
    pattern = r'(вверх|вниз)до(\d{2}.\d{2})мск'
    m = re.match(pattern, signal_lines[1].replace(' ', '').lower())
    if m is None:
        return

    prognosis = m.group(1)
    deal_time_str = m.group(2)
    deal_time = datetime.datetime.strptime(deal_time_str, '%H.%M').time()
    return option, prognosis, deal_time


def deal_result_process(result):
    global step
    global is_deal

    logger.info('Got result: %s', result)
    if result == 'LOSE':
        step += 1
    elif result == 'WIN':
        step = 1
    else:
        raise ValueError('Unknown result: {}'.format(result))

    is_deal = False


def message_process(user_mess, mess_date):
    global step
    global is_deal

    logger.info('\nGot message: %s', user_mess)
    logger.info(mess_date.strftime('Message date: %d-%m-%Y %H:%M'))
    if is_deal:
        logger.info('Deal is active now, skip message.')
        return

    try:
        signal = parse_signal(user_mess)
        if signal is None:
            logger.info('Message is not a signal, skip.')
            return

        option, prognosis, deal_time = signal

        logger.info('Получен сигнал: {opt} {prog} до {tm}'.format(
            opt=option,
            prog=prognosis,
            tm=deal_time.strftime('%H.%M')
        ))

        summ = get_summ(step)
        logger.info('Сумма: {}'.format(summ))

        broker_manager.make_deal(option, prognosis, summ, deal_time, deal_result_process)
        is_deal = True

    except Exception as err:
        logger.error("Ошибка: {}\n".format(err))
        traceback.print_exc(file=sys.stdout)


def save_state(save_file_path):
    global step
    global init_summ
    with open(save_file_path, 'w') as sav:
        sav.write("{} {}".format(step, init_summ))

    logger.debug("Saved to {}".format(save_file_path))


def load_state(save_file_path):
    global step
    global init_summ

    if not os.path.isfile(save_file_path):
        logger.error("Save state {} is not exists".format(save_file_path))
        return

    with open(save_file_path, 'r') as sav:
        content = sav.read()
    step, init_summ = map(int, content.split())

    logger.debug("Loaded from {}".format(save_file_path))
    logger.debug('step = {}'.format(step))
    logger.debug('init_summ = {}'.format(init_summ))


def main():
    # Proper number, api_id and api_hash from command line
    number, api_id, api_hash = sys.argv[1:]
    client = TelegramClient(number, api_id, api_hash)

    @client.on(events.NewMessage(chats='Scrooge Club'))  # создает событие, срабатывающее при появлении нового сообщения
    async def normal_handler(event):
        message = event.message.to_dict()
        message_process(message['message'], message['date'])

    load_state(SAVE_STATE_FILE_PATH)
    client.start()
    logger.info('Клиент запущен, бот активен.')
    try:
        client.run_until_disconnected()
    except:
        pass
    save_state(SAVE_STATE_FILE_PATH)


if __name__ == '__main__':
    main()
