from telethon import TelegramClient, events
import datetime
import logging
import os
import re
import sys
import traceback

from broker_manager_gui import BrokerManagerGui, BrokerManagerInterface

# Cоздание и сохранение пути файла session.sav
SAVE_STATE_FILE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'session.sav')

# Cоздание папки log
if not os.path.isdir("log"):
    os.mkdir("log")

# Initial values
step = 1
INIT_SUMM = 50
TIME_OFFSET = 1

# Prepare logger
logger = logging.getLogger('pyFinance')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler(os.path.join('log', datetime.datetime.now().strftime('%Y-%m-%d.log')), 'a', 'utf-8')
formatter = logging.Formatter('%(asctime)s %(message)s')
fh.setFormatter(formatter)
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

ch = logging.StreamHandler()
ch.setFormatter(formatter)
ch.setLevel(logging.INFO)
logger.addHandler(ch)

# Prepare telethon logger
telethon_logger = logging.getLogger('telethon')
tfh = logging.FileHandler(os.path.join('log', datetime.datetime.now().strftime('%Y-%m-%d_telethon.log')), 'a', 'utf-8')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
tfh.setFormatter(formatter)
telethon_logger.setLevel(logging.DEBUG)
telethon_logger.addHandler(tfh)


def save_state(save_file_path):
    global step
    global INIT_SUMM
    with open(save_file_path, 'w') as sav:
        sav.write("{} {}".format(step, INIT_SUMM))

    logger.debug("Saved to {}\n".format(save_file_path))


def load_state(save_file_path):
    global step
    global INIT_SUMM

    if not os.path.isfile(save_file_path):
        logger.error("Save state {} is not exists\n".format(save_file_path))
        return

    with open(save_file_path, 'r') as sav:
        content = sav.read()
    step, INIT_SUMM = map(int, content.split())

    logger.debug("Loaded from {}".format(save_file_path))
    logger.debug('step = {}'.format(step))
    logger.debug('init_summ = {}'.format(INIT_SUMM))


def get_summ(st):
    return int(INIT_SUMM * (2.3 ** (st - 1)))


def parse_signal(signal_text):
    signal_lines = signal_text.split('\n')
    print(signal_lines)
    if len(signal_lines) != 1:
        # Ожидаем 1 строку, иначе это не сигнал
        return None

    option = signal_lines[0][:6]
    if option not in BrokerManagerInterface.OPTION_LIST:
        # Если не нашли известный нам опцион, значит это не сигнал
        return None

    pattern = r'[\S\D]*(вверх|вниз)на(\d+)[\S\D]*'
    m = re.match(pattern, signal_lines[0].replace(' ', '').lower())
    if m is None:
        # Если строка не соответствует шаблону, значит это не сигнал
        return

    prognosis = m.group(1)
    deal_time_str = m.group(2)
    deal_time = int(deal_time_str)
    return option, prognosis, deal_time


def deal_result_process(result):
    global step

    logger.info('Got result: %s', result)
    if result == 'LOSE':
        step += 1
    elif result == 'WIN':
        step = 1
    else:
        step = 1
        logger.error('Unknown result: {}'.format(result))

    save_state(SAVE_STATE_FILE_PATH)


def message_process(message_text, message_date, broker_manager):
    global step

    logger.info('-------------------------------------------------------------------')
    logger.info('Got message')
    logger.debug(message_text)
    logger.info(message_date.strftime('Message date: %d-%m-%Y %H:%M'))

    try:
        signal = parse_signal(message_text)
        if signal is None:
            logger.info('Message is not a signal, skip.\n')
            return

        option, prognosis, deal_time = signal
        deal_time -= TIME_OFFSET

        logger.info('Получен сигнал: {opt} {prog} на {tm}'.format(
            opt=option,
            prog=prognosis,
            tm=deal_time
        ))

        summ = get_summ(step)
        logger.info('Сумма: {}'.format(summ))
        logger.info('Колено: {}'.format(step))

        broker_manager.make_deal(option, prognosis, summ, deal_time)

    except Exception as err:
        logger.error("Ошибка: {}\n".format(err))
        traceback.print_exc(file=sys.stdout)


def main():
    # Proper number, api_id and api_hash from command line
    number, api_id, api_hash, *rest = sys.argv[1:]
    if len(rest) > 0:
        config = rest[0]
    else:
        # Default value
        config = 'broker_manager_gui_nick_config.json'

    client = TelegramClient(number, api_id, api_hash)
    broker_manager = BrokerManagerGui(deal_result_process, config)

    # создает событие, срабатывающее при появлении нового сообщения
    @client.on(events.NewMessage(chats='🔊 СИГНАЛЫ №1 🔊'))
    async def normal_handler(event):
        message = event.message.to_dict()
        message_process(message['message'], message['date'], broker_manager)

    load_state(SAVE_STATE_FILE_PATH)
    client.start()
    logger.info('Клиент запущен, бот активен.\n')
    client.run_until_disconnected()


if __name__ == '__main__':
    main()
